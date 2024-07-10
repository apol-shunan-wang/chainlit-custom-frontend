import itertools
import os
import random
import sys
from collections import namedtuple
from datetime import datetime
from time import sleep

import chainlit as cl
from api.client import ApiClientHandler
from chainlit.data import ThreadDict
from chainlit.server import app
from chainlit.step import Step, StepDict
from command import handle_command
from config.settings import set_env_params
from datalayer import Neo4jDataLayer, Neo4jDriver
from fastapi import Request, Response, status  # type: ignore
from fastapi.exceptions import RequestValidationError  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from loader import load_template_dict
from templates import CYPHER_TEMPLATES, PROMPT_TEMPLATES, QUESTIONNAIRE_TEMPLATES

# SET ENV parameters
set_env_params()

# GET azure client
api_client = ApiClientHandler("dev")

# SET UP Neo4j
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
neo4j_driver = Neo4jDriver(URI, AUTH)

# SET UP data layer
cl.data._data_layer = Neo4jDataLayer()

"""
class ThreadDict(TypedDict):
    id: str
    createdAt: str
    name: Optional[str]
    userId: Optional[str]
    userIdentifier: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[Dict]
    steps: List["StepDict"]
    elements: Optional[List["ElementDict"]]

class StepDict(TypedDict, total=False):
    name: str
    type: StepType
    id: str
    threadId: str
    parentId: Optional[str]
    disableFeedback: bool
    streaming: bool
    waitForAnswer: Optional[bool]
    isError: Optional[bool]
    metadata: Dict
    tags: Optional[List[str]]
    input: str
    output: str
    createdAt: Optional[str]
    start: Optional[str]
    end: Optional[str]
    generation: Optional[Dict]
    showInput: Optional[Union[bool, str]]
    language: Optional[str]
    indent: Optional[int]
    feedback: Optional[FeedbackDict]
"""


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@cl.password_auth_callback
async def auth_callback(email: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database

    result = await neo4j_driver.execute_cypher(
        cypher=CYPHER_TEMPLATES["get_user_properties"],
        email=email,
    )
    records = result.records

    # return cl.User(
    #     id=1,
    #     identifier="test",
    #     createdAt="2024-07-04",
    #     metadata={
    #         "role": "user",
    #         "provider": "credentials",
    #         "email": "test@apol.co.jp",
    #         "name": "テスト名前",
    #         "phonenumber": "090-9999-8888",
    #     },
    # )

    if (email, password) == (records[0][0], records[0][1]):
        return cl.User(
            id=records[0][0],
            identifier=records[0][0],
            createdAt=records[0][2],
            metadata={
                "role": "user",
                "provider": "credentials",
                "email": records[0][0],
                "name": records[0][3],
                "phonenumber": records[0][4],
            },
        )
    else:
        return None


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="経理・財務",
            markdown_description="",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="総務",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
        cl.ChatProfile(
            name="法務",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
        cl.ChatProfile(
            name="人事",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
        cl.ChatProfile(
            name="情報システム",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
        cl.ChatProfile(
            name="データサイエンティスト",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
        cl.ChatProfile(
            name="ITコンサルタント",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
        cl.ChatProfile(
            name="ビジネスコンサルタント",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
        cl.ChatProfile(
            name="インフラエンジニア",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
        cl.ChatProfile(
            name="ソフトウェアエンジニア（バックエンド）",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
        cl.ChatProfile(
            name="ソフトウェアエンジニア（フロントエンド）",
            markdown_description="The underlying LLM model is **GPT-4**.",
        ),
    ]


@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)
    cl.user_session.set("settings", settings)


def update_thread_dict(step_dict, **metadata):
    thread_dict = cl.user_session.get("thread_dict")
    metadata["user_session_id"] = cl.user_session.get("id")
    thread_dict["metadata"].update(metadata)
    thread_dict["steps"].append(step_dict)

    cl.user_session.set("thread_dict", thread_dict)

    return thread_dict


def process_step(step_dict, **kwargs):
    if type(step_dict) is Step:
        step_dict = step_dict.to_dict()

    user_session_id = cl.user_session.get("id")
    thread_dict = cl.user_session.get("thread_dict")
    last_step_id = thread_dict["steps"][-1]["id"] if len(thread_dict["steps"]) > 0 else None

    kwargs["metadata"] = {
        "last_message_id": last_step_id,
        "user_session_id": user_session_id,
        "role": "assistant",
        "author": cl.user_session.get("user").identifier,
        "topic": cl.user_session.get("topic"),
        "topics": cl.user_session.get("topics"),
        "qa_loop": cl.user_session.get("qa_loop"),
        "ifAddToMessages": False,
    } | kwargs["metadata"]

    step_dict.update(kwargs)
    update_thread_dict(step_dict=step_dict)

    return step_dict


@cl.step(type="assistant_message", show_input=False)
async def show_assistant_message(content, **kwargs):
    kwargs = {"role": "assistant", "author": "template"} | kwargs

    current_step = cl.context.current_step

    step_dict = process_step(
        current_step,
        output=content,
        metadata=kwargs,
    )
    current_step.metadata = step_dict["metadata"]
    current_step.output = step_dict["output"]
    return content


@cl.step(type="user_message", show_input=False)
async def show_user_message(content, **kwargs):
    kwargs = {
        "role": "user",
    } | kwargs

    current_step = cl.context.current_step

    step_dict = process_step(
        current_step,
        output=content,
        metadata=kwargs,
    )
    current_step.metadata = step_dict["metadata"]
    current_step.output = step_dict["output"]
    return content


@cl.step(type="user_message", show_input=False)
async def log_user_message(content, **kwargs):
    kwargs = {"role": "user"} | kwargs

    current_step = cl.context.current_step

    step_dict = process_step(
        current_step,
        type="user_message",
        output=content,
        metadata=kwargs,
    )
    current_step.metadata = step_dict["metadata"]
    current_step.output = step_dict["output"]

    return content


@cl.step(type="assistant_message", show_input=False)
async def log_assistant_message(content, **kwargs):
    kwargs = {"role": "assistant", "author": "template"} | kwargs

    current_step = cl.context.current_step

    step_dict = process_step(
        current_step,
        type="assistant_message",
        output=content,
        metadata=kwargs,
    )
    current_step.metadata = step_dict["metadata"]
    current_step.output = step_dict["output"]

    return content


@cl.step(type="system_message")
async def system_message():
    interviewee = cl.user_session.get("user").identifier

    topic = "essentials"
    topics = []
    qa_loop = 1
    thread_dict = ThreadDict(
        steps=[],
        metadata={},
        userIdentifier=interviewee,
    )

    cl.user_session.set("topic", topic)
    cl.user_session.set("topics", topics)
    cl.user_session.set("qa_loop", qa_loop)
    cl.user_session.set("thread_dict", thread_dict)

    # system message
    current_step = cl.context.current_step

    content = cl.user_session.get("PROMPT_TEMPLATES")["system_definition"]
    metadata = {
        "author": "template",
        "role": "system",
        "ifAddToMessages": True,
    }
    step_dict = process_step(
        current_step,
        output=content,
        metadata=metadata,
    )
    current_step.metadata = step_dict["metadata"]
    current_step.output = step_dict["output"]

    return content


async def goahead_step1():
    sleep(0.5)
    content = "AI面接は下記の流れで進めさせていただきます。"
    await show_assistant_message(content, ifAddToMessages=False)

    sleep(0.5)
    content = "【STEP1】基礎スキルに関するアンケート（3問）\n【STEP2】AI面接官によるスキル/ご経験に関する質疑応答（平均15問）\n\n※ページを閉じると情報が失われてしまいますのでご注意ください。"
    await show_assistant_message(content, ifAddToMessages=False)

    sleep(0.5)
    content = "では、まず\n**【STEP1】基礎スキルに関するアンケート（3問）**\nをお願い致します。"
    await show_assistant_message(content, ifAddToMessages=False)

    content = "スタートボタンを押して開始して下さい。"

    goahead_message = cl.AskActionMessage(
        content=content,
        author="askAction",
        actions=[cl.Action(name="【STEP1】スタート", value="【STEP1】スタート", label="【STEP1】スタート")],
        timeout=180,
    )

    sleep(0.5)
    res = None
    while res == None:
        res = await goahead_message.send()
        goahead_message.content = content
        await goahead_message.update()
    else:
        await goahead_message.remove()
        await show_assistant_message(content, ifAddToMessages=False)
        sleep(0.5)
        await show_user_message(res.get("value"), ifAddToMessages=False)

    # return ans


async def askEssentialStep(qa):
    content = qa["question"]

    action_message = cl.AskActionMessage(
        content=content,
        author="askAction",
        actions=[cl.Action(name=answer["label"], value=answer["label"], label=answer["label"]) for answer in qa["answers"]],
        timeout=180,
    )

    sleep(0.5)
    res = None
    while res == None:
        res = await action_message.send()
        action_message.content = content
        await action_message.update()
    else:
        await action_message.remove()
        await show_assistant_message(content, ifAddToMessages=False)
        sleep(0.5)
        await show_user_message(res.get("value"), ifAddToMessages=False)


async def askEssentialsStep(questionnaire):
    for qa in questionnaire:
        sleep(0.5)
        await askEssentialStep(qa)


async def goahead_step2():
    sleep(0.5)
    content = "ご回答ありがとうございます。これで【STEP1】は完了です。"
    await show_assistant_message(content, ifAddToMessages=False)

    sleep(0.5)
    content = "では次に、\n**【STEP2】AI面接官によるスキル/ご経験に関する質疑応答（平均15問）**\nに移らせていただきます。"
    await show_assistant_message(content, ifAddToMessages=False)

    content = "スタートボタンを押して開始してください。"

    goahead_message = cl.AskActionMessage(
        content=content,
        author="askAction",
        actions=[cl.Action(name="【STEP2】スタート", value="【STEP2】スタート", label="【STEP2】スタート")],
        timeout=180,
    )

    sleep(0.5)
    res = None
    while res == None:
        res = await goahead_message.send()
        goahead_message.content = content
        await goahead_message.update()
    else:
        await goahead_message.remove()
        await show_assistant_message(content, ifAddToMessages=False)
        sleep(0.5)
        await show_user_message(res.get("value"), ifAddToMessages=False)


async def selectTopicsMessage(job):
    if job in ["経理・財務", "総務", "法務", "人事", "情報システム"]:
        PROMPT_TEMPLATES = load_template_dict("text_template/prompt/prompt_set_backoffice.json")
        skill_set = job
    elif job in ["データサイエンティスト"]:
        PROMPT_TEMPLATES = load_template_dict("text_template/prompt/prompt_set.json")
        skill_set = "データサイエンス"
    else:
        pass

    content = PROMPT_TEMPLATES["intro"]
    sleep(0.5)
    await show_assistant_message(content, ifAddToMessages=False)

    res = await neo4j_driver.execute_cypher(
        cypher="MATCH (s:Skill) WHERE s.skill_name=$skill_set WITH s MATCH (t:Skill) WHERE (t)-[:A_PART_OF]->(s) RETURN t.skill_name AS skill_name LIMIT 25",
        skill_set=skill_set,
    )
    skill_topics = res.records

    selected_topics = []

    while len(selected_topics) < 3:
        if len(selected_topics) == 0:
            content = "**最もアピールしたいスキル** を選択してください。"
        elif len(selected_topics) == 1:
            content = "**2番目にアピールしたいスキル** を選択してください。"
        elif len(selected_topics) == 2:
            content = "**3番目にアピールしたいスキル** を選択してください。"
        else:
            raise ValueError("too much skill")

        action_message = cl.AskActionMessage(
            content=content,
            author="askAction",
            actions=[
                cl.Action(
                    name=record["skill_name"],
                    value=record["skill_name"],
                    label=record["skill_name"],
                )
                for record in skill_topics
            ],
            timeout=180,
        )

        sleep(0.5)
        res = None
        while res == None:
            res = await action_message.send()
            action_message.content = content
            await action_message.update()
        else:
            await action_message.remove()
            await show_assistant_message(content, ifAddToMessages=False)
            sleep(0.5)
            await show_user_message(res.get("value"), ifAddToMessages=False)
        selected_topics.append(res.get("value"))
    else:
        cl.user_session.set("topics", selected_topics)


async def new_topic_start():
    topic = cl.user_session.get("topic")
    topics = cl.user_session.get("topics")
    if len(topics) >= 2:
        content = f"ではまず、最もアピールしたいスキル **「{topic}」** に関して、質疑応答をさせて頂きます。（平均5回）"
    else:
        rs = 3 - len(topics)
        content = f"次に、{rs}番目にアピールしたいスキル **「{topic}」** に関して、質疑応答をさせて頂きます。（平均5回）"

    await show_assistant_message(content=content, author="gpt-4-32k", ifAddToMessages=True)


@cl.step(type="undefined")
async def make_context_messages(system, instruction, steps=None):
    interviewee = cl.user_session.get("user").identifier
    topic = cl.user_session.get("topic")
    system_message = (
        [
            {
                "role": "system",
                "content": system.format(
                    interviewee=interviewee,
                    topic=topic,
                ),
            }
        ]
        if system
        else [
            {
                "role": "system",
                "content": "you are a helpful assistant.",
            }
        ]
    )

    instruction_message = (
        [
            {
                "role": "user",
                "content": instruction.format(
                    interviewee=interviewee,
                    topic=topic,
                ),
            }
        ]
        if instruction
        else [{"role": "user", "content": "Hello?"}]
    )

    if steps:
        messages = (
            system_message
            + [
                {
                    "role": step_dict["metadata"]["role"],
                    "content": step_dict["output"].format(interviewee=interviewee, topic=topic),
                }
                for step_dict in steps
                if step_dict["metadata"]["ifAddToMessages"]
            ]
            + instruction_message
        )
    else:
        messages = system_message + instruction_message

    return messages


@cl.step(type="tool")
async def get_llm_chat_response(messages):
    res = api_client.api.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"),
        messages=messages,
        temperature=0.0,
        max_tokens=800,
    )
    content = random.choice(res.choices).message.content
    return content


async def firstQuestionMessage():
    thread_dict = cl.user_session.get("thread_dict")
    await new_topic_start()

    system = cl.user_session.get("PROMPT_TEMPLATES")["system_definition"]
    instruction = "テーマ「{topic}」に関する{interviewee}のスキルや職務経験を知るための質問を一つだけ考え、聞いてください。聞ける内容は一つだけです。"

    messages = await make_context_messages(
        system=system,
        instruction=instruction,
        steps=thread_dict["steps"][1:],
    )
    content = await get_llm_chat_response(messages=messages)
    question = await paraphrasing(content)

    await show_assistant_message(question, author="gpt-4-32k", ifAddToMessages=True)


@cl.step(type="tool", show_input=False)
async def chat_analyze():
    system = cl.user_session.get("PROMPT_TEMPLATES")["system_definition"]
    instruction = "以上の質問と回答における{interviewee}の思考過程を、ステップ・バイ・ステップで論理的に分析し、「{topic}」に関する{interviewee}のスキルと職務経験について、\n1. 回答からはっきりわかる事実\n2. 回答に使われた専門知識と、それの理解の程度\n3. 分析から推測できるが、確信を得るためにはさらなる質問を必要とすること\nを列挙し、詳しく説明してください。"

    messages = await make_context_messages(
        system=system,
        instruction=instruction,
        steps=cl.user_session.get("thread_dict")["steps"][1:],
    )

    content = await get_llm_chat_response(messages)
    return content


@cl.step(type="tool", show_input=False)
async def make_question(analysis):
    system = cl.user_session.get("PROMPT_TEMPLATES")["system_definition"]  # + "\n\n#スキルや職務経験についての分析\n{analysis}".format(analysis=analysis)
    instruction = "以上のやり取りと分析をもとに、「{topic}」に関する{interviewee}のスキルや職務経験をより良く理解するための、最も核心をに迫る質問を考え、聞いてください。聞ける内容は一つだけです。接続詞「また」を使わずに質問を考えてさい。"

    messages = await make_context_messages(
        system=system,
        instruction=instruction,
        steps=cl.user_session.get("thread_dict")["steps"][1:],
    )

    content = await get_llm_chat_response(messages)
    return content


@cl.step(type="tool", show_input=False)
async def paraphrasing(question):
    if question.startswith("「") and question.endswith("」"):
        question = question.strip("「」")

    system = "あなたは、有能なアシスタントです。"
    instruction = "以下に与えるTextをもとに、次のRuleに従って修正し、質問してください。\n\n# Rule\n- 質問は簡潔にしてください。\n- 特に、「また」などの接続詞は使わないでください。\n- ただし、もとのTextに含まれている情報が失われないように、一つのことだけに集中して質問するなどの工夫をしてください。。\n- 分析や質問の意味が不明瞭な部分があれば補足してください。\n- 自然な日本語で、要点を得た表現に言い換えてください。\n\n# Text\n{question}\n\n# Output\n面接官による質疑".format(
        question=question
    )

    messages = await make_context_messages(
        system=system,
        instruction=instruction,
        steps=[],
    )

    content = await get_llm_chat_response(messages)
    if content.startswith("「") and content.endswith("」"):
        content = content.strip("「」")
    return content


async def questionMessage():
    analysis = ""
    # analysis = await chat_analyze()
    question = await make_question(analysis)
    # question = await paraphrasing(question)

    await show_assistant_message(question, author="gpt-4-32k", ifAddToMessages=True)


# @cl.step(type="tool")
async def ask_contact_info():
    content = "以上で【STEP2】は完了です。\n\n最後に、AI面接の合否連絡用に、下記情報をご共有いただきます。\n- 氏名\n- メールアドレス\n- 電話番号"
    await show_assistant_message(content=content, ifAddToMessages=False)

    # name
    content = "氏名をご記入ください。"
    username_message = cl.AskUserMessage(
        content=content,
        author="askAction",
        timeout=180,
    )
    username = None
    while username == None:
        username = await username_message.send()
        username_message.content = content
        await username_message.update()

    # email
    content = "メールアドレスをご記入ください。"
    email_message = cl.AskUserMessage(
        content=content,
        author="askAction",
        timeout=180,
    )
    email = None
    while email == None:
        email = await email_message.send()
        email_message.content = content
        await email_message.update()

    # phonenumber
    content = "電話番号をご記入ください。"
    phonenumber_message = cl.AskUserMessage(
        content=content,
        author="askAction",
        timeout=180,
    )
    phonenumber = None
    while phonenumber == None:
        phonenumber = await phonenumber_message.send()
        phonenumber_message.content = content
        await phonenumber_message.update()

    user = cl.user_session.get("user")
    # user.metadata["name"] = username["output"]
    # user.metadata["email"] = email["output"]
    # user.metadata["phonenumber"] = phonenumber["output"]
    user.metadata["start_message_id"] = cl.user_session.get("thread_dict")["steps"][0]["id"]

    cl.user_session.set("user", user)


async def end_greeting():
    content = "以上でAI面接は終了です。ありがとうございました！\n\n面接の結果は、1週間ほどで、メールにてお知らせ致します。"
    await show_assistant_message(content=content, ifAddToMessages=False)


@cl.on_chat_start
async def on_chat_start():
    # セッション初期化
    # チャットの設定
    chat_profile = cl.user_session.get("chat_profile")
    print("chat_profile is:", chat_profile)

    if chat_profile in ["経理・財務", "総務", "法務", "人事", "情報システム"]:
        QUESTIONNAIRE_TEMPLATES = load_template_dict("text_template/questionnaire/questionnaire_backoffice.json")
        cl.user_session.set("PROMPT_TEMPLATES", load_template_dict("text_template/prompt/prompt_set_backoffice.json"))
    elif chat_profile in ["データサイエンティスト"]:
        QUESTIONNAIRE_TEMPLATES = load_template_dict("text_template/questionnaire/questionnaire_set.json")
        cl.user_session.set("PROMPT_TEMPLATES", load_template_dict("text_template/prompt/prompt_set.json"))
    else:
        pass

    content = f"上部のプルダウンに表示されているものが応募職種になります。 **{chat_profile}** で正しいですか？違う場合は、正しい応募職種を選択してください。"
    msg = cl.AskActionMessage(
        content=content,
        author="askAction",
        actions=[
            cl.Action(
                name="GO",
                value="GO",
                label="GO",
            )
        ],
        timeout=600,
    )

    sleep(0.5)
    res = None
    while res == None:
        res = await msg.send()
        msg.content = content
        await msg.update()
    else:
        await msg.remove()

    # system message 定義
    sleep(0.5)
    system_step_dict = await system_message()

    # 必須・歓迎要件の申告
    sleep(0.5)
    await goahead_step1()
    sleep(0.5)
    await askEssentialsStep(QUESTIONNAIRE_TEMPLATES)

    # トピックスの選択
    sleep(0.5)
    await goahead_step2()
    sleep(0.5)
    await selectTopicsMessage(chat_profile)

    # 最初の質問
    topics = cl.user_session.get("topics")
    topic = topics.pop(0)

    cl.user_session.set("topics", topics)
    cl.user_session.set("topic", topic)
    cl.user_session.set("qa_loop", 1)

    sleep(0.5)
    await firstQuestionMessage()


@cl.on_chat_resume
async def on_chat_resume(thread_dict: ThreadDict):
    """
    Resume Chatボタンを押して、
    Chatがアクティブになる前までに走る処理
    """
    print("resume chat\n")
    chat_profile = cl.user_session.get("chat_profile")
    print("chat_profile is:", chat_profile)

    if chat_profile in ["経理・財務", "総務", "法務", "人事", "情報システム"]:
        QUESTIONNAIRE_TEMPLATES = load_template_dict("text_template/questionnaire/questionnaire_backoffice.json")
        cl.user_session.set("PROMPT_TEMPLATES", load_template_dict("text_template/prompt/prompt_set_backoffice.json"))
    elif chat_profile in ["データサイエンティスト"]:
        QUESTIONNAIRE_TEMPLATES = load_template_dict("text_template/questionnaire/questionnaire_set.json")
        cl.user_session.set("PROMPT_TEMPLATES", load_template_dict("text_template/prompt/prompt_set.json"))
    else:
        pass

    # thread:ThreadDictから thread_dict を復元する
    cl.user_session.set("thread_dict", thread_dict)
    print(thread_dict["steps"][-1])

    # conversation loopの状態の復元
    # topics = json.loads(thread_dict["steps"][-1]["metadata"]["topics"])
    topics = thread_dict["steps"][-1]["metadata"]["topics"]
    cl.user_session.set("topics", topics)
    print(topics)

    topic = thread_dict["steps"][-1]["metadata"]["topic"]
    cl.user_session.set("topic", topic)
    print(topic)

    qa_loop = thread_dict["steps"][-1]["metadata"]["qa_loop"]
    cl.user_session.set("qa_loop", qa_loop)
    print(qa_loop)


@cl.on_message
async def on_message(user_message: cl.Message):
    """
    ユーザーからメッセージがポストされたときの応答！
    """
    # コマンド処理
    if user_message.content.startswith("/"):
        result = await handle_command(user_message)
        return result
    else:
        pass

    user = cl.user_session.get("user").identifier
    thread_dict = cl.user_session.get("thread_dict") or []  # type: ignore
    topic = cl.user_session.get("topic")
    topics = cl.user_session.get("topics")
    qa_loop = cl.user_session.get("qa_loop")

    # ユーザーからのメッセージを格納処理
    await user_message.remove()
    await log_user_message(user_message.content, ifAddToMessages=True)

    if qa_loop >= 5:
        if len(topics) <= 0:
            await ask_contact_info()
            await end_greeting()
            return
        else:
            topic = topics.pop(0)
            cl.user_session.set("topic", topic)
            cl.user_session.set("topics", topics)
            cl.user_session.set("qa_loop", 1)
            await firstQuestionMessage()
    else:
        qa_loop += 1
        cl.user_session.set("qa_loop", qa_loop)
        await questionMessage()


@cl.on_chat_end
async def on_chat_end():
    await cl.data._data_layer.upsert_feedback(feedback=None, ifCommit=True)
    try:
        user = cl.user_session.get("user")
        print(user)
        await cl.data._data_layer.driver.execute_cypher(
            cypher=CYPHER_TEMPLATES["start_step"],
            name=user.metadata["name"],
            email=user.metadata["email"],
            phonenumber=user.metadata["phonenumber"],
            # message_id = user.metadata["start_message_id"],
            message_id=cl.user_session.get("thread_dict")["steps"][0]["id"],
            password="password",
        )
    except Exception as e:
        print(e)
        pass

    print("\n------------- CHAT END --------------\n")


@cl.on_logout
def main(request: Request, response: Response):
    # response.delete_cookie("my_cookie")
    print("\n------------- LOGOUT !! ----------------\n")


@cl.step(type="tool")
async def askProfileStep():
    ask_profile_message = cl.AskActionMessage(
        content="履歴書・職務経歴書を提出されますか？\n\n※AI選考において、提出の有無は合否に関係ありません。\n※ここで提出しない場合でも、2次面接に進んでいただく際には提出をお願い致します。",
        author="askAction",
        actions=[
            cl.Action(
                name="提出する",
                value="提出する",
                label="提出する",
            ),
            cl.Action(
                name="提出する",
                value="提出しない",
                label="提出しない",
            ),
        ],
    )

    sleep(0.5)
    res = None
    while res == None:
        res = await ask_profile_message.send()
    else:
        await ask_profile_message.remove()

    if res.get("value") == "提出する":
        resume_message = cl.AskFileMessage(
            content="こちらには履歴書をご提出ください。",
            author="askAction",
            max_files=1,
            accept=["text/plain", "application/pdf"],
        )

        resume = None
        while resume == None:
            resume = resume_message.send()

        cv_message = cl.AskFileMessage(
            content="こちらには職務経歴書をご提出ください。",
            author="askAction",
            max_files=1,
            accept=["text/plain", "application/pdf"],
        )

        cv = None
        while cv == None:
            cv = cv_message.send()

        content = "履歴書・職務経歴書の提出ありがとうございます。\n本日はありがとうございました。"
        message = cl.Message(content=content, author="template")
        message.send()

    elif res.get("value") == "提出しない":
        content = "それでは、AI面接の合否連絡用に、下記情報をご共有ください。\n1. 氏名\n1. メールアドレス\n1. 電話番号"
        sleep(0.5)
        username_message = cl.AskUserMessage(
            content="お名前をご記入ください。",
            author="askAction",
        )
        email_message = cl.AskUserMessage(
            content="メールアドレスをご記入ください。",
            author="askAction",
        )
        phonenumber_message = cl.AskUserMessage(
            content="電話番号をご記入ください。",
            author="askAction",
        )
        username = None
        while username == None:
            username = username_message.send()
        email = None
        while email == None:
            email = email_message.send()
        phonenumber = None
        while phonenumber == None:
            phonenumber = phonenumber_message.send()

        await cl.Message(content="\n本日は以上になります！\nありがとうございました。", author="template").send()
