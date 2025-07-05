# type: ignore

import os
import random
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def load_word_list():
    with open("word-list.json", "r") as file:
        return json.load(file)

def load_valid_words():
    with open("valid-words.json", "r") as file:
        return json.load(file)

class Game:
    def __init__(self, name):
        self.name = name

    async def start_game(self, update, context):
        raise NotImplementedError("This method should be overridden by a mini-game class")

    def handle_guess(self, update, context):
        raise NotImplementedError("This method should be overridden by a mini-game class")

    def get_feedback(self):
        raise NotImplementedError("This method should be overridden by a mini-game class")

class WordleGame(Game):
    def __init__(self):
        super().__init__("Wordle")
        self.target_word = random.choice(load_word_list()).lower()
        self.attempts = 6
        self.valid_words = load_valid_words()
    
    async def start_game(self, update, context):
        self.attempts = 6
        self.target_word = random.choice(load_word_list()).lower()

        context.user_data["current_game"] = self

        if hasattr(update, "callback_query"):
            await update.callback_query.message.reply_text("New Wordle game started! Guess a 5-letter word:")
        else:
            await update.message.reply_text("New Wordle game started! Guess a 5-letter word:")

    def handle_guess(self, update, context):
        guessed_word = update.message.text.strip().lower()

        if len(guessed_word) != 5:
            return "Your guess must be a 5-letter word."
        
        if guessed_word not in self.valid_words:
            return "This is not a valid word. Please guess a valid 5-letter word."

        if guessed_word == self.target_word:
            return f"Congrats! You guessed the word: {self.target_word}. You win!"
        
        feedback = self.get_feedback(guessed_word)
        self.attempts -= 1
        if self.attempts == 0:
            return f"Game over! The word was: {self.target_word}. Better luck next time!"
        
        return feedback

    def get_feedback(self, guessed_word):
        feedback = [""] * 5
        target_word_copy = list(self.target_word)
        
        for i, char in enumerate(guessed_word):
            if char == self.target_word[i]:
                feedback[i] = "🟩"
                target_word_copy[i] = None
        
        for i, char in enumerate(guessed_word):
            if feedback[i] == "":
                if char in target_word_copy and char != None:
                    feedback[i] = "🟨"
                    target_word_copy[target_word_copy.index(char)] = None
        
        for i, char in enumerate(guessed_word):
            if feedback[i] == "":
                feedback[i] = "🟥"
        
        return " ".join(feedback) + f" [{self.attempts-1} attempts left]"

class GameBot:
    def __init__(self):
        self.games = {
            "Wordle": WordleGame()
        }
        self.current_game = None

    async def start_game(self, game_name, update, context):
        if game_name in self.games:
            self.current_game = self.games[game_name]
            await self.current_game.start_game(update, context)
        else:
            await update.message.reply_text(f"Sorry, the game {game_name} is not available.")

    async def handle_guess(self, update, context):
        if "current_game" not in context.user_data:
            await update.message.reply_text("Please start a game first with /play.")
            return

        game = context.user_data["current_game"]
        response = game.handle_guess(update, context)
        await update.message.reply_text(response)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to GameBot! Type /play to choose a game. You can also type /stop to end your current game.")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Wordle", callback_data="play_wordle")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a game to play:", reply_markup=reply_markup)

async def game_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    gamebot = GameBot()

    if query.data == "play_wordle":
        await query.message.reply_text("Type /stop to end your current game.")
        await gamebot.start_game("Wordle", update, context)
    
    await query.answer()

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gamebot = GameBot()
    await gamebot.handle_guess(update, context)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "current_game" in context.user_data:
        del context.user_data["current_game"]
    await update.message.reply_text("Your game has been stopped.")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("stop", stop))

    application.add_handler(CallbackQueryHandler(game_choice))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))

    application.run_polling()

if __name__ == "__main__":
    main()
