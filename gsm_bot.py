import os
import logging
import openai
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GSMAssistantBot")

SYSTEM_PROMPT = "You are a helpful assistant."
MODEL = "gpt-4o"
TEMPERATURE = 0.7

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm your AI assistant. Ask me anything!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.message.from_user.id
    logger.info(f"Received from {user_id}: {user_text}")

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        response = await openai.ChatCompletion.acreate(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=TEMPERATURE
        )
        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        await update.message.reply_text("⚠️ Sorry, I couldn't process that. Try again later.")

def main():
    if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
        raise ValueError("Missing TELEGRAM_TOKEN or OPENAI_API_KEY.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 GSM Assistant Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
