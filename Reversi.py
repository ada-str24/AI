# Reversi
# Minimax

import random
import time
import sys

start = time.time()

MAX = 1
MIN = 0

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
UL = 4
UR = 5
DL = 6
DR = 7

PASS = 0

class State:

    def __init__(self, player, opponent, turn):
        self.player = player
        self.opponent = opponent
        self.turn = turn

    def print(self):
        # print("new")
        for i in range(0, 64):
            if (self.player & (1<<i)) != 0: print('-', end='')
            elif (self.opponent & (1<<i)) != 0: print('+', end='')
            else: print('.', end='')
            if i%8 == 7: print('\n')

    @staticmethod
    def print_mask(mask):
        print("new")
        for i in range(0, 64):
            if (mask & (1<<i)) != 0: print('X', end='')
            else: print('.', end='')
            if i%8 == 7: print('\n')

    def possible_moves(self):
        moves = []
        for i in range(0, 64):
            val, rev = self.move(i)
            if val != 0:
                moves.append([val, i, State(self.opponent^(self.opponent & rev), self.player | rev, 1-self.turn)])
        return moves

    def move(self, dest):
        reversed = 0
        if ((1<<dest) & self.player) != 0 or ((1<<dest) & self.opponent) != 0:
            return 0, 0
        counter = 0
        for i in range(0, 8):
            c,r = self.how_many(dest, i)
            counter += c
            reversed |= r
        return counter, reversed

    def how_many(self, dest, direction):
        dest = 1<<dest
        counter = 0
        reversed = 0
        for i in range(0, 8):
            reversed |= dest
            dest, k = State.move_in_direction(dest, 0, direction)
            if (dest & self.opponent) == 0:
                if (dest & self.player) != 0:
                    return counter, reversed
                return 0, 0
            counter += 1

    def how_many2(self, dest, direction):
        reversed = 0
        d = dest
        k = dest
        dest = 1<<dest
        for i in range(0, 8):
            reversed |= dest
            #print(bin(dest))
            new_dest, new_k = State.move_in_direction(dest, k, direction)
            new_dest |= dest
            if new_k < 0 or new_k > 64: break
            new_dest &= self.opponent
            new_dest &= (~(((self.opponent | self.player) >> new_k) & 0x0000000000000001) + 1) & 0xFFFFFFFFFFFFFFFF
            #print(hex(new_dest))
            if dest | new_dest == dest: break
            dest = new_dest
            k = new_k
        #print(hex(new_dest))
        #print(hex(((~(1 << d)) & 0xFFFFFFFFFFFFFFFF)))
        return bin(((~(1 << d)) & 0xFFFFFFFFFFFFFFFF) & new_dest).count("1"), (new_dest | (1<<d))

    @staticmethod
    def move_in_direction(pos, k, dir):
        if dir == UP:
            return pos >> 8, k-8
        if dir == DOWN:
            return pos << 8, k+8
        if dir == LEFT:
            return (pos >> 1) & 0x7F7F7F7F7F7F7F7F, k-1
        if dir == RIGHT:
            return (pos << 1) & 0xFEFEFEFEFEFEFEFE, k+1
        if dir == UL:
            return State.move_in_direction(pos >> 8, k-8, LEFT)
        if dir == UR:
            return State.move_in_direction(pos >> 8, k-8, RIGHT)
        if dir == DL:
            return State.move_in_direction(pos << 8, k+8, LEFT)
        if dir == DR:
            return State.move_in_direction(pos << 8, k+8, RIGHT)

    def final(self):
        if self.player | self.opponent == 0xFFFFFFFFFFFFFFFF: return True
        return False

    def profit(self):
        if self.turn == MIN:
            return bin(self.opponent).count("1") - bin(self.player).count("1")
        return bin(self.player).count("1") - bin(self.opponent).count("1")


    def heur(self):
        p = self.profit()
        if self.turn == MAX:
            p += bin(self.player & 0x8100000000000081).count("1")*10
            p -= bin(self.opponent & 0x8100000000000081).count("1")*10
            p += bin(self.player & 0x3C0081818181003C).count("1")*3
            p -= bin(self.opponent & 0x3C0081818181003C).count("1")*3
        else:
            p -= bin(self.player & 0x8100000000000081).count("1")*10
            p += bin(self.opponent & 0x8100000000000081).count("1")*10
            p -= bin(self.player & 0x3C0081818181003C).count("1")*3
            p += bin(self.opponent & 0x3C0081818181003C).count("1")*3
        return p


def decision(state):
    moves = state.possible_moves()
    if len(moves) == 0:
        return [0, 0, State(state.opponent, state.player, 1-state.turn)]
    if state.turn == MIN:
        for m in moves:
            print(m[1], end=' ')
        print()
        l = sys.stdin.readline()
        l = l.split('\n')
        l = int(l[0])
        # m = random.choice(moves)
        move = None
        for m in moves:
            if m[1] == l: move = m
        return move
    else:
        if len(moves) == 0: return None
        m = max(moves, key=lambda move: minmax(move[2]))
        print(m[1])
        return m


def minmax(state, depth=0, passed=False):
    if depth >= 4:
        return state.heur()
    if state.final():
        return state.profit()
    moves = state.possible_moves()
    if len(moves) == 0:
        if passed: return 0
        return minmax(State(state.opponent, state.player, 1-state.turn), depth+1, True)
    val = [minmax(move[2], depth+1) for move in moves]
    if state.turn == MIN:
        return min(val)
    else:
        return max(val)

def solve():
    wins = [0, 0]
    for i in range(0, 1):
        print(i)
        state = State(0x0000000810000000, 0x0000001008000000, MAX)
        licz=0
        pas = False
        while not state.final():
            d = decision(state)
            if d is None:
                if pas: break
                pas = True
                state = State(state.opponent, state.player, 1 - state.turn)
                continue
            pas = False
            state = d[2]
            #print(d[1])
        if state.profit()>0: wins[0] += 1
        else: wins[1] += 1
    print("lost :")
    print(wins[1])

solve()
end = time.time()
print(round(end - start, 6))

# state = State(0x0000000810000000, 0x0000001008000000, MAX)
# state = State(0x0000000000000000, 0x0000000800000000, MAX)
# state.print()
# print(state.how_many2(27, DOWN))
#
# x = 0x0
# print(bin(0xFFFFFFFFFFFFFFFF & ((~x)+1)))
