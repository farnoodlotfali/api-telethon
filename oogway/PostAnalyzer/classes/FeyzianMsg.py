import re

import requests
from asgiref.sync import sync_to_async
from telethon.tl.types import Message

from ..models import (
    Channel,
    EntryTarget,
    Market,
    Post,
    PostStatus,
    Predict,
    Symbol,
    TakeProfitTarget,
    SettingConfig
)
from ..Utility.utils import returnSearchValue,sizeAmount
from .BingXApiClass import BingXApiClass

# ****************************************************************************************************************************


class FeyzianMsg:
    bingx = BingXApiClass()

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
            entry_index = re.search(r"\d+", entry_index)
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

    # check if post is a Stoploss point or not
    async def isStopLoss(self, post):
        if post is None or post.reply_to_msg_id is None:
            return False
        if (
            "Stoploss".lower() in post.message.lower()
            or "Stop loss".lower() in post.message.lower()
        ):
            status_value = await sync_to_async(PostStatus.objects.get)(name="FAILED")
            predict_value = await sync_to_async(Predict.objects.get)(
                post__message_id=post.reply_to_msg_id
            )

            predict_value.status = status_value
            await sync_to_async(predict_value.save)()
            return True
        else:
            return False

    # check if post is a AllProfit point or not
    async def isAllProfitReached(self, post):
        if post is None or post.reply_to_msg_id is None:
            return False
        if (
            "all take-profit target".lower() in post.message.lower()
            or "all take profit target".lower() in post.message.lower()
        ):
            status_value = await sync_to_async(PostStatus.objects.get)(name="SUCCESS")
            predict_value = await sync_to_async(Predict.objects.get)(
                post__message_id=post.reply_to_msg_id
            )

            predict_value.status = status_value
            await sync_to_async(predict_value.save)()
            return True
        else:
            return False

    # check if post is a Take-Profit point or not
    async def isTakeProfit(self, PostData):
        if PostData is None or PostData.reply_to_msg_id is None:
            return None
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
        
        settings = await sync_to_async(SettingConfig.objects.get)(id=1)

        # symbol
        symbol_match = re.search(r"Symbol: #(.+)", string)
        symbol_match = (
            returnSearchValue(symbol_match).strip().split("USDT")[0].replace("/", "")
        )
        symbol_value = await sync_to_async(Symbol.objects.get)(asset=symbol_match)

        #  market
        market_match = re.search(r"Market: (.+)", string)
        market_value, market_created = await sync_to_async(
            Market.objects.get_or_create
        )(name=returnSearchValue(market_match).strip().upper())
        isSpot = market_value.name == "SPOT"

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
            "position": "Buy" if isSpot else returnSearchValue(position_match),
            "market": market_value,
            "leverage": returnSearchValue(leverage_match),
            "stopLoss": returnSearchValue(stopLoss_match),
            "status": status_value,  # PENDING = 1
            "order_id": None,
        }
        newPredict = Predict(**PredictData)

        first_entry_value = None
        if entry_values:
            for i, value in enumerate(entry_values):
                if i == 0:
                    first_entry_value = value
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

        first_tp_value = None
        if profit_values:
            for i, value in enumerate(profit_values):
                if i == 0:
                    first_tp_value = value

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

        if post.channel.can_trade and settings.allow_channels_set_order:
            # set order in BingX
            max_entry_money = settings.max_entry_money

            crypto = newPredict.symbol.name
            leverage = re.findall(r"\d+", newPredict.leverage)[0]
            pos = newPredict.position
            margin_mode = self.bingx.set_margin_mode(crypto, "ISOLATED")
            set_levarage = self.bingx.set_levarage(crypto, pos, 1)
            # set_levarage = self.bingx.set_levarage(crypto, pos, leverage)

            # 1- size = float(newPredict.symbol.size) * settings.size_times_by
            # 2- size = float(newPredict.symbol.size) 
            # 3-
            size = max_entry_money / float(first_entry_value)
            
            order_data = await self.open_trade(
                crypto,
                pos,
                first_entry_value,
                size,
                sl=newPredict.stopLoss,
                tp=first_tp_value,
            )
            newPredict.order_id = order_data["orderId"]

        await sync_to_async(newPredict.save)()
        return newPredict
    
    async def open_trade(self, pair, position_side, price, volume, sl, tp):
        print(price, volume, "tp: ",tp,"sl: ", sl, position_side)
        order_data = self.bingx.open_limit_order(
            pair,
            position_side,
            price,
            volume,
            sl,
            tp,
        )

        return order_data

    async def extract_data_from_message(self, message):
        if isinstance(message, Message):
            is_predict_msg = self.isPredictMsg(message.message)
            channel = await sync_to_async(Channel.objects.get)(
                channel_id=message.peer_id.channel_id
            )
            PostData = {
                "channel": channel if channel else None,
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
                # stop loss msg
            elif await self.isStopLoss(post):
                pass
            # All Profit msg
            elif await self.isAllProfitReached(post):
                pass

            return PostData
        else:
            return None
