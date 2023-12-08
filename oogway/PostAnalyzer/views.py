from django.shortcuts import render
from django.http import HttpResponse

from django.http import JsonResponse
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser

api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'

async def get_user_posts(username, limit):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        user = await client.get_entity(username)  # Get user entity
        posts = await client.get_messages(entity=user, limit=limit)  # Retrieve posts

        # Process the posts as needed
        post_texts = [post.text for post in posts]
        return post_texts

def get_user_posts_view(request):
    username = request.GET.get('username')
    limit = int(request.GET.get('limit', 10))

    posts = []

    if username:
        try:
            posts = TelegramClient.loop.run_until_complete(get_user_posts(username, limit))
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'posts': posts})