from django.shortcuts import render
from django.http import HttpResponse
from telethon.tl.types import Message, PeerChannel
from django.http import JsonResponse
from telethon.sync import TelegramClient, events
from telethon.tl.types import InputPeerUser
from dotenv import dotenv_values
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import date, datetime, timezone
from tqdm import tqdm
import json
from .models import PostInitial
from asgiref.sync import sync_to_async
import requests

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


def get_posts_view(request):
    posts = PostInitial.objects.all()

    return render(request, "home.html", {"posts": posts})


def get_coin_view(request):
    symbol = request.GET.get("symbol", None)
    print(symbol)
    if symbol:
        url = f"https://api-futures.kucoin.com/api/v1/ticker?symbol={symbol}"

        response = requests.get(url)
        data = response.json()

        return render(request, "coin.html", {"data": data})
    else:
        # Handle case when symbol parameter is not provided
        error_data = {
            "error": "Symbol parameter is missing.",
        }
        return JsonResponse(error_data, status=400)


async def get_user_posts_view(request):
    # client = await TelegramClient(username, api_id, api_hash).start()
    # await client.connect()
    peer_channel = PeerChannel(2101974116)
    # peer_channel = PeerChannel(1566206468)
    # my_channel = await client.get_entity(peer_channel)
    # await client.disconnect()

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 0
    posts = []

    async with TelegramClient(username, api_id, api_hash) as client:

        async def handle_new_message(event):
            try:
                msg = event.message
                data = {
                    "message_id": msg.id,
                    "channel_id": msg.peer_id.channel_id,
                    "message": msg.message,
                    "reply_to_msg_id": msg.reply_to.reply_to_msg_id
                    if msg.reply_to
                    else None,
                    "edit_date": msg.edit_date.strftime("%Y-%m-%d %H:%M:%S")
                    if msg.edit_date
                    else None,
                    "date": msg.date.strftime("%Y-%m-%d %H:%M:%S")
                    if msg.date
                    else None,
                }
                print(data)
                new_instance = PostInitial(**data)
                await sync_to_async(new_instance.save)()
            except:
                print("An exception occurred")

        async def handle_message_edit(event):
            try:
                msg = event.message
                post = await sync_to_async(PostInitial.objects.get)(message_id=msg.id)
                post.edit_date = msg.date.strftime("%Y-%m-%d %H:%M:%S")
                post.message = msg.message
                if msg.reply_to:
                    post.reply_to_msg_id = msg.reply_to.reply_to_msg_id
                else:
                    post.reply_to_msg_id = None

                await sync_to_async(post.save)()
            except:
                print("An exception occurred")

        client.add_event_handler(
            handle_new_message,
            events.NewMessage(chats=[PeerChannel(2101974116), PeerChannel(1566206468)]),
        )
        client.add_event_handler(
            handle_message_edit,
            events.MessageEdited(
                chats=[PeerChannel(2101974116), PeerChannel(1566206468)]
            ),
        )
        await client.run_until_disconnected()
    await client.disconnect()
    return JsonResponse({"posts": []})

    # shouldStop = False
    # while not shouldStop:
    #     print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
    #     history = await client(
    #         GetHistoryRequest(
    #             peer=my_channel,
    #             offset_id=offset_id,
    #             offset_date=None,
    #             # offset_date=start_date,
    #             add_offset=0,
    #             limit=limit,
    #             max_id=0,
    #             min_id=0,
    #             hash=0,
    #         )
    #     )
    #     if not history.messages:
    #         break

    #     messages = history.messages
    #     for message in tqdm(messages):
    #         # to control msg date time
    #         message_date = message.date.replace(tzinfo=timezone.utc)
    #         # end_date = datetime(2023, 10, 19, tzinfo=timezone.utc)
    #         end_date = datetime(2023, 11, 1, tzinfo=timezone.utc)
    #         if message_date < end_date:
    #             shouldStop = True
    #             break
    #         # print(message_date, end_date)

    #         # will download img and save it a folder called "hi"
    #         # client.download_media(message, "./"+"hi"+"/")

    #         # print(message_data['message'] if message_data else None)

    #         all_messages.append(message.to_dict())

    #     offset_id = messages[len(messages) - 1].id
    #     total_messages = len(all_messages)
    #     tt = type(all_messages)
    #     if total_count_limit != 0 and total_messages >= total_count_limit:
    #         break

    await client.disconnect()
    return JsonResponse({"posts": all_messages}, encoder=DateTimeEncoder)
