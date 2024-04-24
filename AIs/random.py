import chess
import random


def ai_random(moves):
    index = random.randint(0, len(moves) - 1)
    return moves[index]
