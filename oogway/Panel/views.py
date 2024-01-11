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
)
from django.db.models import Count
config = dotenv_values("../.env")
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

    grouped_predictions = (Predict.objects.values('status__name').annotate(prediction_count=Count('id')))
   
    predictsGroup = {f"{group['status__name']}": group['prediction_count'] for group in grouped_predictions}
    print(predictsGroup)
    return render(request, "Home/home.html", {"channels": channels,"predicts": predicts,"predictsGroup":predictsGroup})

def advance_test(request):
    print(12121)
    return render(request, "advanced.html")


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
        bingx.cancel_order(symbol, order_id)
        predict = Predict.objects.get(order_id=order_id)
        cancelStatus = PostStatus.objects.get(name="CANCELED")
        predict.status = cancelStatus
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
