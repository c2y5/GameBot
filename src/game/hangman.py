import random
from telegram import Update
from telegram.ext import ContextTypes

class HangmanGame:
    def __init__(self, words):
        self.words = words
        self.secret_word = ""
        self.guessed_letters = set()
        self.wrong_guesses = set()
        self.remaining_attempts = 6
        self.game_over = False
        self.hangman_stages = [
            """
            -----
            |   |
                |
                |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
                |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
            |   |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
           /|   |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
           /|\\  |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
           /|\\  |
           /    |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
           /|\\  |
           / \\  |
                |
            ========
            """
        ]

    async def start_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.secret_word = random.choice(self.words).lower()
        self.guessed_letters = set()
        self.wrong_guesses = set()
        self.remaining_attempts = 6
        self.game_over = False

        context.user_data["current_game"] = self
        
        welcome_msg = (
            "🎮 *Hangman Started!*\n"
            f"Word: {self._get_display_word()}\n"
            f"{self._get_hangman_display()}\n"
            "Guess a letter or the whole word:"
        )
        
        await self._send_message(update, welcome_msg)

    def _get_display_word(self):
        return " ".join(
            letter if letter in self.guessed_letters else "▯" 
            for letter in self.secret_word
        )

    def _get_hangman_display(self):
        stage = 6 - self.remaining_attempts
        return f"```{self.hangman_stages[stage]}```"

    async def _send_message(self, update, text):
        if update.message:
            await update.message.reply_text(text, parse_mode="Markdown")
        elif update.callback_query:
            await update.callback_query.message.reply_text(text, parse_mode="Markdown")

    async def handle_guess(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        guess = update.message.text.strip().lower()
        
        if not guess.isalpha():
            await self._send_message(update, "❌ Please enter only letters!")
            return
                
        if len(guess) == 1:
            response = await self._handle_letter_guess(guess, context)
        else:
            response = await self._handle_word_guess(guess, context)
        
        await self._send_message(update, response)

    async def _handle_letter_guess(self, letter, context):
        if letter in self.guessed_letters or letter in self.wrong_guesses:
            return f"You already guessed '{letter}'!"
            
        if letter in self.secret_word:
            self.guessed_letters.add(letter)
            response = (
                f"✅ *Correct!* '{letter}' is in the word.\n"
                f"{self._get_display_word()}\n"
                f"{self._get_hangman_display()}"
            )
        else:
            self.wrong_guesses.add(letter)
            self.remaining_attempts -= 1
            response = (
                f"❌ *Wrong!* '{letter}' is not in the word.\n"
                f"Wrong guesses: {', '.join(sorted(self.wrong_guesses))}\n"
                f"{self._get_display_word()}\n"
                f"{self._get_hangman_display()}"
            )
        
        if self._check_win():
            self.game_over = True
            context.user_data["current_game"] = None
            return (
                f"🎉 *You won!* The word was: *{self.secret_word}*\n"
                f"Wrong guesses: {len(self.wrong_guesses)}\n"
                f"{self._get_hangman_display()}"
            )
            
        if self.remaining_attempts <= 0:
            self.game_over = True
            context.user_data["current_game"] = None
            return (
                f"💀 *Game over!* The word was: *{self.secret_word}*\n"
                f"{self._get_hangman_display()}"
            )
            
        return response

    async def _handle_word_guess(self, word, context):
        if word == self.secret_word:
            self.game_over = True
            context.user_data["current_game"] = None
            return f"🎉 *Perfect guess!* You won!"
        
        self.remaining_attempts -= 1
        if self.remaining_attempts <= 0:
            self.game_over = True
            context.user_data["current_game"] = None
            return (
                f"💀 *Wrong!* Game over. The word was: *{self.secret_word}*\n"
                f"{self._get_hangman_display()}"
            )
            
        return (
            f"❌ *Nope!* {self.remaining_attempts} attempts left.\n"
            f"{self._get_display_word()}\n"
            f"{self._get_hangman_display()}"
        )

    def _check_win(self):
        return all(letter in self.guessed_letters for letter in self.secret_word)
