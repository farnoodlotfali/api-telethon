from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from PostAnalyzer.models import (
    Channel,
    EntryTarget,
    Market,
    Post,
    Predict,
    Symbol,
    TakeProfitTarget,
)


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
    return render(request, "Home/home.html")


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
    predicts = []
    symbol_param = request.GET.get("symbol")
    if symbol_param:
        predicts = Predict.objects.filter(symbol__name=symbol_param)
    else:
        predicts = Predict.objects.all()

    symbols = Symbol.objects.all()

    return render(
        request,
        "Predict/index.html",
        {"predicts": predicts, "symbols": symbols, "symbol_param": symbol_param},
    )


# channels
@login_required(login_url="login")
def channel_list(request):
    channels = Channel.objects.all()
    return render(request, "Channel/channelList.html", {"channels": channels})


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
