import random
from telegram import Update
from telegram.ext import ContextTypes

class UnscrambleGame:
    def __init__(self, words):
        self.words = set(words)
        self.current_word = ""
        self.scrambled_word = ""
        self.game_over = False
        self.name = "Unscramble Word"
        self.last_update = None
        
    async def start_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.last_update = update 
        await self.new_round(update, context)
        
    async def new_round(self, update: Update, context: ContextTypes.DEFAULT_TYPE, last_response: str = None):
        while True:
            self.current_word = random.choice(list(self.words)).lower()

            if len(self.current_word) >= 5:
                break
        
        self.scrambled_word = "".join(random.sample(self.current_word, len(self.current_word)))
        self.game_over = False
        context.user_data["current_game"] = self
        
        start_message = (
            "🔑 *New Unscramble Challenge!*\n"
            f"Unscramble this word: *{self.scrambled_word}*\n"
            "Reply with your guess or type /stop to end the game."
        )
        
        if last_response:
            await self._send_message(update, last_response)

        await self._send_message(update, start_message)

    async def _send_message(self, update, text):
        if update.message:
            await update.message.reply_text(text, parse_mode="Markdown")
        elif update.callback_query:
            await update.callback_query.message.reply_text(text, parse_mode="Markdown")

    async def check_guess(self, player_guess: str, context: ContextTypes.DEFAULT_TYPE):
        player_guess = player_guess.lower().strip()
        print(self.current_word)
        if not player_guess:
            return "Please enter a word or type /stop to end the game."

        if player_guess == self.current_word:
            response = f"✅ *Correct!* The word was \"{self.current_word}\"."
            if self.last_update:
                await self.new_round(self.last_update, context, last_response=response)
                return

        return "❌ That's not correct. Try again or type /stop to end the game."

    async def handle_guess(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.last_update = update
        player_guess = update.message.text.strip().lower()
        response = await self.check_guess(player_guess, context)
        if response is None:
            return
        await self._send_message(update, response)
