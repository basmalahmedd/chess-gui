import chess
import time

MATE_SCORE = 10**6
INF = 10**9

class AlphaBetaMinimax:
    def __init__(self, evaluate, time_limit=None, use_move_ordering=False):
        self.evaluate = evaluate
        self.time_limit = time_limit
        self.use_move_ordering = use_move_ordering
        self.nodes = 0
        self.start_time = None

    def search(self, board, max_depth):
        self.start_time = time.time()
        self.nodes = 0
        best_move = None

        for depth in range(1, max_depth + 1):  # iterative deepening
            if board.turn == chess.WHITE:
                value, move = self.max_value(board, depth, -INF, INF)
            else:
                value, move = self.min_value(board, depth, -INF, INF)

            if move is not None:
                best_move = move

            if self.time_limit and time.time() - self.start_time > self.time_limit:
                break

        return best_move

    def max_value(self, board, depth, alpha, beta):
        self.nodes += 1
        if self.time_limit and time.time() - self.start_time > self.time_limit:
            return self.evaluate(board), None
        if depth == 0 or board.is_game_over():
            return self.evaluate(board), None

        value = -INF
        best_move = None
        moves = self.order_moves(board)

        for move in moves:
            board.push(move)
            child_value, _ = self.min_value(board, depth - 1, alpha, beta)
            board.pop()

            if child_value > value:
                value = child_value
                best_move = move

            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, best_move

    def min_value(self, board, depth, alpha, beta):
        self.nodes += 1
        if self.time_limit and time.time() - self.start_time > self.time_limit:
            return self.evaluate(board), None
        if depth == 0 or board.is_game_over():
            return self.evaluate(board), None

        value = INF
        best_move = None
        moves = self.order_moves(board)

        for move in moves:
            board.push(move)
            child_value, _ = self.max_value(board, depth - 1, alpha, beta)
            board.pop()

            if child_value < value:
                value = child_value
                best_move = move

            beta = min(beta, value)
            if beta <= alpha:
                break
        return value, best_move

    def order_moves(self, board):
        moves = list(board.legal_moves)
        if not self.use_move_ordering:
            return moves

        # MVV-LVA heuristic
        def mvv_lva(move):
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                victim_value = victim.piece_type if victim else 0
                attacker_value = attacker.piece_type if attacker else 1
                return (victim_value * 10) - attacker_value
            return 0

        moves.sort(key=mvv_lva, reverse=True)
        return moves
