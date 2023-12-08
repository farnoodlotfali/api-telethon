from telethon.sync import TelegramClient, events
from dotenv import dotenv_values
from telethon.tl.types import Message, PeerChannel
config = dotenv_values(".env")

api_id = config["api_id"]
api_hash = config["api_hash"]

username = config["username"]

client = TelegramClient(username, api_id, api_hash).start()
peer_channel = PeerChannel(2101974116)
events.MessageEdited
peer_channel1 = PeerChannel(1566206468)
@client.on(events.NewMessage(chats=[peer_channel,peer_channel1]))
async def handle_new_message(event):
    # Handle the new message here
    print(event.message)

with client:
    client.run_until_disconnected()


# @client.on(events.MessageEdited(chats=peer_channel))
# async def handle_message_edit(event):
#     # Handle the edited message here
#     print('Message edited:', event.message)

# with client:
#     client.run_until_disconnected()

# with TelegramClient(username, api_id, api_hash) as client:
#     client.send_message("me", "Hello, myself!")
#     print(client.download_profile_photo("me"))

#     @client.on(events.NewMessage(pattern="(?i).*Hello"))
#     async def handler(event):
#         await event.reply("Hey!")

#     client.run_until_disconnected()
