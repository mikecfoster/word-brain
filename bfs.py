from collections import deque, namedtuple
import sqlite3
import copy

# Search for words to help sove WordBrain puzzles

class Grid:
    """ A 2D grid organised as a list of lists of letters, 
        a non-null cell value is walkable. 
        The grid is zero based; 0,0 is top left. """
    def __init__(self, grid):
        self.grid = grid

    def is_walkable(self, x, y, partial_word):
        if x >= 0 and x < len(self.grid[0]):
            if y >= 0 and y < len(self.grid):
                if self.grid[y][x] == '':
                    return False
                word = partial_word + self.grid[y][x]
                print('search for: {0}'.format(word))
                if valid_word(word):
                    return True
        return False
    
    def letter(self, x, y):
        if x >= 0 and x < len(self.grid[0]):
            if y >= 0 and y < len(self.grid):
                return self.grid[y][x]
        return ''
    
    def adjacent(self, x, y, partial_word):
        """ return a list of adjcent cells as a list of tuples """
        cells = []
        point = namedtuple('point', ['x', 'y'])
        if self.is_walkable(x+1, y, partial_word):
            cells.append(point(x+1, y))
            #print('walkable x+1')
        if self.is_walkable(x-1, y, partial_word):
            cells.append(point(x-1, y))
            #print('walkable x-1')
        if self.is_walkable(x, y+1, partial_word):
            cells.append(point(x, y+1))
            #print('walkable y+1')
        if self.is_walkable(x, y-1, partial_word):
            cells.append(point(x, y-1))
            #print('walkable y-1')
        if self.is_walkable(x-1, y-1, partial_word):
            cells.append(point(x-1, y-1))
            #print('walkable x-1, y-1')
        if self.is_walkable(x+1, y+1, partial_word):
            cells.append(point(x+1, y+1))
            #print('walkable x+1, y+1')
        if self.is_walkable(x+1, y-1, partial_word):
            cells.append(point(x+1, y-1))
            #print('walkable x+1, y-1')
        if self.is_walkable(x-1, y+1, partial_word):
            cells.append(point(x-1, y+1))
            #print('walkable x-1, y+1')
        return cells
    
    def visualise(self,path=None):
        """ visualise the maze overlayed with the search path """
        for y in range(len(self.grid)):
            line = ''
            for x in range(len(self.grid[y])):
                if (trace := path.find(x, y)):
                    line +=str(trace.step).rjust(2)+' '
                else:
                    line += ' . ' if self.grid[y][x] != '' else ' X '
            print(line)   


class Cell:
    """ a single cell in a grid with x, y and weight attributes """
    def __init__(self, x, y, letter, step=0):
        self.x = x
        self.y = y
        self.letter = letter
        self.step = step
    
    def __repr__(self):
        return "({0},{1},{2},{3})".format(self.x, self.y, self.letter, self.step)
    
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
    
    def word_from_path(self):
        """ concatenate letters from the path and check that it forms an entire word 
            or the start of a valid word from the dictionary.
        """
        word = ""
        for cell in self.path:
            word += cell.letter
        return word         
    

def bfs():
    maze = [
        ['s','e','l','l','b'],
        ['p','r','e','c','i'],
        ['s','u','c','t','e'],
        ['p','t','a','n','t'],
        ['o','l','p','y','u']
    ]
    grid = Grid(maze)
    path = PathList()
    start_point = Cell(2,4,grid.letter(2,4))
    max_length = 7
    # objective = Cell(2,5)
    path.path.appendleft( start_point )
    found = False
    finished_searching = False

    while not (found or finished_searching):
        path_length = len(path.path)
        search_path = path.path.copy()
        partial_word = path.word_from_path()
        print('partial word: {0}'.format(partial_word))
        for cell in search_path:
            adjacent = grid.adjacent(cell.x, cell.y, partial_word)
            for point in adjacent:
                if path.find(point.x, point.y):
                    continue
                letter = grid.letter(point.x,point.y)
                path.path.append(Cell(point.x, point.y, letter, cell.step+1))
        # found = path.find(start_point.x, start_point.y)
        if (len(path.path) == path_length) or (len(path.path) == max_length):
            finished_searching = True
        print('Path: ')
        print(path.path)
    
    print(path.path)
    grid.visualise(path)

# defined as a global type
Point = namedtuple('point', ['x', 'y'])

def valid_word(word):
    """ create a database connection to an SQLite database """
    db = "dictionary.db"
    conn = None
    rows = []
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        search = word+'%'
        sql = """ select count(*) from words where word like (?) """
        cursor.execute(sql, (search,))
        rows = cursor.fetchone()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return True if rows[0]>0 else False


if __name__ == '__main__':
    bfs()