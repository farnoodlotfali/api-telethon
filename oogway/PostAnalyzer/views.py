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
from .models import (
    PostInitial,
    Post,
    Symbol,
    Market,
    EntryTarget,
    Predict,
    TakeProfitTarget,
    PostStatus,
)
from asgiref.sync import sync_to_async
import requests
import re


config = dotenv_values("../.env")

api_id = config["api_id"]
api_hash = config["api_hash"]

username = config["username"]


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        if isinstance(o, str):
            return o  # Return Persian text as is without encoding

        return json.JSONEncoder.default(self, o)


def test(request):
    test = EntryTarget.objects.get(post_id__message_id=191, index=0)
    print(test)
    return render(request, "test.html", {"test": test})


def get_posts_view(request):
    posts = PostInitial.objects.all().order_by("-id")

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
    async with TelegramClient(username, api_id, api_hash) as client:

        async def handle_new_message(event):
            # try:
            await options[event.message.peer_id.channel_id](event.message)

            # except:
            #     print("An exception occurred")

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
            events.NewMessage(
                chats=[
                    PeerChannel(int(config["CHANNEL_TEST"])),
                    PeerChannel(int(config["CHANNEL_FEYZ"])),
                    PeerChannel(int(config["CHANNEL_TEST_2"])),
                ]
            ),
        )
        client.add_event_handler(
            handle_message_edit,
            events.MessageEdited(
                chats=[
                    PeerChannel(int(config["CHANNEL_TEST"])),
                    PeerChannel(int(config["CHANNEL_FEYZ"])),
                    PeerChannel(int(config["CHANNEL_TEST_2"])),
                ]
            ),
        )
        await client.run_until_disconnected()
    # await client.disconnect()
    # return JsonResponse({"posts": []})


async def channelTest(msg):
    p1 = FeyzianMsg()
    predict = await p1.extract_data_from_message(msg)


def channelTest2(msg):
    print(msg)


def returnSearchValue(val):
    return val.group(1) if val else None


class FeyzianMsg:
    # determine if a message is a predict message or not
    def isPredictMsg(self, msg):
        patterns = [
            r"Symbol: (.+)",
            # r"Position: (.+)",
            # r"Leverage: (.+)",
            r"Market: (.+)",
            r"StopLoss: (.+)",
        ]

        return all(re.search(pattern, msg) for pattern in patterns)

    # check if post is a Entry point or not
    async def isEntry(self, PostData):
        entry_price = returnSearchValue(
            re.search(r"Entry Price: (.+)", PostData.message)
        )

        entry_index = returnSearchValue(re.search(r"Entry(.+)", PostData.message))

        if entry_index:
            # find number
            entry_index = re.search(
                r"\d+",
            )
            if entry_index:
                entry_index = int(entry_index.group()) - 1
            else:
                return False
        else:
            return False

        patterns = [r"Entry(.+)", r"Price:(.+)", r"Entry Price: (.+)"]
        check = all(re.search(pattern, PostData.message) for pattern in patterns)

        # for control "average entry".
        # sometimes entry_price is different to value. so we should find difference, then calculate error
        if entry_price and check:
            entry_price_value = float(re.findall(r"\d+\.\d+", entry_price)[0])

            entry_target = await sync_to_async(EntryTarget.objects.get)(
                post__message_id=PostData.reply_to_msg_id, index=entry_index
            )

            if entry_target:
                bigger_number = max(entry_price_value, float(entry_target.value))
                smaller_number = min(entry_price_value, float(entry_target.value))

                error = (100 * (1 - (smaller_number / bigger_number))) > 1
                if error:
                    return False
                else:
                    entry_target.active = True
                    entry_target.date = PostData.date
                    # entry_target.date = period
                    await sync_to_async(entry_target.save)()
                    return True

        return False

    # check if str(msg) is a Stoploss point or not
    def isStopLoss(self, msg):
        if "Stoploss".lower() in msg.lower() or "Stop loss".lower() in msg.lower():
            return True
        else:
            return False

    # check if post is a Take-Profit point or not
    async def isTakeProfit(self, PostData):
        tp_index = returnSearchValue(
            re.search(r"Take-Profit target(.+)", PostData.message)
        )
        if tp_index:
            tp_index = re.search(r"\d+", tp_index)
            if tp_index:
                tp_index = int(tp_index.group()) - 1
            else:
                return False
        else:
            return False

        patterns = [
            r"Take-Profit(.+)",
            r"Profit(.+)",
            r"Period(.+)",
        ]

        # Check if all patterns have a value
        check = all(re.search(pattern, PostData.message) for pattern in patterns)

        if check:
            tp_target = await sync_to_async(TakeProfitTarget.objects.get)(
                post__message_id=PostData.reply_to_msg_id, index=tp_index
            )

            if tp_target:
                tp_target.active = True
                tp_target.date = PostData.date
                tp_target.period = returnSearchValue(
                    re.search(r"Period: (.+)", PostData.message)
                )
                await sync_to_async(tp_target.save)()
                return True

        return False

    # find important parts of a predict message such as symbol or entry point
    async def predictParts(self, string, post):
        if string is None or post is None:
            return None

        # symbol
        symbol_match = re.search(r"Symbol: #(.+)", string)
        symbol_value, symbol_created = await sync_to_async(
            Symbol.objects.get_or_create
        )(name=returnSearchValue(symbol_match).strip())
        #  market
        market_match = re.search(r"Market: (.+)", string)
        market_value, market_created = await sync_to_async(
            Market.objects.get_or_create
        )(name=returnSearchValue(market_match).strip().upper())

        status_value = await sync_to_async(PostStatus.objects.get)(name="PENDING")

        # position
        position_match = re.search(r"Position: (.+)", string)
        leverage_match = re.search(r"Leverage: (.+)", string)
        stopLoss_match = re.search(r"StopLoss: (.+)", string)

        # entry targets
        entry_targets_match = re.search(r"Entry Targets:(.+?)\n\n", string, re.DOTALL)
        entry_values = (
            re.findall(r"\d+\.\d+", entry_targets_match.group(1))
            if entry_targets_match
            else None
        )

        # take_profit targets
        take_profit_targets_match = re.search(
            r"Take-Profit Targets:(.+?)\n\n", string, re.DOTALL
        )
        profit_values = (
            re.findall(r"\d+\.\d+", take_profit_targets_match.group(1))
            if take_profit_targets_match
            else None
        )

        PredictData = {
            "post": post,
            "symbol": symbol_value,
            "position": returnSearchValue(position_match),
            "market": market_value,
            "leverage": returnSearchValue(leverage_match),
            "stopLoss": returnSearchValue(stopLoss_match),
            "status": status_value,  # PENDING = 1
        }
        newPredict = Predict(**PredictData)

        await sync_to_async(newPredict.save)()

        if entry_values:
            for i, value in enumerate(entry_values):
                entryData = EntryTarget(
                    **{
                        "post": post,
                        "index": i,
                        "value": value,
                        "active": False,
                        "period": None,
                        "date": None,
                    }
                )
                await sync_to_async(entryData.save)()

        if profit_values:
            for i, value in enumerate(profit_values):
                takeProfitData = TakeProfitTarget(
                    **{
                        "post": post,
                        "index": i,
                        "value": value,
                        "active": False,
                        "period": None,
                        "date": None,
                    }
                )
                await sync_to_async(takeProfitData.save)()

        return PredictData

    async def extract_data_from_message(self, message):
        if isinstance(message, Message):
            is_predict_msg = self.isPredictMsg(message.message)
            PostData = {
                "channel_id": message.peer_id.channel_id,
                "date": message.date,
                "message_id": message.id,
                "message": message.message,
                "reply_to_msg_id": message.reply_to.reply_to_msg_id
                if message.reply_to
                else None,
                "edit_date": message.edit_date,
                "is_predict_msg": is_predict_msg,
            }
            post = Post(**PostData)

            await sync_to_async(post.save)()
            # predict msg
            if is_predict_msg:
                await self.predictParts(message.message, post)
                # entry msg
            elif await self.isEntry(post):
                pass
                # take profit msg
            elif await self.isTakeProfit(post):
                pass

            return PostData
        else:
            return None


options = {
    int(config["CHANNEL_TEST"]): channelTest,
    int(config["CHANNEL_TEST_2"]): channelTest2,
}
