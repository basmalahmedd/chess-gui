import chess
import time
import sys
import argparse
from alpha_beta import AlphaBetaMinimax
from ai_random import RandomAI
from evaluation import improved_eval

def play_game(white_ai, black_ai, max_depth_white, max_depth_black):
    board = chess.Board()
    start_time = time.time()
    white_nodes = 0
    black_nodes = 0

    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = white_ai.search(board, max_depth_white)
            if hasattr(white_ai, "nodes"):
                white_nodes += white_ai.nodes
        else:
            move = black_ai.search(board, max_depth_black)
            if hasattr(black_ai, "nodes"):
                black_nodes += black_ai.nodes

        if move is None:
            break
        board.push(move)

    game_time = time.time() - start_time
    return board.result(), white_nodes, black_nodes, game_time


def summarize(results, label, total_nodes, total_time, games=10):
    win_rate = (results["1-0"] + 0.5 * results["1/2-1/2"]) / sum(results.values()) * 100
    print(f"\n{label}:")
    print(f"  Win rate for White: {win_rate:.1f}% over {sum(results.values())} games")
    print(f"  Outcome breakdown: {results}")
    print(f"  Average nodes searched per game: {total_nodes // games}")
    print(f"  Average game time: {total_time / games:.2f} seconds\n")
    sys.stdout.flush()   


# --- Main ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("depth_simple", type=int, help="Depth for Simple AB")
    parser.add_argument("depth_opt", type=int, help="Depth for Optimized AB")
    args = parser.parse_args()

    depth_simple = args.depth_simple
    depth_opt = args.depth_opt

    # --- Step 1: Alpha-Beta vs Random ---
    ab_ai = AlphaBetaMinimax(evaluate=improved_eval, time_limit=2.0, use_move_ordering=True)
    rand_ai = RandomAI()

    results = {"1-0": 0, "0-1": 0, "1/2-1/2": 0}
    agent_wins = {"alpha_beta": 0, "random": 0, "draws": 0}
    total_nodes = total_time = 0

    for _ in range(5): 
        # AB White vs Random Black
        res, wn, bn, t = play_game(ab_ai, rand_ai, depth_simple, 0)
        results[res] += 1
        total_nodes += wn + bn
        total_time += t
        if res == "1-0": agent_wins["alpha_beta"] += 1
        elif res == "0-1": agent_wins["random"] += 1
        else: agent_wins["draws"] += 1

        # Random White vs AB Black
        res, wn, bn, t = play_game(rand_ai, ab_ai, 0, depth_simple)
        results[res] += 1
        total_nodes += wn + bn
        total_time += t
        if res == "1-0": agent_wins["random"] += 1
        elif res == "0-1": agent_wins["alpha_beta"] += 1
        else: agent_wins["draws"] += 1

    summarize(results, "Alpha-Beta vs Random", total_nodes, total_time, games=10)
    print("  Agent win counts:", agent_wins)



    # --- Step 2: Simple AB vs Optimized AB ---
    simple_ab = AlphaBetaMinimax(evaluate=improved_eval, time_limit=2.0, use_move_ordering=False)
    opt_ab = AlphaBetaMinimax(evaluate=improved_eval, time_limit=2.0, use_move_ordering=True)

    results = {"1-0": 0, "0-1": 0, "1/2-1/2": 0}
    agent_wins = {"simple": 0, "optimized": 0, "draws": 0}
    total_nodes = total_time = 0

    for _ in range(5):
        # Simple White vs Optimized Black
        res, wn, bn, t = play_game(simple_ab, opt_ab, depth_simple, depth_opt)
        results[res] += 1
        total_nodes += wn + bn
        total_time += t
        if res == "1-0": agent_wins["simple"] += 1
        elif res == "0-1": agent_wins["optimized"] += 1
        else: agent_wins["draws"] += 1

        # Optimized White vs Simple Black
        res, wn, bn, t = play_game(opt_ab, simple_ab, depth_opt, depth_simple)
        results[res] += 1
        total_nodes += wn + bn
        total_time += t
        if res == "1-0": agent_wins["optimized"] += 1
        elif res == "0-1": agent_wins["simple"] += 1
        else: agent_wins["draws"] += 1

    summarize(results, "Simple AB vs Optimized AB", total_nodes, total_time, games=10)
    print("  Agent win counts:", agent_wins)
