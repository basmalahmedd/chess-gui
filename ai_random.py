import random
import chess

class RandomAI:
    def search(self, board, max_depth):
        moves = list(board.legal_moves)
        return random.choice(moves) if moves else None
