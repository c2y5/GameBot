# type: ignore

import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

class MemoryGame:
    def __init__(self):
        self.grid_size = 2
        self.red_squares = set()
        self.user_clicks = set()
        self.game_over = False
        self.name = "Memory Game"
        self.current_message = None
        self.stage = 1
        self.display_time = 3
        self.rounds_completed = 0
        self.rounds_per_size = 2
        
    async def start_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.grid_size = 2
        self.stage = 1
        self.rounds_completed = 0
        self.rounds_per_size = self.grid_size
        self.game_over = False
        context.user_data["current_game"] = self
        await self.new_round(update, context)
        
    async def new_round(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        total_squares = self.grid_size ** 2
        min_red = self.grid_size
        max_red = max(min_red + 1, int(total_squares * 0.3))
        num_red = random.randint(min_red, max_red)
        
        self.red_squares = set()
        while len(self.red_squares) < num_red:
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)
            self.red_squares.add((row, col))
        
        self.user_clicks = set()
        
        await self._show_pattern(update, context)
        
        await asyncio.sleep(self.display_time)
        await self._show_blank_grid(update, context)
    
    async def _show_pattern(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for row in range(self.grid_size):
            keyboard_row = []
            for col in range(self.grid_size):
                if (row, col) in self.red_squares:
                    text = "🔴"
                else:
                    text = "⚪"
                keyboard_row.append(InlineKeyboardButton(text, callback_data="ignore"))
            keyboard.append(keyboard_row)
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = (f"🔍 *Memory Game - Stage {self.stage}*\n\n"
               f"Round {self.rounds_completed + 1}/{self.rounds_per_size} at {self.grid_size}x{self.grid_size}\n"
               f"Find {len(self.red_squares)} red squares!\n"
               "Memorize the pattern!")
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            self.current_message = await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    async def _show_blank_grid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for row in range(self.grid_size):
            keyboard_row = []
            for col in range(self.grid_size):
                keyboard_row.append(InlineKeyboardButton("⬜", callback_data=f"{row},{col}"))
            keyboard.append(keyboard_row)
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = (f"🔍 *Memory Game - Stage {self.stage}*\n\n"
               f"Round {self.rounds_completed + 1}/{self.rounds_per_size} at {self.grid_size}x{self.grid_size}\n"
               "Click the squares that were red!")
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            self.current_message = await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    async def handle_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if self.game_over:
            return
        
        try:
            row, col = map(int, query.data.split(","))
        except:
            return
        
        if (row, col) in self.user_clicks:
            return
        
        self.user_clicks.add((row, col))
        
        keyboard = []
        for r in range(self.grid_size):
            keyboard_row = []
            for c in range(self.grid_size):
                if (r, c) in self.user_clicks:
                    if (r, c) in self.red_squares:
                        text = "🟢"
                    else:
                        text = "🔴"
                else:
                    text = "⬜"
                keyboard_row.append(InlineKeyboardButton(text, callback_data=f"{r},{c}"))
            keyboard.append(keyboard_row)
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
        
        correct = sum(1 for square in self.user_clicks if square in self.red_squares)
        incorrect = sum(1 for square in self.user_clicks if square not in self.red_squares)
        remaining = len(self.red_squares) - correct
        
        if incorrect > 0:
            self.game_over = True
            await self._end_game(update, context, success=False)
        elif remaining == 0:
            self.rounds_completed += 1
            
            if self.rounds_completed < self.rounds_per_size:
                await self.new_round(update, context)
            else:
                if self.grid_size < 7:
                    self.grid_size += 1
                    self.stage += 1
                    self.rounds_completed = 0
                    self.rounds_per_size = self.grid_size
                    self.display_time = min(5, self.display_time + 0.5)
                    await self.new_round(update, context)
                else:
                    self.game_over = True
                    await self._end_game(update, context, success=True)
    
    async def _end_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE, success: bool):
        context.user_data["current_game"] = None
        
        if success:
            text = (
                "🎉 *Congratulations!* 🎉\n\n"
                "You've completed all stages of the Memory Game!\n"
                "Type /play to start a new game."
            )
        else:
            keyboard = []
            for row in range(self.grid_size):
                keyboard_row = []
                for col in range(self.grid_size):
                    if (row, col) in self.red_squares:
                        text = "🔴"
                    else:
                        text = "⚪"
                    keyboard_row.append(InlineKeyboardButton(text, callback_data="ignore"))
                keyboard.append(keyboard_row)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                "💀 *Game Over!*\n\n"
                "You clicked a wrong square.\n"
                f"Stage reached: {self.stage} ({self.grid_size}x{self.grid_size})\n"
                "Here was the correct pattern:\n"
                "Type /play to try again."
            )
            
            query = update.callback_query
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return
            
        query = update.callback_query
        await query.edit_message_text(
            text=text,
            parse_mode="Markdown"
        )