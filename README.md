# Telegram Game Bot

A fun and interactive Telegram bot featuring multiple word and puzzle games to challenge your mind.

[Try the bot here!](https://t.me/convergegamebot)

## Available Games
**1. Wordle**
- Guess the hidden 5-letter word in 6 tries
- Letters change color to show if they're correct and in position (🟩), correct but wrong position (🟨), or not in word (🟥)

**2. WordChain**
- Type a word that starts with the last letter of the previous word
- Example: "apple" -> "elephant" -> "tiger" -> ...
- Challenge mode against friends coming soon!

**3. Hangman**
- Classic word guessing game
- Guess letters before the stick figure is complete

**4. Unscramble Word**
- Rearrange scrambled letters to form the correct word
- Example: "elppha" -> "apple"

**5. Memory Game**
- Remember which square had the red dot
- Increasing difficulty with more squares
- Tests your visual memory skills

**6. Math Challenge**
- Combine given numbers with +, -, *, / to reach target
- Example: Numbers: 2, 4, 5, 6 Target: 24 -> (2 + 4) * 5 - 6
- Shows solution if stuck with ``$solution``

## How to play?
- Choose a game using ``/play``
- Follow the in-game instructions
- Use ``/stop`` to end any game

## Self-host
### Installation

```bash
git clone https://github.com/c2y5/GameBot.git
cd GameBot
pip install -r requirements.txt
python main.py
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## Contributing

Contributions and suggestions are welcome! Please open issues or submit pull requests.

---
