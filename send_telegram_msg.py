from telegram import Bot
from env import tele_api_key, tele_id
import json


async def send_message(image_path,msg):#need to somehow get the correct image.
    # Initialize your bot with the token
    # print("Executing sending image to yc")
    bot = Bot(tele_api_key)

    # Replace "YOUR_CHAT_ID" with the ID of the chat you want to send the image to
    chat_ids = tele_id
    chat_ids = chat_ids[1:-1].split(',')
    for chat_id in chat_ids:
        # print(f"chat_id is {chat_id}")
        # photo=open(image_path, 'rb')
        # print(photo)
        await bot.send_photo(chat_id=chat_id, photo=open(image_path, 'rb'), caption = msg)