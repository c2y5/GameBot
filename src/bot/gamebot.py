# type: ignore

from telegram import Update
from telegram.ext import ContextTypes
from src.game.wordle import WordleGame
from src.game.wordchain import WordChainGame
from src.game.hangman import HangmanGame
from src.game.unscramble_word import UnscrambleGame
from src.game.memory import MemoryGame
from src.game.mathgame import MathGame

class GameBot:
    def __init__(self):
        self.games = {
            "Wordle": None,
            "WordChain": None,
            "Hangman": None,
            "Unscramble": None,
            "Memory": None,
            "MathGame": None
        }
        self.current_game = None
        self.words = self.load_words("english-words.txt")
        self.common_words = self.load_words("common-words.txt")

    def load_words(self, filename):
        with open(filename, "r") as file:
            return {line.strip().lower() for line in file.readlines()}

    async def start_game(self, game_name, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if game_name == "Wordle":
            self.games["Wordle"] = WordleGame()
            self.current_game = self.games["Wordle"]
            await self.current_game.start_game(update, context)
        elif game_name == "WordChain":
            if self.games["WordChain"] is None:
                self.games["WordChain"] = WordChainGame(self.words)

            self.current_game = self.games["WordChain"]
            await self.current_game.start_game(update, context)
        elif game_name == "Hangman":
            if self.games["Hangman"] is None:
                self.games["Hangman"] = HangmanGame(list(self.common_words))

            self.current_game = self.games["Hangman"]
            await self.current_game.start_game(update, context)
        elif game_name == "Unscramble Word":
            if self.games["Unscramble"] is None:
                self.games["Unscramble"] = UnscrambleGame(list(self.common_words))

            self.current_game = self.games["Unscramble"]
            await self.current_game.start_game(update, context)
        elif game_name == "Memory Game":
            if self.games["Memory"] is None:
                self.games["Memory"] = MemoryGame()

            self.current_game = self.games["Memory"]
            await self.current_game.start_game(update, context)
        elif game_name == "Math Game":
            if self.games["MathGame"] is None:
                self.games["MathGame"] = MathGame()

            self.current_game = self.games["MathGame"]
            await self.current_game.start_game(update, context)
        else:
            reply_text = f"Sorry, the game {game_name} is not available."
            if update.message is not None:
                await update.message.reply_text(reply_text)
            elif update.callback_query is not None:
                await update.callback_query.message.reply_text(reply_text)

    async def handle_guess(self, update, context):
        if self.current_game is None and "current_game" not in context.user_data:
            await update.message.reply_text("Please start a game first with /play.")
            return

        game = self.current_game or context.user_data.get("current_game")
        
        if game is None:
            await update.message.reply_text("Please start a game first with /play.")
            return

        try:
            if isinstance(game, WordleGame):
                response = game.handle_guess(update, context)
            elif isinstance(game, WordChainGame):
                response = game.handle_guess(update, context)
            elif isinstance(game, HangmanGame):
                response = game.handle_guess(update, context)
            elif isinstance(game, UnscrambleGame):
                response = await game.handle_guess(update, context)
            elif isinstance(game, MemoryGame):
                await game.handle_click(update, context)
                return
            elif isinstance(game, MathGame):
                response = await game.handle_guess(update, context)
            else:
                response = "Unknown game type. Please start a new game."

            if response:
                if update.message is not None:
                    await update.message.reply_text(response)
                elif update.callback_query is not None:
                    await update.callback_query.message.reply_text(response)

        except Exception as e:
            print(f"Error handling guess: {e}")
            await update.message.reply_text("An error occurred. Please try again.")

        if hasattr(game, "game_over") and game.game_over:
            self.current_game = None
            if "current_game" in context.user_data:
                del context.user_data["current_game"]
            game_over_message = "Game over! Type /play to start again."
            if update.message is not None:
                await update.message.reply_text(game_over_message)
            elif update.callback_query is not None:
                await update.callback_query.message.reply_text(game_over_message)
