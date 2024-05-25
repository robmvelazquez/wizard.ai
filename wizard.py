import os
import asyncio
from openai import AsyncOpenAI
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()

# Set your API keys
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY")
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define the bot username as a constant
BOT_USERNAME = '@Eldric'

# Define the roleplay function with AI integration
async def generate_response(user_input):
    try:
        chat_completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Eldric, a wise and friendly wizard who loves sharing knowledge about magic and the world. You speak in a formal and articulate manner with a touch of magical flair."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.0
        )
        print(chat_completion.choices[0].message.content)
        response_content = chat_completion.choices[0].message.content.strip()
        logger.info(f"OpenAI response: {response_content}")
        return response_content
    except Exception as e:
        logger.error(f"Error generating the response from OpenAI")
        return None
    except AsyncOpenAI.error.OpenAIError as e:
        logger.error(f"Unexpected error: {e}")
        return None

async def roleplay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    logger.info(f"Received message: {user_input}")
    try:
        response = await generate_response(user_input)
        if not response:
            response = "I'm sorry, I couldn't generate a response. Please try again."
        logger.info(f"Generated response: {response}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while generating a response. Please try again later.")

# Define the start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = f"Welcome to the AI-powered roleplay bot! My name is {BOT_USERNAME}."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

# Initialize the application
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Add handlers
start_handler = CommandHandler('start', start)
app.add_handler(start_handler)

roleplay_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), roleplay)
app.add_handler(roleplay_handler)

# Run the bot
if __name__ == '__main__':
    import asyncio
    import sys

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app.run_polling()