class Game:
    def __init__(self, name):
        self.name = name

    async def start_game(self, update, context):
        raise NotImplementedError("This method should be overridden by a mini-game class")

    def handle_guess(self, update, context):
        raise NotImplementedError("This method should be overridden by a mini-game class")

    def get_feedback(self):
        raise NotImplementedError("This method should be overridden by a mini-game class")
