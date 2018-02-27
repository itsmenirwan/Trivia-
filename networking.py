import asyncio
import json
import logging
import re

import aiohttp

import question


async def fetch(url, session, timeout):
    try:
        async with session.get(url, timeout=timeout) as response:
            return await response.text()
    except:
        print("Server timeout/error to {}".format(url))
        return ""


async def get_responses(urls, timeout, headers):
    tasks = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session, timeout))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses


async def get_response(url, timeout, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        return await fetch(url, session, timeout)


async def get_json_response(url, timeout, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, timeout=timeout) as response:
            return await response.json()


async def websocket_handler(uri, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.ws_connect(uri) as ws:
            for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    message = msg.data
                    message = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", message)

                    message_data = json.loads(message)
                    logging.info(message_data)

                    if message_data["type"] == "question":
                        question_str = message_data["question"]
                        answers = [ans["text"] for ans in message_data["answers"] if ans["text"].strip() != ""]
                        print("\n" * 5)
                        print("Question detected.")
                        print("Question {} out of {}".format(message_data["questionNumber"],
                                                             message_data["questionCount"]))
                        print(question_str)
                        print(answers)
                        print()
                        print(await question.answer_question(question_str, answers))
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    print("Socket closed")
                    break
