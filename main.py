import os
import telebot
import requests
import json
import html
import io
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv

load_dotenv()

# Telegram bot token
TOKEN = os.getenv('API_KEY')

# Wikipedia API endpoint for fetching a random page
WIKI_API_ENDPOINT = "https://en.wikipedia.org/api/rest_v1/page/random/summary"

# Default image URL
DEFAULT_IMAGE_URL = "https://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50?f=y"

# Create a TeleBot instance
bot = telebot.TeleBot(TOKEN)

# Fetch a random Wikipedia article and its summary
def fetch_random_wiki_article():
    response = requests.get(WIKI_API_ENDPOINT)
    if response.status_code == 200:
        article_data = json.loads(response.content.decode("utf-8"))
        return (article_data["title"], article_data["extract"], article_data["thumbnail"])
    return None

# Handle the /random command
@bot.message_handler(commands=['random'])
def send_random_wiki_article(message):
    article = fetch_random_wiki_article()
    if article:
        title = article[0]
        summary = article[1]
        thumbnail = article[2]

        # Escape special characters in the title using HTML escape
        escaped_title = html.escape(title)

        caption = f"<b>{escaped_title}</b>\n\n{summary}"

        if thumbnail:
            # Get the thumbnail image data
            image_data = requests.get(thumbnail["source"]).content

            # Create a BytesIO object and write the image data
            image_stream = io.BytesIO(image_data)
            image_stream.seek(0)

            try:
                # Open the image using PIL to check the format
                image = Image.open(image_stream)
                image_format = image.format

                # Check if the format is supported
                if image_format in ["JPEG", "PNG"]:
                    # Send the image with the caption
                    bot.send_photo(chat_id=message.chat.id, photo=image_stream, caption=caption, parse_mode="HTML")
                else:
                    raise ValueError("Unsupported image format")

            except UnidentifiedImageError:
                # Handle the UnidentifiedImageError here
                print("Error: Unidentified image format")
                send_default_image(message.chat.id, caption)

            except Exception as e:
                # Handle other exceptions here
                print(f"Error: {e}")
                send_default_image(message.chat.id, caption)

        else:
            bot.send_message(chat_id=message.chat.id, text=caption, parse_mode="HTML")

# Function to send a default image with the caption
def send_default_image(chat_id, caption):
    # Send the default image with the caption
    bot.send_photo(chat_id=chat_id, photo=DEFAULT_IMAGE_URL, caption=caption, parse_mode="HTML")

# Start the bot
bot.polling()
