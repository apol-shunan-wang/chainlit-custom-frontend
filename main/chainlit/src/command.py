import os
import sys
import uuid
import json
import random
import itertools
from datetime import datetime
from collections import namedtuple

import chainlit as cl

from socketio.exceptions import TimeoutError

import plotly.graph_objects as go

from templates import PROMPT_TEMPLATES, CYPHER_TEMPLATES
from api.client import ApiClientHandler
from datalayer import Neo4jDriver

# GET azure client
api_client = ApiClientHandler("dev")

# SET UP Neo4j
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
neo4j_driver = Neo4jDriver(URI, AUTH)

async def handle_command(user_message: cl.Message):
    # TODO 評価コードをEvaluatorクラスに抽象化する
    # TODO バッチ評価のモジュール化
    message_history = cl.user_session.get("message_history")

    if user_message.content == "/eval":
        await cl.Message(
            content = "評価を出力します。このメッセージと直前のあなたの投稿はデータベースに記録されません。",
            author = "template",
        ).send()

        # single-hop skill evaluate
        single_evaluate_message = cl.Message(content="### 1-hop skill evaluate\n", author="gpt-4-32k")
        await single_evaluate_message.send()

        single_hop_skill_instruction = '以上のやり取りから、{topic}というテーマにおける{interviewee}の能力のレベルの評価の得点を1, 0, -1で評価してください。1は期待されるものよりも優れた回答であること、0は期待通りの回答であること、-1は期待されるものよりも不足した回答であることを意味します。\n結果は以下のフォーマットの python dict で出力してください。。\n# フォーマット\n{{"score": 得点, "reason": 簡単な理由}}'.format(
            topic = cl.user_session.get("topic"),
            interviewee = cl.user_session.get("user").identifier,
        )

        messages =  [{
            "role": msg_log.role,
            "content": msg_log.content.format(
                interviewee = cl.user_session.get("user").identifier,
            )
        } for msg_log in message_history[0:1]] + [{
            "role": msg_log.role,
            "content": msg_log.content,
        } for msg_log in message_history[-3:-1]] + [{
            "role": "user",
            "content": single_hop_skill_instruction,
        }]
        # print(messages)

        res = api_client.api.chat.completions.create(
            model = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"),
            temperature = 0.0,
            messages = messages,
        )
        
        content = random.choice(res.choices).message.content

        single_evaluate_message.content += content

        try:
            # print(type(res))
            # print(res)
            res_json = json.loads(content)
            score = res_json["score"]
            reason = res_json["reason"]
        except KeyError as e:
            raise e
        except Exception as e:
            raise e

        singleEvaluateMessageLog = MessageLog(
            message_id = str(uuid.uuid4()),
            timestamp = datetime.now().isoformat(),
            role = "assistant",
            author = single_evaluate_message.author,
            topic = None,
            content = single_evaluate_message.content,
            ifSend = True,
            ifSaveToLog = True,
            ifAddToMessages = False,
        )
        await single_evaluate_message.update()
        await neo4j_driver.execute_cypher(
            cypher = CYPHER_TEMPLATES["Evaluation_EVAL_Message"],
            message_id = message_history[-2].message_id,
            evaluation_id = singleEvaluateMessageLog.message_id,
            timestamp = singleEvaluateMessageLog.timestamp,
            author = singleEvaluateMessageLog.author,
            hopnumber = 1,
            instruction = single_hop_skill_instruction,
            content = singleEvaluateMessageLog.content,
            evaluation_type = "single_hop_skill_eval",
            score = score,
            reason = reason,
            ifSend = singleEvaluateMessageLog.ifSend,
            ifSaveToLog = singleEvaluateMessageLog.ifSaveToLog,
            ifAddToMessages = singleEvaluateMessageLog.ifAddToMessages,
        )

        # single-hop communication evaluate
        single_evaluate_message = cl.Message(content="### 1-hop communication evaluate\n", author="gpt-4-32k")
        await single_evaluate_message.send()

        # 減点方式でいいのでは?
        single_hop_communication_instruction = '以上の質問と回答から、評価基準に沿ってステップバイステップで推論し、0または-1の得点で評価してください。0はすべての基準で問題がないことを意味し、-1はいずれかの基準で問題があることを意味します。結果は以下のフォーマットの python dict で出力してください。\n\
        # 評価基準\n\
        1. 最後の質問に対する回答は、必要かつ十分であるか？\n\
        2. 専門用語を使いすぎていないか？\n\
        3. 一連の回答に矛盾はあるか？\n\
        4. 受け答えの内容は飛躍なく、一貫しているか？\n\
        # フォーマット\n{{"score": 評価, "reason": 理由}}\n\
        '.format(
            topic = cl.user_session.get("topic"),
            interviewee = cl.user_session.get("user").identifier,
        )

        messages =  [{
            "role": msg_log.role,
            "content": msg_log.content.format(
                interviewee = cl.user_session.get("user").identifier,
                interviewee_info = cl.user_session.get(cl.user_session.get("qa")),
            )
        } for msg_log in message_history[:-1]] + [{
            "role": "user",
            "content": single_hop_communication_instruction,
        }]
        # print(messages)

        res = api_client.api.chat.completions.create(
            model = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"),
            temperature = 0.0,
            messages = messages,
        )
        content = random.choice(res.choices).message.content

        single_evaluate_message.content += content

        # contentのパース
        # JSONは出力させるが、安全にやるためにはこのパース部分で工夫が必要
        # 例えば、exceptionが出たら、contentをoutput形式のダメな例として追加して
        # もう一度クエリするループ（コスト的な安全のためにループ回数制限をかける必要はある）など
        try:
            # print(res)
            res_json = json.loads(content)
            score = res_json["score"]
            reason = res_json["reason"]
        except KeyError:
            try:
                score = sum([v["score"] for v in res_json.values()])
                reason = "\n".join([v["reason"] for v in res_json.values()])
            except KeyError as e:
                raise e
        except Exception as e:
            raise e

        singleEvaluateMessageLog = MessageLog(
            message_id = str(uuid.uuid4()),
            timestamp = datetime.now().isoformat(),
            role = "assistant",
            author = single_evaluate_message.author,
            topic = None,
            content = single_evaluate_message.content,
            ifSend = True,
            ifSaveToLog = True,
            ifAddToMessages = False,
        )
        await single_evaluate_message.update()
        await neo4j_driver.execute_cypher(
            cypher = CYPHER_TEMPLATES["Evaluation_EVAL_Message"],
            message_id = message_history[-2].message_id,
            evaluation_id = singleEvaluateMessageLog.message_id,
            timestamp = singleEvaluateMessageLog.timestamp,
            author = singleEvaluateMessageLog.author,
            hopnumber = 1,
            instruction = single_hop_communication_instruction,
            content = singleEvaluateMessageLog.content,
            evaluation_type = "single_hop_communication_eval",
            score = score,
            reason = reason,
            ifSend = singleEvaluateMessageLog.ifSend,
            ifSaveToLog = singleEvaluateMessageLog.ifSaveToLog,
            ifAddToMessages = singleEvaluateMessageLog.ifAddToMessages,
        )

        # whole hop skill evaluate
        whole_evaluate_message = cl.Message(content="### whole skill evaluate\n", author="gpt-4-32k")
        await whole_evaluate_message.send()

        whole_hop_skill_instruction = '\
            以上のやり取りから、{topic}というテーマにおける{interviewee}の能力のレベルを「初級者」、「中級者」、「上級者」の三択で、理由とともに評価してください。結果は、以下のフォーマットの python dict で出力してください。\n\
            # フォーマット\n{{"score": 評価, "reason": 理由}}\n\
            '.format(
                topic = cl.user_session.get("topic"),
                interviewee = cl.user_session.get("user").identifier,
            )

        messages = [{
            "role": msg_log.role,
            "content": msg_log.content.format(
                interviewee = cl.user_session.get("user").identifier,
                interviewee_info = cl.user_session.get(cl.user_session.get("qa")),
            )
        } for msg_log in message_history[:-1]] + [{
            "role": "user",
            "content": whole_hop_skill_instruction,
        }] 
        # print(messages) 

        res = api_client.api.chat.completions.create(
            model = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"),
            temperature = 0.0,
            messages = messages,
        )
        content = random.choice(res.choices).message.content

        whole_evaluate_message.content += content

        try:
            # print(res)
            res_json = json.loads(content)
            score = res_json["score"]
            reason = res_json["reason"]
        except KeyError as e:
            raise e
        except Exception as e:
            raise e

        wholeEvaluateMessageLog = MessageLog(
            message_id = str(uuid.uuid4()),
            timestamp = datetime.now().isoformat(),
            role = "assistant",
            author = whole_evaluate_message.author,
            topic = None,
            content = whole_evaluate_message.content,
            ifSend = True,
            ifSaveToLog = True,
            ifAddToMessages = False,
        )
        await whole_evaluate_message.update()
        await neo4j_driver.execute_cypher(
            cypher = CYPHER_TEMPLATES["Evaluation_EVAL_Message"],
            message_id = message_history[-2].message_id,
            evaluation_id = wholeEvaluateMessageLog.message_id,
            timestamp = wholeEvaluateMessageLog.timestamp,
            author = wholeEvaluateMessageLog.author,
            hopnumber = -1,
            instruction = whole_hop_skill_instruction,
            content = wholeEvaluateMessageLog.content,
            evaluation_type = "whole_hop_skill_eval",
            score = score,
            reason = reason,
            ifSend = wholeEvaluateMessageLog.ifSend,
            ifSaveToLog = wholeEvaluateMessageLog.ifSaveToLog,
            ifAddToMessages = wholeEvaluateMessageLog.ifAddToMessages,
        )
        # print(wholeEvaluateMessageLog.content)
        return True
    elif user_message.content == "/chart":
        res = await neo4j_driver.execute_cypher(
            cypher = "\
                MATCH path=(m:Message)--(e:Evaluation) \
                WHERE e.evaluation_type=$evaluation_type AND (:Message {message_id: $first_message_id})-[:NEXT*..50]->(m)-[:NEXT*..50]->(:Message {message_id: $last_message_id}) \
                RETURN m.message_id, e.score \
                LIMIT 100\
            ",
            evaluation_type = "single_hop_skill_eval",
            first_message_id = message_history[0].message_id,
            last_message_id = message_history[-1].message_id,
        )
        records = res.records
        # print(records)

        score = []
        for msg in message_history:
            for record in records:
                if record["m.message_id"] == msg.message_id:
                    score.append(record["e.score"])
                    break
            else:
                score.append(0)
        # print("\n-----------------THIS IS RECORD------------------\n\n", [record for record in records])
        # print("\n-----------------THIS IS RECORD TO SCORE----------------\n\n", score)

        fig = go.Figure(
            data = [
                go.Bar(
                    x = [m.message_id[:5]+"..." for m in message_history],
                    y = [i for i in itertools.accumulate(score)] ,
                ),
            ],
            layout_title_text = "累積評価",
        )
        elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
        await cl.Message(content="This message has a chart", elements=elements).send()

        return True
    else:
        return False
