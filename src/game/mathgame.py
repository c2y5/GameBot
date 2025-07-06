import random
import re
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

class MathGame:
    def __init__(self):
        self.goal = 0
        self.usable_operators = ["+", "-", "*", "/"]
        self.current_numbers = []
        self.name = "Math Challenge"
        self.game_over = False
        self.last_update = None
        self.computer_solution = ""
        
    async def start_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.last_update = update
        await self.new_round(update, context)
        
    async def new_round(self, update: Update, context: ContextTypes.DEFAULT_TYPE, last_response: str = None):
        self.game_over = False
        goal, numbers, computer_solution = self._generate_data()
        self.goal = goal
        self.current_numbers = numbers
        self.computer_solution = computer_solution
        context.user_data["current_game"] = self
        
        start_message = (
            "🧮 *Math Challenge!*\n"
            f"Use these numbers: {', '.join(map(str, numbers))}\n"
            f"Target: *{goal}*\n"
            r"Combine them with +, -, \*, / and parentheses to reach the target."
            "\n"
            r"Example: (3 + 5) \* 2"
            "\n"
            "Type /stop to end the game or $solution to see the answer."
        )
        
        if last_response:
            await self._send_message(update, last_response)
            
        await self._send_message(update, start_message)

    def _generate_data(self):
        while True:
            self.current_numbers = [random.randint(1, 15) for _ in range(4)]
            operators = [random.choice(self.usable_operators) for _ in range(3)]
            
            structures = [
                "((a {op1} b) {op2} c) {op3} d",
                "(a {op1} (b {op2} c)) {op3} d",
                "a {op1} ((b {op2} c) {op3} d)",
                "(a {op1} b) {op2} (c {op3} d)"
            ]
            
            random.shuffle(structures)
            
            for structure in structures:
                expression = structure.format(
                    op1=operators[0],
                    op2=operators[1],
                    op3=operators[2]
                )
                
                try:
                    a, b, c, d = self.current_numbers
                    result = eval(expression)
                    
                    if isinstance(result, float):
                        if not result.is_integer() or abs(result) > 100:
                            continue
                        result = int(result)
                    
                    if -100 <= result <= 100 and result != 0:
                        self.goal = result
                        computer_sol = expression.replace("a", str(a)).replace("b", str(b))\
                                                .replace("c", str(c)).replace("d", str(d))
                        return self.goal, self.current_numbers, computer_sol
                        
                except ZeroDivisionError:
                    continue
        
    def _verify_solution(self, user_input):
        input_numbers = [int(num) for num in re.findall(r'\d+', user_input)]
        if sorted(input_numbers) != sorted(self.current_numbers):
            return False, "You must use exactly the provided numbers."

        if not re.fullmatch(r'^[\d+\-*/(). $]+$', user_input):
            return False, "Only numbers, +, -, *, /, $, and parentheses are allowed."

        try:
            result = eval(user_input)
            if isinstance(result, float):
                if not result.is_integer():
                    return False, "Result must be a whole number."
                result = int(result)
            
            if result == self.goal:
                return True, f"✅ Correct! The computer's solution was: {self.computer_solution} = {self.goal}"
            else:
                return False, f"❌ Incorrect. Your solution equals {result}, but the target is {self.goal}."
        except ZeroDivisionError:
            return False, "❌ Division by zero is not allowed."
        except:
            return False, "❌ Invalid mathematical expression."

    async def check_guess(self, player_guess: str, context: ContextTypes.DEFAULT_TYPE):
        player_guess = player_guess.strip()
        
        if not player_guess:
            return "Please enter a solution or type /stop to end the game."

        if player_guess.lower() == "$solution":
            await self.show_solution(self.last_update, context)
            return None

        success, message = self._verify_solution(player_guess)
        if success:
            if self.last_update:
                await self.new_round(self.last_update, context, last_response=message)
                return None
        return message

    async def show_solution(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.computer_solution:
            solution_message = (
                f"💡 The solution was:\n"
                f"{self.computer_solution} = {self.goal}\n\n"
                "Starting a new challenge..."
            )
            await self.new_round(update, context, last_response=solution_message)
        else:
            await self._send_message(update, "No solution available. Start a new game with /play")

    async def _send_message(self, update, text, parse_markdown=True):
        """Helper method to send messages with proper error handling for Markdown"""
        try:
            if update.message:
                await update.message.reply_text(
                    text,
                    parse_mode=ParseMode.MARKDOWN if parse_markdown else None
                )
            elif update.callback_query:
                await update.callback_query.message.reply_text(
                    text,
                    parse_mode=ParseMode.MARKDOWN if parse_markdown else None
                )
        except Exception as e:
            # If Markdown parsing fails, send as plain text
            if "Can't parse entities" in str(e):
                if update.message:
                    await update.message.reply_text(text, parse_mode=None)
                elif update.callback_query:
                    await update.callback_query.message.reply_text(text, parse_mode=None)
            else:
                raise e

    async def handle_guess(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.last_update = update
        player_guess = update.message.text.strip()
        
        # First check if it's the solution command
        if player_guess.lower() == "$solution":
            await self.show_solution(update, context)
            return
            
        # Process as math solution
        response = await self.check_guess(player_guess, context)
        if response is not None:
            # Send response without Markdown parsing to avoid entity errors
            await self._send_message(update, response, parse_markdown=False)
