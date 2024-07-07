import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Game variables
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
TETROMINOS = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]  # Z
]

class TetrisGame:
    def __init__(self):
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_piece = None
        self.current_pos = None

    def new_piece(self):
        self.current_piece = random.choice(TETROMINOS)
        self.current_pos = [0, BOARD_WIDTH // 2 - len(self.current_piece[0]) // 2]

    def move(self, dx, dy):
        new_pos = [self.current_pos[0] + dy, self.current_pos[1] + dx]
        if self.is_valid_position(new_pos):
            self.current_pos = new_pos
            return True
        return False

    def rotate(self):
        rotated = list(zip(*self.current_piece[::-1]))
        if self.is_valid_position(self.current_pos, rotated):
            self.current_piece = rotated
            return True
        return False

    def is_valid_position(self, pos=None, piece=None):
        if pos is None:
            pos = self.current_pos
        if piece is None:
            piece = self.current_piece

        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    if (pos[0] + y >= BOARD_HEIGHT or
                        pos[1] + x < 0 or
                        pos[1] + x >= BOARD_WIDTH or
                        self.board[pos[0] + y][pos[1] + x]):
                        return False
        return True

    def place_piece(self):
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.current_pos[0] + y][self.current_pos[1] + x] = 1

    def clear_lines(self):
        lines_cleared = 0
        for y in range(BOARD_HEIGHT - 1, -1, -1):
            if all(self.board[y]):
                del self.board[y]
                self.board.insert(0, [0 for _ in range(BOARD_WIDTH)])
                lines_cleared += 1
        return lines_cleared

    def step(self):
        if not self.move(0, 1):
            self.place_piece()
            lines_cleared = self.clear_lines()
            self.new_piece()
            if not self.is_valid_position():
                return False, lines_cleared
        return True, 0

    def get_board_string(self):
        board_str = ""
        for row in self.board:
            board_str += "".join(["🟦" if cell else "⬜" for cell in row]) + "\n"
        return board_str

# Game instance
game = TetrisGame()

def start(update: Update, context: CallbackContext) -> None:
    global game
    game = TetrisGame()
    game.new_piece()
    update.message.reply_text(f"Welcome to Telegram Tetris!\n\n{game.get_board_string()}")

def move_left(update: Update, context: CallbackContext) -> None:
    if game.move(-1, 0):
        update.message.reply_text(game.get_board_string())

def move_right(update: Update, context: CallbackContext) -> None:
    if game.move(1, 0):
        update.message.reply_text(game.get_board_string())

def rotate(update: Update, context: CallbackContext) -> None:
    if game.rotate():
        update.message.reply_text(game.get_board_string())

def drop(update: Update, context: CallbackContext) -> None:
    while game.move(0, 1):
        pass
    game_over, lines_cleared = game.step()
    if game_over:
        update.message.reply_text(f"Game Over! Lines cleared: {lines_cleared}")
    else:
        update.message.reply_text(f"{game.get_board_string()}\nLines cleared: {lines_cleared}")

def main() -> None:
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    updater = Updater("6401277675:AAEz4pXPDNfy1Nh_WIC9C8vqITs7oYQCkVI", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("left", move_left))
    dp.add_handler(CommandHandler("right", move_right))
    dp.add_handler(CommandHandler("rotate", rotate))
    dp.add_handler(CommandHandler("drop", drop))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
