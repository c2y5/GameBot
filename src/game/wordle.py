import random
from .game import Game
import json

def load_word_list():
    with open("word-list.json", "r") as file:
        return json.load(file)

def load_valid_words():
    with open("valid-words.json", "r") as file:
        return json.load(file)

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

    async def handle_guess(self, update, context):
        guessed_word = update.message.text.strip().lower()

        if len(guessed_word) != 5:
            await update.message.reply_text("Your guess must be a 5-letter word.")
            return
        
        if guessed_word not in self.valid_words:
            await update.message.reply_text("This is not a valid word. Please guess a valid 5-letter word.")
            return

        if guessed_word == self.target_word:
            await update.message.reply_text(f"Congrats! You guessed the word: {self.target_word}. You win!")
            context.user_data["current_game"] = None
            return
        
        feedback = self.get_feedback(guessed_word)
        self.attempts -= 1
        if self.attempts == 0:
            await update.message.reply_text(f"Game over! The word was: {self.target_word}. Better luck next time!")
            context.user_data["current_game"] = None
            return
        
        await update.message.reply_text(feedback)

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
