from bingx.api import BingxAPI
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from dotenv import dotenv_values
from PostAnalyzer.models import (
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
from telethon.sync import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import asyncio
from django.db.models import Count,Q
config = dotenv_values(".env")
API_KEY = config["API_KEY"]
SECRET_KEY = config["SECRET_KEY"]
bingx = BingxAPI(API_KEY, SECRET_KEY, timestamp="local")

def get_posts_api(request):
    posts = Post.objects.all()  # Fetch all posts from the database
    data = serializers.serialize("json", posts)

    return JsonResponse(data, safe=False)


def get_symbols_api(request):
    symbols = Symbol.objects.all()  # Fetch all symbols from the database
    data = serializers.serialize("json", symbols)
    print(symbols)
    return JsonResponse(data, safe=False)


@login_required(login_url="login")
def home(request):
    channels = Channel.objects.all()
    predicts = Predict.objects.all()
    
    return render(request, "Home/home.html", {"channels": channels,"predicts": predicts})

def advance_test(request):
    return render(request, "advanced.html")

def charts_test(request):
    return render(request, "chartjs.html")

def validation_test(request):
    return render(request, "validation.html")


class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return "/panel"


# symbols
@login_required(login_url="login")
def get_symbols(request):
    symbols = Symbol.objects.all()
    return render(request, "Symbol/index.html", {"symbols": symbols})


# markets
@login_required(login_url="login")
def get_markets(request):
    markets = Market.objects.all()
    return render(request, "Market/index.html", {"markets": markets})


# predicts
@login_required(login_url="login")
def get_predicts(request):
    predicts = Predict.objects.all()
    symbol_param = request.GET.get("symbol")
    channel_param = request.GET.get("channel")
    
    if symbol_param:
        predicts = predicts.filter(symbol__name=symbol_param)
    if channel_param:
        predicts = predicts.filter(post__channel__channel_id=channel_param)
    
    
    symbols = Symbol.objects.all()
    channels = Channel.objects.all()

    return render(
        request,
        "Predict/index.html",
        {"predicts": predicts, "symbols": symbols, "symbol_param": symbol_param, "channels": channels, "channel_param": channel_param,},
    )


# channels
@login_required(login_url="login")
def channel_list(request):
    channels = Channel.objects.all()
    return render(request, "Channel/channelList.html", {"channels": channels})


# channels
@login_required(login_url="login")
def change_channel_trade(request, channel_id):
    channel = Channel.objects.get(channel_id=channel_id)
    channel.can_trade = not channel.can_trade
    channel.save()
    return redirect("Panel:channel_list")


# channel detail
@login_required(login_url="login")
def channel_detail(request, channel_id):
    channel = get_object_or_404(Channel, channel_id=channel_id)
    return render(request, "Channel/channelDetail.html", {"channel": channel})


# posts list
@login_required(login_url="login")
def post_list(request):
    posts = Post.objects.all().order_by("-id")
    return render(request, "Post/postList.html", {"posts": posts})


# post detail
@login_required(login_url="login")
def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)

    related_posts = Post.objects.filter(reply_to_msg_id=post.message_id)

    predict = None
    entries = None
    take_profits = None
    if post.is_predict_msg:
        predict = Predict.objects.get(post=post)
        entries = EntryTarget.objects.filter(post=post)
        take_profits = TakeProfitTarget.objects.filter(post=post)

    return render(
        request,
        "Post/postDetail.html",
        {
            "post": post,
            "related_posts": related_posts,
            "predict": predict,
            "entries": entries,
            "take_profits": take_profits,
        },
    )


# post detail
@login_required(login_url="login")
def save_coins_from_api(request):
    order_data = bingx.get_all_contracts()

    # for symbol in order_data:
    #     newSymbol = {
    #         "name": symbol["symbol"],
    #         "size": symbol["size"],
    #         "fee_rate": symbol["feeRate"],
    #         "currency": symbol["currency"],
    #         "asset": symbol["asset"],
    #     }
    #     newSymbol = Symbol(**newSymbol)

    #     newSymbol.save()

    data = serializers.serialize("json", order_data)

    return JsonResponse(data, safe=False)


# cancel order
@login_required(login_url="login")
def cancel_order(request, symbol, order_id=None):
    try:
        res = bingx.cancel_order(symbol,order_id, order_id)
        # res = bingx.cancel_all_orders_of_symbol(symbol)
        predict = Predict.objects.get(order_id=order_id)
        cancelStatus = PostStatus.objects.get(name="CANCELED")
        predict.status = cancelStatus
        print(111)
        print(res)
        predict.save()
    except:
        print("error")

    # data = serializers.serialize("json", order_data)

    return redirect("Panel:predict")

# change predict status
@login_required(login_url="login")
def change_predict_status(request, predict_id, status):
    try:
        predict = Predict.objects.get(pk=predict_id)
        newStatus = PostStatus.objects.get(name=status)
        predict.status = newStatus
        predict.save()
    except:
        print("error")

    return redirect("Panel:predict")


# charts
def predict_status_chart(request):
    statuses = PostStatus.objects.all()

    status_dict = dict()

    for status in statuses:
        status_dict[status.name] = 0

    grouped_predictions = (Predict.objects.values('status__name').annotate(prediction_count=Count('id')))

    for group in grouped_predictions:
        status_dict[group['status__name']] = group["prediction_count"]


    predictsGroup = {
        "labels": list(status_dict.keys()),
        "data": list(status_dict.values()),
    }

    return JsonResponse(predictsGroup)

def channel_predict_status_chart(request):
    statuses = PostStatus.objects.all()

    channel_counts = Channel.objects.values('name').annotate(
        **{status.name: Count('post__predict__status', filter=Q(post__predict__status__name=status.name)) for status in statuses}
    )

    # print(channel_counts)

    channel_status_count_dict = {}

    for channel in channel_counts:
        channel_name = channel['name']
        channel_status_count_dict[channel_name] = {
           status.name: channel[status.name] for status in statuses
        }

    # print(list(channel_status_count_dict.keys()))
    # print(list(channel_status_count_dict.values()))

    
    return JsonResponse({
        "labels": list(channel_status_count_dict.keys()),
        "data": list(channel_status_count_dict.values()),
    })


# settings
@login_required(login_url="login")
def get_settings(request):
    setting = SettingConfig.objects.get(id=1)
    return render(request, "Settings/index.html", {"setting": setting})

@login_required(login_url="login")
def update_settings(request):
    settings = SettingConfig.objects.get(id=1)
    max_leverage_param = float(request.POST.get("max_leverage"))
    leverage_effect_param = bool(request.POST.get("leverage_effect"))
    allow_channels_set_order_param = bool(request.POST.get("allow_channels"))
    max_entry_money_param = float(request.POST.get("max_entry_money"))

    settings.max_leverage = max_leverage_param
    settings.leverage_effect = leverage_effect_param
    settings.allow_channels_set_order = allow_channels_set_order_param
    settings.max_entry_money = max_entry_money_param
    settings.save()
    return redirect("Panel:settings")




async def set_phone_number(phone_number,token):
    config = dotenv_values(".env")

    api_id = config["api_id"]
    api_hash = config["api_hash"]

    username = config["username"]
    print(1)
    client = TelegramClient(username, api_id, api_hash)
    print(2)
    # await client.start()
    await client.connect()
    print( client._phone_code_hash)
    print(3)
    # Ensure you're authorized
    if not await client.is_user_authorized():
        print(4)
        if not token:
            await client.send_code_request(phone_number)
            print(phone_number)
            print(5)
        elif token:
            print(6)
            try:
                print(7)
                await client.send_code_request(phone_number)
                await client.sign_in(phone_number,token)
                print(8)
            except SessionPasswordNeededError:
                await client.sign_in(password=input('Password: '))
                
            print(9)
    print(10)
            
    # me = await client.get_me()

@login_required(login_url="login")
def getPhoneNumberAndCode(request):
    phone_number_param = request.POST.get("phone_number")
    token_param = request.POST.get("token")
    
    if phone_number_param:
        print(11)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(set_phone_number(phone_number_param,token_param))
    return render(request, "test.html", {"phone_number": phone_number_param})