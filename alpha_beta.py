import chess
import time

MATE_SCORE = 10**6
INF = 10**9

class AlphaBetaMinimax:
    def __init__(self, evaluate, time_limit=None, use_tt=True, use_qsearch=True):
        self.evaluate = evaluate
        self.time_limit = time_limit
        self.use_tt = use_tt
        self.use_qsearch = use_qsearch
        self.tt = {}
        self.nodes = 0
        self.start_time = None

    def get_tt_key(self, board):
        if hasattr(board, "transposition_key"):
            return board.transposition_key()
        elif hasattr(board, "_transposition_key"):
            return board._transposition_key()
        else:
            return hash(board)

    def search(self, board, max_depth):
        self.start_time = time.time()
        self.nodes = 0
        best_move = None

        for depth in range(1, max_depth + 1):
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
        alpha_orig = alpha
        key = self.get_tt_key(board)

        if self.time_limit and time.time() - self.start_time > self.time_limit:
            return self.evaluate(board), None

        if self.use_tt and key in self.tt:
            tt_depth, tt_flag, tt_value, tt_move = self.tt[key]
            if tt_depth >= depth:
                if tt_flag == "EXACT":
                    return tt_value, tt_move
                elif tt_flag == "LOWER":
                    alpha = max(alpha, tt_value)
                elif tt_flag == "UPPER":
                    beta = min(beta, tt_value)
                if alpha >= beta:
                    return tt_value, tt_move

        if depth == 0 or board.is_game_over():
            if self.use_qsearch:
                return self.quiescence(board, alpha, beta), None
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

        if self.use_tt:
            if value <= alpha_orig:
                flag = "UPPER"
            elif value >= beta:
                flag = "LOWER"
            else:
                flag = "EXACT"
            self.tt[key] = (depth, flag, value, best_move)

        return value, best_move

    def min_value(self, board, depth, alpha, beta):
        self.nodes += 1
        beta_orig = beta
        key = self.get_tt_key(board)

        if self.time_limit and time.time() - self.start_time > self.time_limit:
            return self.evaluate(board), None

        if self.use_tt and key in self.tt:
            tt_depth, tt_flag, tt_value, tt_move = self.tt[key]
            if tt_depth >= depth:
                if tt_flag == "EXACT":
                    return tt_value, tt_move
                elif tt_flag == "LOWER":
                    alpha = max(alpha, tt_value)
                elif tt_flag == "UPPER":
                    beta = min(beta, tt_value)
                if alpha >= beta:
                    return tt_value, tt_move

        if depth == 0 or board.is_game_over():
            if self.use_qsearch:
                return self.quiescence(board, alpha, beta), None
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

        if self.use_tt:
            if value <= alpha:
                flag = "UPPER"
            elif value >= beta_orig:
                flag = "LOWER"
            else:
                flag = "EXACT"
            self.tt[key] = (depth, flag, value, best_move)

        return value, best_move

    def quiescence(self, board, alpha, beta):
        stand_pat = self.evaluate(board)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        for move in self.order_moves(board, captures_only=True):
            board.push(move)
            score = -self.quiescence(board, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def order_moves(self, board, captures_only=False):
        moves = list(board.legal_moves)
        if captures_only:
            moves = [m for m in moves if board.is_capture(m)]

        def mvv_lva(move):
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                victim_value = victim.piece_type if victim else 0
                attacker_value = attacker.piece_type if attacker else 1
                return (victim_value * 10) - attacker_value
            return 0

        key = self.get_tt_key(board)
        tt_move = None
        if self.use_tt and key in self.tt:
            tt_move = self.tt[key][3]

        if tt_move in moves:
            moves.remove(tt_move)
            moves.insert(0, tt_move)

        moves.sort(key=mvv_lva, reverse=True)
        return moves
