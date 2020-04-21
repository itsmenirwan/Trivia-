#!/usr/bin/env python3
import time
import random
import asyncio
import discord
import logging
from datetime import datetime

import networking

logging.basicConfig(level=logging.INFO)
client = discord.Client()
bot_channel = discord.Object(id='696611589876482068')


@client.event
async def on_ready():
    print('\n')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.send_message(bot_channel, "Connection settings invalid")


async def get_questions():
    await client.wait_until_ready()

    try:
        with open("conn_settings.txt", "r") as conn_settings:
            BEARER_TOKEN = conn_settings.readline().strip().split("=")[1]
            USER_ID = conn_settings.readline().strip().split("=")[1]

        main_url = "https://api-quiz.hype.space/shows/now?type=hq&userId={USER_ID}"
        headers = {"Authorization": "Bearer {BEARER_TOKEN}",
                   "x-hq-client": "Android/1.3.0"}
        # "x-hq-stk": "MQ==",
        # "Connection": "Keep-Alive",
        # "User-Agent": "okhttp/3.8.0"}

        while not client.is_closed:
            try:
                # response_data = await networking.get_json_response(main_url, timeout=1.5, headers=headers)
                response_data = await networking.get_json_response(main_url, timeout=1.5, headers=None)
            except Exception as e:
                error = "Server response not JSON, retrying...\n" + str(e)
                await client.send_message(bot_channel, error)
                await asyncio.sleep(5)
                continue

            logging.debug(response_data)

            if "broadcast" not in response_data or response_data["broadcast"] is None:
                if "error" in response_data and response_data["error"] == "Auth not valid":
                    await client.send_message(bot_channel, "Connection settings invalid")
                    #raise RuntimeError("Connection settings invalid")
                else:
                    response_text = "Show not on.\n"
                    next_time = datetime.strptime(
                        response_data["nextShowTime"], "%Y-%m-%dT%H:%M:%S.000Z")
                    now = time.time()
                    offset = datetime.fromtimestamp(
                        now) - datetime.utcfromtimestamp(now)
                    response_text += "Next show time: {}\n".format(
                        (next_time + offset).strftime('%Y-%m-%d %I:%M %p'))
                    response_text += "Prize: " + \
                        response_data["nextShowPrize"] + '\n'
                    await client.send_message(bot_channel, response_text)
                    await asyncio.sleep(60)
            else:
                socket = response_data["broadcast"]["socketUrl"]
                await client.send_message(bot_channel, "@everyone Show active, connecting to socket at {socket}")
                await networking.websocket_handler(socket, headers, client=client, channel=bot_channel)
    except Exception as error:
        await client.send_message(bot_channel, str(error))

client.loop.create_task(get_questions())
client.run(process.env.token)
