import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I'm a simple echo bot. Send me any text!",
    )

# --- Message Handlers ---

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echoes the user's message."""
    await update.message.reply_text(update.message.text)

# --- Error Handler ---

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a traceback to the console."""
    logger.error("Exception while handling an update:", exc_info=context.error)

def main() -> None:
    """Start the bot."""
    # Get the bot token from environment variables
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') 
    
    if not BOT_TOKEN:
        logger.error("Bot token not found. Please set the TELEGRAM_BOT_TOKEN environment variable in Render.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))

    # Register message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot started polling...")

if __name__ == '__main__':
    main()
