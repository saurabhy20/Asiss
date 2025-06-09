import os
import logging
from telegram import Update, Chat, ChatMemberUpdated
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ContextTypes
)
import openai

TELEGRAM_TOKEN = os.getenv("7639863811:AAFpYst7CZ0i5xOQDjviV2PUbz7KnyPXjtQ")
OPENAI_API_KEY = os.getenv("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")
openai.api_key = OPENAI_API_KEY

MODEL = "gpt-4o"
TEMPERATURE = 0.7
SYSTEM_PROMPT = "You are a smart assistant that helps everyone in the group chat."
MAX_HISTORY = 10

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GroupChatBot")

chat_histories = {}

def get_history(chat_id):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return chat_histories[chat_id]

def update_history(chat_id, role, content):
    history = get_history(chat_id)
    history.append({"role": role, "content": content})
    if len(history) > MAX_HISTORY + 1:
        chat_histories[chat_id] = [history[0]] + history[-MAX_HISTORY:]

def is_bot_mentioned(message, bot_username):
    if message.text:
        return bot_username in message.text or message.chat.type == Chat.PRIVATE
    return False

async def generate_response(history):
    try:
        response = await openai.ChatCompletion.acreate(
            model=MODEL,
            messages=history,
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "⚠️ I'm having trouble thinking right now. Try again later."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat = message.chat
    text = message.text.strip()
    bot_username = context.bot.username

    if not is_bot_mentioned(message, bot_username):
        return

    logger.info(f"Message from {chat.id}: {text}")

    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
    update_history(chat.id, "user", text)
    reply = await generate_response(get_history(chat.id))
    update_history(chat.id, "assistant", reply)
    await message.reply_text(reply)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm your group assistant bot. Mention me and I'll reply!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mention me in any group message and I'll respond using AI ✨")

async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.username == context.bot.username:
            await update.message.reply_text("👋 Thanks for adding me! Mention me in your messages and I'll chat with you.")

def main():
    if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
        raise ValueError("Missing TELEGRAM_TOKEN or OPENAI_API_KEY environment variables.")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Group Chatbot Assistant running...")
    application.run_polling()

if __name__ == "__main__":
    main()
