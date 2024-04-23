import chess
import chess.svg
import chess.pgn
import pygame
import time
import sys
import io

træk = 0
legal_count = 0
board = chess.Board()

print("---------------")
print(board)
print("---------------")

def choice():
    global træk,legal_count
    print(board.turn)
    legal = 0

    legal_count = board.legal_moves.count()
    move_list = list(board.legal_moves)
    if legal_count == 0:
        print("Der er skakmat")
    if legal_count == 1:
        træk = str(move_list[0])
        print("Der er kun ét muligt træk, som blev fortaget automatisk")
    else:
        træk = input("Skriv træk: ")

    for i in range(len(move_list)):
        legal = 0
        #print(move_list[i])
        if træk == str(move_list[i]):
            legal = 1
            træk = move_list[i]
            break
    if legal == 0:
        print("Ikke et gyldigt træk")
        choice()
    if legal == 1:
        board.push(træk)
        print("---------------")
        print(board)
        print("---------------")
        choice()


choice()