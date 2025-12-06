# api/webhook.py
import os
import logging
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I'm a simple echo bot. Send me any text!",
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echoes the user's message."""
    await update.message.reply_text(update.message.text)

# --- Global Application Instance ---
# Initialize the Application once globally to avoid re-creating it on every request.
# This is crucial for serverless functions.
# The bot token is fetched from an environment variable.
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE') 
# Using your provided token directly for now, but strongly recommend using environment variables.
if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or not BOT_TOKEN:
    logger.error("Bot token not found. Please set the TELEGRAM_BOT_TOKEN environment variable.")
    # In a real scenario, you might want to raise an exception or handle this more robustly.
    # For Vercel, if the token is missing, the bot won't work, but the function will deploy.

application = Application.builder().token(BOT_TOKEN).build()

# Register command handlers
application.add_handler(CommandHandler("start", start))

# Register message handlers
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- Vercel Serverless Function Handler ---
async def handler(request):
    """
    Vercel serverless function handler for Telegram webhooks.
    This function will be called by Vercel when Telegram sends an update.
    """
    if request.method == "POST":
        try:
            # Vercel's Python runtime provides the request body as JSON via request.json
            update_json = await request.json()

            if not update_json:
                logger.warning("Received empty JSON body from Telegram webhook.")
                return {"statusCode": 400, "body": "Bad Request: Empty JSON"}

            # Create an Update object from the JSON payload
            update = Update.de_json(update_json, application.bot)
            
            # Process the update
            await application.process_update(update)

            # Telegram expects a 200 OK response quickly
            return {"statusCode": 200, "body": "OK"}

        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            return {"statusCode": 500, "body": f"Internal Server Error: {e}"}
    else:
        # Handle GET requests (e.g., for testing the endpoint directly)
        return {"statusCode": 200, "body": "This is a Telegram bot webhook endpoint. Send POST requests."}
