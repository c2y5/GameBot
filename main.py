# type: ignore

import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from src.bot.gamebot import GameBot

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to GameBot! Type /play to choose a game. You can also type /stop to end your current game.")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Wordle", callback_data="play_wordle")],
        [InlineKeyboardButton("WordChain", callback_data="play_wordchain")],
        [InlineKeyboardButton("Hangman", callback_data="play_hangman")],
        [InlineKeyboardButton("Unscramble Word", callback_data="play_unscramble")],
        [InlineKeyboardButton("Memory Game", callback_data="play_memorygame")],
        [InlineKeyboardButton("Math Game", callback_data="play_mathgame")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a game to play:", reply_markup=reply_markup)

async def game_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    gamebot = GameBot()
    context.user_data["gamebot"] = gamebot

    if query.data == "play_wordle":
        await query.message.reply_text("Type /stop to end your current game.")
        await gamebot.start_game("Wordle", update, context)
    elif query.data == "play_wordchain":
        await query.message.reply_text("Type /stop to end your current game.")
        await gamebot.start_game("WordChain", update, context)
    elif query.data == "play_hangman":
        await query.message.reply_text("Type /stop to end your current game.")
        await gamebot.start_game("Hangman", update, context)
    elif query.data == "play_unscramble":
        await query.message.reply_text("Type /stop to end your current game.")
        await gamebot.start_game("Unscramble Word", update, context)
    elif query.data == "play_memorygame":
        await query.message.reply_text("Type /stop to end your current game.")
        await gamebot.start_game("Memory Game", update, context)
    elif query.data == "play_mathgame":
        await query.message.reply_text("Type /stop to end your current game.")
        await gamebot.start_game("Math Game", update, context)

    await query.answer()

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    gamebot = context.user_data.get("gamebot")
    if not gamebot:
        await query.message.reply_text("No active game! Start a new game with /play.")
        return
    
    await gamebot.handle_guess(update, context)

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gamebot = context.user_data.get("gamebot")
    
    if not gamebot:
        await update.message.reply_text("No active game! Start a new game with /play.")
        return
    
    try:
        await gamebot.handle_guess(update, context)
    except Exception as e:
        print(f"Error handling guess: {str(e)}")
        await update.message.reply_text("An error occurred while processing your guess. Please try again.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "current_game" in context.user_data:
        del context.user_data["current_game"]
    if "gamebot" in context.user_data:
        del context.user_data["gamebot"]
    await update.message.reply_text("Your game has been stopped.")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("stop", stop))

    application.add_handler(CallbackQueryHandler(game_choice, pattern="^play_"))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))
    application.run_polling()

if __name__ == "__main__":
    main()