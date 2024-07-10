import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional

from chainlit.step import StepDict
from chainlit.data import ThreadDict
from chainlit.element import Element
import chainlit as cl

from neo4j import AsyncGraphDatabase

from collections import namedtuple

from templates import CYPHER_TEMPLATES

deleted_thread_ids = []  # type: List[str]

class Neo4jDriver:
    def __init__(self, uri: str, auth: (str, str)):
        self.driver = AsyncGraphDatabase.driver(uri, auth=auth)

    async def execute_cypher(self, cypher, *args, **replacements):
        result = await self.driver.execute_query(cypher, **replacements, database_="neo4j")
        return result

    async def close(self):
        await self.driver.close()


class Neo4jDataLayer(cl.data.BaseDataLayer):
    def __init__(self):
        URI = os.getenv("NEO4J_URI")
        AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        self.driver = Neo4jDriver(URI, AUTH)
        self.thread_history = []
        self.feedback_dict = defaultdict(list)

    async def get_user(self, identifier: str):
        # Fetches a user by their identifier. Return type is optionally a PersistedUser.
        result = await self.driver.execute_cypher(
            cypher = CYPHER_TEMPLATES["get_user_properties"],
            email = identifier,
        )
        records = result.records

        return cl.PersistedUser(
            id = records[0][0],
            identifier = records[0][0],
            createdAt = records[0][2].iso_format(),
            metadata={
                "role": "user",
                "provider": "credentials",
                "email": records[0][0],
                "name": records[0][3],
                "phonenumber": records[0][4],
            },
        )

    async def create_user(self, user: cl.User):
        # Creates a new user based on the User instance provided. Return type is optionally a PersistedUser.
        # result = await self.driver.execute_cypher(
        #     cypher = CYPHER_TEMPLATES["start_step"],
        #     name = user.identifier,
        #     email = user.metadata["email"],
        #     phonenumber = user.metadata["phonenumber"],
        #     message_id = user.metadata["start_message_id"],
        #     password = "password",
        # )
        pass

    async def upsert_feedback(self, feedback: cl.data.Feedback, ifCommit=False):
        # Inserts or updates feedback. Accepts a Feedback instance and returns a string as an identifier of the persisted feedback.
        if ifCommit:
            for message_id, feedback_list in self.feedback_dict.items():
                for f in feedback_list:
                    result = await self.driver.execute_cypher(
                        cypher = CYPHER_TEMPLATES["upsert_feedback"],
                        message_id = message_id,
                        value = f["value"],
                        nega_posi = f["nega_posi"],
                        comment = f["comment"],
                    )
        else:
            if feedback.value == 1:
                nega_posi = "Positive"
            elif feedback.value == 0:
                nega_posi = "Negative"
            self.feedback_dict[feedback.forId] += [{
                "value": feedback.value,
                "nega_posi": nega_posi,
                "comment": feedback.comment,
            }]
            
        print(self.feedback_dict)
        # return feedback.id

    async def delete_feedback(self, feedback_id: str):
        # Deletes a feedback by feedback_id. Return True if it was successful.
        return False

    async def create_element(self, element_dict: cl.element.ElementDict):
        # Adds a new element to the data layer. Accepts ElementDict as an argument.
        pass

    async def get_element(self, thread_id: str, element_id: str):
        # Retrieves an element by thread_id and element_id. Return type is optionally an ElementDict.
        pass

    async def delete_element(self, element_id: str):
        # Deletes an element given its identifier element_id.
        pass

    async def create_step(self, step_dict: StepDict):
        # Creates a new step in the data layer. Accepts StepDict as an argument.
        print("+++++++++++", step_dict["id"], step_dict["type"], step_dict["name"], "|", step_dict["output"][:20])

        if step_dict["name"] != "askAction" and step_dict["type"] not in ["tool"]:
            print(step_dict["metadata"])


    async def update_step(self, step_dict: StepDict):
        # Updates an existing step. Accepts StepDict as an argument.
        print("^^^^^^^^^^^", step_dict["id"], step_dict["type"], step_dict["name"], "|", step_dict["output"][:20]+"...")

        if step_dict["name"] != "askAction" and step_dict["type"] not in ["tool"]:
            print(step_dict["metadata"])
            await self.driver.execute_cypher(
                cypher = CYPHER_TEMPLATES["MERGE_Message"],
                message_id = step_dict["id"],
                createdAt = step_dict["createdAt"],
                type = step_dict["type"],
                name = step_dict["name"],
                input = step_dict["input"],
                output = step_dict["output"],
                role = step_dict["metadata"].get("role"),
                author = step_dict["metadata"].get("author"),
                topic = step_dict["metadata"].get("topic"),
                topics = step_dict["metadata"].get("topics"),
                qa_loop = step_dict["metadata"].get("qa_loop"),
                ifAddToMessages = step_dict["metadata"].get("ifAddToMessages"),
            )
        
            if step_dict["metadata"].get("last_message_id"):
                await self.driver.execute_cypher(
                    cypher = CYPHER_TEMPLATES["MERGE_NEXT"],
                    last_message_id = step_dict["metadata"]["last_message_id"],
                    new_message_id = step_dict["id"],
                    user_session_id = step_dict["metadata"]["user_session_id"],
                )

    async def delete_step(self, step_id: str):
        # Deletes a step given its identifier step_id.
        pass

    async def list_threads(
        self,
        pagination: cl.data.Pagination,
        filters: cl.data.ThreadFilter,
    ) -> cl.data.PaginatedResponse[ThreadDict]:
        """
        Lists threads based on pagination and filters arguments. Returns a PaginatedResponse[ThreadDict].
        """
        if not filters.userId:
            raise ValueError("userId is required")
        else:
            userId = filters.userId

        search_text = filters.search or ""

        # ログを取ってくる
        result = await self.driver.execute_cypher(
            cypher = CYPHER_TEMPLATES["get_threads_path"],
            identifier = userId,
            output = r"[\s.]*" + search_text + r"[.|\s]*",
        )
        records = result.records
        # print(userId)
        # print(records)

        thread_history = []

        for path in records[::-1]:
            steps = [{
                "id": node.get("message_id"),
                "createdAt": node.get("createdAt"),
                "name": node.get("name"),
                "type": node.get("type") or "assistant_message",
                "threadId": path.data()["path"][-1].get("message_id"),
                "input": node.get("input"),
                "output": node.get("output"),
                "metadata": {
                    "last_message_id": path.data()["path"][i-2].get("message_id") if i > 2 else None,
                    "author": node.get("author"),
                    "role": node.get("role"),
                    "topic": node.get("topic"),
                    "topics": node.get("topics"),
                    "qa_loop": node.get("qa_loop"),
                    "ifAddToMessages": node.get("ifAddToMessages"),
                },
                "streaming": False,
                "disableFeedback": False,
            } for i, node in enumerate(path.data()["path"]) if isinstance(node, dict) ]

            thread = {
                "id": steps[-1]["id"],
                "createdAt": steps[-1]["createdAt"],
                "name": steps[-1]["id"][:4]+"..."+"@"+steps[-1]["createdAt"][11:],
                "userIdentifier": userId,
                "userId": userId,
                "metadata": {
                    "topic": steps[-1]["metadata"]["topic"],
                    "topics": steps[-1]["metadata"]["topics"],
                    "qa_loop": steps[-1]["metadata"]["qa_loop"],
                },
                "steps": steps,
            }
            # print(thread["metadata"])

            thread_history.append(thread)

        self.set_thread_history(thread_history)

        return cl.data.PaginatedResponse(
            data = [ t for t in self.get_thread_history() ],
            pageInfo=cl.data.PageInfo(
                hasNextPage=False, startCursor=None, endCursor=None
            ),
        )
    
    def set_thread_history(self, value):
        self.thread_history = value
    
    def get_thread_history(self):
        # print(self.thread_history)
        return self.thread_history

    async def get_thread(self, thread_id: str):
        # Retrieves a thread by its identifier thread_id. Return type is optionally a ThreadDict.
        thread_history = self.get_thread_history()
        
        thread = next((t for t in thread_history if t["id"] == thread_id), None)
        # print("\n-------------THIS IS THREAD-------------\n", thread)
        return thread

    async def get_thread_author(self, thread_id: str) -> str:
        # Fetches the author of a given thread by thread_id. Returns a string representing the author identifier.
        thread = await self.get_thread(thread_id)
        if not thread:
            return ""
        user_identifier = thread.get("userIdentifier")
        if not user_identifier:
            return ""

        return user_identifier

    async def delete_thread(self, thread_id: str):
        # Deletes a thread given its identifier thread_id.
        deleted_thread_ids.append(thread_id)

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ):
        # Updates a thread’s details like name, user_id, metadata, and tags. Arguments are mostly optional.
        # thread_history = self.get_thread_history()
        # thread = next((t for t in thread_history if t["id"] == thread_id), None)
        # if thread:
        #     if name:
        #         thread["name"] = name
        #     if metadata:
        #         thread["metadata"] = metadata
        #     if tags:
        #         thread["tags"] = tags
        # else:
        #     thread_history.append(
        #         {
        #             "id": thread_id,
        #             "name": name,
        #             "metadata": metadata,
        #             "tags": tags,
        #             "createdAt": utc_now(),
        #             "userId": user_id,
        #             "userIdentifier": user_id,
        #             "steps": [],
        #         }
        #     )
        #     self.set_thread_history(thread_history)
        pass

    async def delete_user_session(self, id: str):
        # Deletes a user session given its identifier id. Returns a boolean value indicating success.
        pass
