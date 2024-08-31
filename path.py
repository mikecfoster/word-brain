from collections import deque, namedtuple

# https://www.redblobgames.com/grids/line-drawing.html

class Grid:
    """ A 2D grid organised as a list of lists, a cell value of 0 
        is walkable. The grid is zero based; 0,0 is top left. """
    def __init__(self, grid):
        self.grid = grid

    def is_walkable(self, x, y):
        if x >= 0 and x < len(self.grid[0]):
            if y >= 0 and y < len(self.grid):
                return self.grid[y][x] == 0
        return False
    
    def adjacent(self, x, y):
        """ return a list of adjcent cells as a list of tuples """
        cells = []
        point = namedtuple('point', ['x', 'y'])
        if self.is_walkable(x+1, y):
            cells.append(point(x+1, y))
            print('walkable x+1')
        if self.is_walkable(x-1, y):
            cells.append(point(x-1, y))
            print('walkable x-1')
        if self.is_walkable(x, y+1):
            cells.append(point(x, y+1))
            print('walkable y+1')
        if self.is_walkable(x, y-1):
            cells.append(point(x, y-1))
            print('walkable y-1')
        return cells
    
    def visualise(self,path=None):
        """ visualise the maze overlayed with the search path """
        for y in range(len(self.grid)):
            line = ''
            for x in range(len(self.grid[y])):
                if (trace := path.find(x, y)):
                    line +=str(trace.step).rjust(2)+' '
                else:
                    line += ' . ' if self.is_walkable(x, y) else ' X '
            print(line)   


class Cell:
    """ a single cell in a grid with x, y and weight attributes """
    def __init__(self, x, y, step=0):
        self.x = x
        self.y = y
        self.step = step
    
    def __repr__(self):
        return "({0},{1},{2})".format(self.x, self.y, self.step)
    
class PathList:
    """ a collection of Cells """
    def __init__(self):
        self.path = deque()
    
    def find(self, x ,y):
        """ find a cell with x and y in the list and return instance of Cell """
        for cell in self.path:
            if (cell.x == x) and (cell.y == y):
                return cell
        return False
    
def find_path():
    maze = [
        [0,0,0,1,1,0,1,0,0,1],
        [0,1,0,0,1,0,0,0,1,0],
        [0,1,1,0,0,0,1,0,1,1],
        [0,1,0,0,1,0,0,0,0,0],
        [0,0,0,1,1,0,1,0,0,0],
        [0,1,0,0,1,0,1,0,0,0],
        [0,1,1,0,0,0,1,0,1,0],
        [0,0,0,0,1,0,0,0,1,0]
    ]
    grid = Grid(maze)
    path = PathList()
    start_point = Cell(9,3)
    objective = Cell(2,5)
    path.path.appendleft( objective )
    found = False
    finished_searching = False

    while not (found or finished_searching):
        path_length = len(path.path)
        search_path = path.path.copy()
        for cell in search_path:
            adjacent = grid.adjacent(cell.x, cell.y)
            print(adjacent)
            for point in adjacent:
                if path.find(point.x, point.y):
                    continue
                path.path.append(Cell(point.x, point.y, cell.step+1))
        found = path.find(start_point.x, start_point.y)
        if len(path.path) == path_length:
            finished_searching = True
    
    print(path.path)
    print('Found {0}'.format(found)) if found else print('Not found')
    grid.visualise(path)

# defined as a global type
Point = namedtuple('point', ['x', 'y'])

def los():
    """ find x,y pairs to line-of-sight """
    start = Point(0,0)
    finish = Point(7,3)
    print(line(start, finish))
    print(line(Point(9,5),Point(3,3)))

def line(p0, p1):
    points = []
    N = diagonal_distance(p0, p1)
    for step in range(1,N):
        t = 0.00 if N == 0 else (step / N)
        points.append(round_point(lerp_point(p0, p1, t)))
    return points

def diagonal_distance(p0, p1):
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    return max(abs(dx),abs(dy))

def round_point(p):
    return Point(round(p.x),round(p.y))

def lerp_point(p0, p1, t):
    return Point(lerp(p0.x, p1.x , t), lerp(p0.y, p1.y, t))

def lerp(start, end, t):
    return start + t * (end-start)

if __name__ == '__main__':
    find_path()
    los()
