import random

class WordChainGame:
    def __init__(self, words):
        self.words = set(words)
        self.current_word = random.choice(list(self.words))
        self.game_over = False
        self.name = "WordChain"
        self.used_words = set() 
        self.used_words.add(self.current_word)

    async def start_game(self, update, context):
        self.game_over = False
        self.current_word = random.choice(list(self.words))
        self.used_words = {self.current_word}
        context.user_data["current_game"] = self
        
        start_message = (
            f"🌟 Word Chain Game Started! 🌟\n"
            f"My first word is: {self.current_word}\n"
            f"Your turn! Reply with a word starting with \"{self.current_word[-1]}\""
        )
        
        if update.message is not None:
            await update.message.reply_text(start_message)
        elif update.callback_query is not None:
            await update.callback_query.message.reply_text(start_message)
        return start_message

    def find_bot_word(self, last_letter):
        """Find a valid word starting with the given letter that hasn"t been used yet"""
        possible_words = [
            word for word in self.words 
            if word.startswith(last_letter) 
            and word not in self.used_words
        ]
        return random.choice(possible_words) if possible_words else None

    def check_word(self, player_word):
        player_word = player_word.lower().strip()
        
        if not player_word:
            self.game_over = True
            return "You didn't enter a word! Game over."
            
        if player_word[0] != self.current_word[-1]:
            self.game_over = True
            return f"❌ Your word \"{player_word}\" doesn't start with \"{self.current_word[-1]}\". Game over!"

        if player_word not in self.words:
            self.game_over = True
            return f"❌ \"{player_word}\" is not in the dictionary. Game over!"

        if player_word in self.used_words:
            self.game_over = True
            return f"❌ \"{player_word}\" was already used. Game over!"

        self.used_words.add(player_word)
        self.current_word = player_word
        
        bot_word = self.find_bot_word(player_word[-1])
        if not bot_word:
            self.game_over = True
            return (
                f"✅ Your word: {player_word}\n"
                f"🏆 I can't think of a word starting with \"{player_word[-1]}\"! You win!"
            )
        
        self.used_words.add(bot_word)
        self.current_word = bot_word
        
        return (
            f"✅ Your word: {player_word}\n"
            f"🤖 My word: {bot_word}\n"
            f"Your turn! Reply with a word starting with \"{bot_word[-1]}\""
        )

    def handle_guess(self, update, context):
        player_word = update.message.text.strip().lower()
        return self.check_word(player_word)