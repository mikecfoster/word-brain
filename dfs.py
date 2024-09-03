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
                #print('search for: {0}'.format(word))
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
    def __init__(self, x, y, letter, parent=None, step=0):
        self.x = x
        self.y = y
        self.letter = letter
        self.parent = parent
        self.step = step
    
    def __repr__(self):
        return "({0},{1},{2},{3},{4})".format(self.x, self.y, self.letter, self.parent, self.step)
    
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
        
    def word_from_node(self, node):
        """ Concatenate letters from the path. The path is based on tracing
            backward through a node based on the 'parent' property.
        """
        print("node: {0}".format(node))
        cell = copy.copy(node)
        word = cell.letter
        while (cell.parent != None):
            cell = cell.parent
            word = cell.letter + word
        print("word-from: {0}".format(word))
        return word


def dfs():
    maze = [
        ['s','e','l','l','b'],
        ['p','r','e','c','i'],
        ['s','u','c','t','e'],
        ['p','t','a','n','t'],
        ['o','l','p','y','u']
    ]
    grid = Grid(maze)
    frontier = PathList()
    explored = set()
    words = []
    start_point = Cell(2,4,grid.letter(2,4))
    max_length = 7
    frontier.path.append(start_point)
    explored.add(start_point)

    while frontier.path:
        cell = frontier.path.pop() #current node
        possible_word = frontier.word_from_node(cell)
        print('possible word: {0}'.format(possible_word))
        if valid_word(possible_word) ==1:
            words.append(possible_word)
        if len(possible_word) < max_length:
            adjacent = grid.adjacent(cell.x, cell.y, possible_word)
            print("adjacent: {0}".format(adjacent))
            if adjacent:
                explored.add(cell)
            for point in adjacent:
                print("explored: {0}".format(explored))
                #if explored.find(point.x, point.y):
                #    continue
                letter = grid.letter(point.x,point.y)
                print("letter: {0}".format(letter))
                next_cell = Cell(point.x, point.y, letter, cell, cell.step+1)
                print("Next cell: {0}".format(next_cell))
                frontier.path.append(next_cell)

    print('Words: ')
    print(words)

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
    return len(rows)


if __name__ == '__main__':
    #bfs()
    dfs()