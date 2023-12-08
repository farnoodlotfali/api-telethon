from django.shortcuts import render
from django.http import HttpResponse
from telethon.tl.types import Message, PeerChannel
from django.http import JsonResponse
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from dotenv import dotenv_values
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import date, datetime, timezone
from tqdm import tqdm
import json

config = dotenv_values("../.env")

api_id = config["api_id"]
api_hash = config["api_hash"]

username = config["username"]


# user_input_channel = config["user_input_channel"]
# peer_channel = PeerChannel(1566206468)
# my_channel = client.get_entity(peer_channel)
# 09809225189416
# my_channel = client.get_entity(peer_channel)
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        if isinstance(o, str):
            return o  # Return Persian text as is without encoding

        return json.JSONEncoder.default(self, o)


async def get_user_posts_view(request):
    client = await TelegramClient(username, api_id, api_hash).start()
    await client.connect()
    peer_channel = PeerChannel(1566206468)
    my_channel = await client.get_entity(peer_channel)
    # await client.disconnect()

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 0
    posts = []

    shouldStop = False
    while not shouldStop:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(
            GetHistoryRequest(
                peer=my_channel,
                offset_id=offset_id,
                offset_date=None,
                # offset_date=start_date,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
        if not history.messages:
            break

        messages = history.messages
        for message in tqdm(messages):
            # to control msg date time
            message_date = message.date.replace(tzinfo=timezone.utc)
            # end_date = datetime(2023, 10, 19, tzinfo=timezone.utc)
            end_date = datetime(2023, 11, 1, tzinfo=timezone.utc)
            if message_date < end_date:
                shouldStop = True
                break
            # print(message_date, end_date)

            # will download img and save it a folder called "hi"
            # client.download_media(message, "./"+"hi"+"/")

            # print(message_data['message'] if message_data else None)

            all_messages.append(message.to_dict())

        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        tt = type(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break


    await client.disconnect()
    return JsonResponse({"posts": all_messages}, encoder=DateTimeEncoder)
