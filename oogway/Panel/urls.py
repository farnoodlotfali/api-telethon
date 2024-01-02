from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "Panel"

urlpatterns = [
    path(
        "login/",
        views.CustomLoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("channels/", views.channel_list, name="channel_list"),
    path("channels/<int:channel_id>/", views.channel_detail, name="channel_detail"),
    path("posts/", views.post_list, name="post_list"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("", views.home, name="home"),
    path("symbol/", views.get_symbols, name="symbol"),
    path("predict/", views.get_predicts, name="predict"),
    path("market/", views.get_markets, name="market"),
    path("save-coins/", views.save_coins_from_api, name="save_coins_from_api"),
    path("change-channel-trade/<int:channel_id>", views.change_channel_trade, name="change_channel_trade"),
    # api
    path("get-posts-api/", views.get_posts_api, name="get_posts_api"),
    path("get-symbol-api/", views.get_symbols_api, name="get_symbols_api"),
    path(
        "cancel-order-api/<str:symbol>/<int:order_id>/",
        views.cancel_order,
        name="cancel_order",
    ),
]
