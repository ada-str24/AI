import queue
import heapq
import time
start = time.time()

UP = 1
DOWN = 3
LEFT = 2
RIGHT = 4

EMPTY = 0
TARGET = 1


class Maze:
    def __init__(self):
        maze = []
        n = 0
        infile = open("zad_input.txt")
        for line in infile.readlines():
            line = line[:-1]
            maze.append(line)
            n += 1
            m = len(line)
        infile.close()

        vert_numbers = []
        for row in maze:
            r = []
            for col in row:
                r.append(0)
            vert_numbers.append(r)
        boxes = []
        self.vertices = []
        self.graph = []
        self.box_graph = []
        self.number_of_boxes = 0
        vertex = 0
        keeper = 0

        for i in range(1, n-1):
            for j in range(1, m-1):
                if maze[i][j] == 'W': continue
                self.vertices.append(EMPTY)
                vert_numbers[i][j] = vertex
                self.graph.append([])
                self.box_graph.append([])
                if maze[i][j] == 'K' or maze[i][j] == '+':
                    keeper = vertex
                if maze[i][j] == 'B' or maze[i][j] == '*':
                    boxes.append(vertex)
                    self.number_of_boxes += 1
                if maze[i][j] == 'G' or maze[i][j] == '+' or maze[i][j] == '*':
                    self.vertices[vertex] += TARGET
                if maze[i-1][j] != 'W':
                    self.graph[vertex].append((vert_numbers[i-1][j], UP))
                    self.graph[vert_numbers[i-1][j]].append((vertex, DOWN))
                    if maze[i+1][j] != 'W':
                        self.box_graph[vertex].append((vert_numbers[i-1][j], UP))
                    if maze[i-2][j] != 'W':
                        self.box_graph[vert_numbers[i-1][j]].append((vertex, DOWN))
                if maze[i][j-1] != 'W':
                    self.graph[vertex].append((vert_numbers[i][j-1], LEFT))
                    self.graph[vert_numbers[i][j-1]].append((vertex, RIGHT))
                    if maze[i][j+1] != 'W':
                        self.box_graph[vertex].append((vert_numbers[i][j-1], LEFT))
                    if maze[i][j-2] != 'W':
                        self.box_graph[vert_numbers[i][j-1]].append((vertex, RIGHT))
                vertex += 1

        self.size = vertex
        self.original_state_boxes = boxes
        self.original_state_keeper = keeper
        self.distances = []
        for i in range(0, self.size):
            self.distances.append(1e9)
        self.calculate_distances()
        self.reachable_vertices = []
        for v in self.vertices:
            self.reachable_vertices.append(False)

    def calculate_distances(self):
        dist = []
        for i in range(0, self.size):
            dist.append(-1)
        q = queue.Queue()
        for i in range(0, self.size):
            q.put(i)
            dist[i] = 0
            while True:
                if q.empty():
                    self.distances[i] = int(1e9)
                    break
                v = q.get()
                if self.vertices[v] == TARGET:
                    self.distances[i] = dist[v]
                    break
                for edge in self.box_graph[v]:
                    if dist[edge[0]] == -1:
                        dist[edge[0]] = dist[v]+1
                        q.put(edge[0])
            for j in range(0, self.size): dist[j] = -1
            q = queue.Queue()

    def move_possibility(self, origin, direction):
        for edge in self.graph[origin]:
            if edge[1] == direction: return True
        return False

    def move_destination(self, origin, direction):
        for edge in self.graph[origin]:
            if edge[1] == direction: return edge[0]


maze = Maze()


class State:
    def __init__(self, boxes, keeper, previous, direction):
        self.boxes = boxes
        self.keeper = keeper
        self.previous = previous
        self.direction = direction
        self.total_cost = self.predicted_total_cost()

    def __lt__(self, other):
        return self.total_cost < other.total_cost

    def hash(self):
        h = self.keeper
        for b in self.boxes:
            h *= maze.size
            h += b
        return h

    def final(self):
        for b in self.boxes:
            if maze.vertices[b] != TARGET: return False
        return True

    def box(self, position):
        for b in self.boxes:
            if b == position: return True
        return False

    def moved_boxes(self, origin, direction):
        res = self.boxes.copy()
        for i in range(0, len(self.boxes)):
            if self.boxes[i] == origin:
                res[i] = maze.move_destination(origin, direction)
        return res

    def possible_moves(self):
        moves = []
        for edge in maze.graph[self.keeper]:
            target = edge[0]
            direction = edge[1]
            if self.box(target):
                if maze.move_possibility(target, direction) and not self.box(maze.move_destination(target, direction)):
                    moves.append(State(self.moved_boxes(target, direction), target, self, direction))
            else:
                moves.append(State(self.boxes, target, self, direction))
        return moves

    def heurystyka(self):
        sum = 0
        for box in self.boxes:
            sum += maze.distances[box]
        return sum

    def predicted_total_cost(self):
        if self.previous == None:
            return self.heurystyka()
        answ = self.previous.total_cost
        answ -= self.previous.heurystyka()
        answ += self.heurystyka()
        return answ + 1


def direction_to_str(direction):
    if direction == LEFT: return 'L'
    if direction == RIGHT: return 'R'
    if direction == UP: return 'U'
    if direction == DOWN: return 'D'

class Visited:

    def __init__(self):
        self.h = set()

    def visited(self, hash):
        if hash in self.h:
            return True
        return False

    def visit(self, hash):
        self.h.add(hash)


def solve():
    color = Visited()
    counter = 0
    Q = []
    s = State(maze.original_state_boxes, maze.original_state_keeper, None, LEFT)
    heapq.heappush(Q, s)
    color.visit(s.hash())
    while True:
        s = heapq.heappop(Q)
        counter += 1
        m = s.possible_moves()
        for move in m:
            #if color[move.hash()] == 0:
            if not color.visited(move.hash()):
                if move.final():
                    answer = ''
                    while(move != None):
                        answer += direction_to_str(move.direction)
                        move = move.previous
                    answer = answer[:-1]
                    print(counter)
                    return answer[::-1]         # reverse
                if move.heurystyka() >= 1e9:
                    color.visit(move.hash())
                    continue
                heapq.heappush(Q, move)
                color.visit(move.hash())


outfile = open("zad_output.txt", 'w+')
outfile.write(solve())
end = time.time()
print(round(end - start, 6))

