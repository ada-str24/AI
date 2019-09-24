import Z1
import time
start = time.time()


UNKNOWN = 0
BLACK = 1
WHITE = 1e9


class Obrazek:

    def __init__(self, n=0, m=0, T=None, TT=None, Rows=None, Columns=None):
        if n == 0:
            self.read()
            self.T = [[UNKNOWN for j in range(0, self.m)] for i in range(0, self.n)]
            self.TT = [[UNKNOWN for j in range(0, self.n)] for i in range(0, self.m)]
        else:
            self.n = n
            self.m = m
            self.T = T
            self.TT = TT
            self.Rows = Rows
            self.Columns = Columns
        self.changed_blocks = []

    def read(self):
        infile = open("zad_input.txt")
        s = infile.readline()
        s = s[:-1]
        s = s.split(" ")
        self.n = int(s[0])
        self.m = int(s[1])
        self.Rows = []
        self.Columns = []
        for i in range(0, self.n):
            s = infile.readline()
            s = s[:-1]
            s = s.split(" ")
            L = []
            for c in s:
                L.append(int(c))
            self.Rows.append(L)
        for j in range(0, self.m):
            s = infile.readline()
            s = s[:-1]
            s = s.split(" ")
            L = []
            for c in s:
                L.append(int(c))
            self.Columns.append(L)


    def solve(self):
        while True:
            if self.check():
                return True
            for i in range(0, self.n):
                if not Obrazek.find_intersection(self.T[i], self.Rows[i]):
                    self.cleanup()
                    return False
                upt1 = self.update()
            for j in range(0, self.m):
                if not Obrazek.find_intersection(self.TT[j], self.Columns[j]):
                    self.cleanup()
                    return False
                upt2 = self.update()
            if (not upt1) and (not upt2):
                if self.check():
                    return True
                for j in range(0, self.n):
                    for i in range(0, self.m):
                        if self.T[i][j] == UNKNOWN:
                            self.T[i][j] = BLACK
                            self.TT[j][i] = BLACK
                            o = Obrazek(self.n, self.m, self.T, self.TT, self.Rows, self.Columns)
                            if o.solve():
                                return True
                            self.T[i][j] = WHITE
                            self.TT[j][i] = WHITE
                            self.changed_blocks.append([i, j])
                self.cleanup()
                return False

    def cleanup(self):
        for c in self.changed_blocks:
            self.T[c[0]][c[1]] = UNKNOWN
            self.TT[c[1]][c[0]] = UNKNOWN


    def print_file(self):
        outfile = open("zad_output.txt", 'w+')
        for i in range(0, self.n):
            s = ""
            for j in range(0, self.m):
                if self.T[i][j] == BLACK:
                    s += '#'
                else:
                    s += '.'
            outfile.write(s)
            outfile.write("\n")
        outfile.close()

    def print(self):
        for i in range(0, self.n):
            s = ""
            for j in range(0, self.m):
                if self.T[i][j] == BLACK:
                    s += '#'
                elif self.T[i][j] == WHITE:
                    s += '.'
                else:
                    s += 'U'
            print(s)
        print("\n")


    def check(self):
        done = True
        for i in range(0, self.n):
            Obrazek.correct(self.T[i], self.Rows[i])
        self.update()
        for j in range(0, self.m):
            if not Obrazek.correct(self.TT[j], self.Columns[j]): done = False
        self.update()
        if done: return True
        return False

    @staticmethod
    def correct(S, D):
        if Z1.correct_black(S, D):
            return True
        if Z1.correct_white(S, D):
            return True
        return False

    @staticmethod
    def determine_blacks(S, D):
        if len(D) == 1:
            if D[0] > len(S)//2:
                max_dist = D[0] - len(S)//2
                if len(S)%2 == 0:
                    for i in range(0, max_dist):
                        S[len(S)//2 + i] = BLACK
                        S[len(S)//2 - i -1] = BLACK
                else:
                    S[len(S)//2] = 1
                    for i in range(0, max_dist):
                        S[len(S)//2+i] = BLACK
                        S[len(S)//2-i] = BLACK
        if sum(D) + len(D) - 1 == len(S):
            iter = 0
            for d in D:
                for i in range(0, d):
                    S[iter+i] = BLACK
                iter += d+1
                if iter-1 < len(S):
                    S[iter-1] = WHITE

    @staticmethod
    def find_intersection(S, D):
        INTR = [-1 for i in range(0, len(S))]
        SOL = [-1 for i in range(0, len(S))]
        Obrazek.opt_dist(S, D, SOL, 0, INTR)
        if INTR[len(S)-1] == -1: return False
        for i in range(0, len(S)):
            S[i] = INTR[i]
        return True

    @staticmethod
    def opt_dist(S, D, SOL, SOL_iter, INTR):

        if sum(D) + len(D) - 1 > len(S): return

        if len(D) == 0:
            if sum(S) % WHITE != 0: return
            for i in range(0, len(S)):
                SOL[SOL_iter + i] = WHITE
            Obrazek.intersect(SOL, INTR)
            for i in range(0, len(S)):
                SOL[SOL_iter + i] = S[i]
            return

        if len(D) == 1 and D[0] == len(S):
            if sum(S) < WHITE:
                for i in range(0, len(S)):
                    SOL[SOL_iter + i] = BLACK
                Obrazek.intersect(SOL, INTR)
                for i in range(0, len(S)):
                    SOL[SOL_iter + i] = S[i]
            return

        if sum(S[0:D[0]]) < WHITE and S[D[0]] != BLACK:
            for i in range(0, D[0]):
                SOL[SOL_iter + i] = BLACK
            SOL[SOL_iter + D[0]] = WHITE
            Obrazek.opt_dist(S[D[0]+1 : len(S)], D[1:len(D)], SOL, SOL_iter+D[0]+1, INTR)
            for i in range(0, D[0]+1):
                SOL[SOL_iter + i] = S[i]

        if S[0] != BLACK:
            SOL[SOL_iter] = WHITE
            Obrazek.opt_dist(S[1:len(S)], D, SOL, SOL_iter+1, INTR)
            SOL[SOL_iter] = S[0]

    @staticmethod
    def intersect(sol, intr):
        for i in range(0, len(sol)):
            if intr[i] == -1:
                intr[i] = sol[i]
            elif intr[i] == BLACK:
                if sol[i] == WHITE: intr[i] = UNKNOWN
            elif intr[i] == WHITE:
                if sol[i] == BLACK: intr[i] = UNKNOWN

    def update(self):
        changed = False
        for i in range(0, self.m):
            for j in range(0, self.n):
                if self.T[j][i] == UNKNOWN and self.TT[i][j] != UNKNOWN:
                    self.T[j][i] = self.TT[i][j]
                    self.changed_blocks.append([j, i])
                    changed = True
                if self.T[j][i] != UNKNOWN and self.TT[i][j] == UNKNOWN:
                    self.TT[i][j] = self.T[j][i]
                    self.changed_blocks.append([j,i])
                    changed = True
        return changed


obrazek = Obrazek()
obrazek.solve()
obrazek.print_file()

end = time.time()
print(round(end - start, 6))

'''S = [1,WHITE,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
print(Obrazek.find_intersection(S, [1,3,4,5]))
print(S)'''

