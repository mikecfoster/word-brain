from collections import deque, namedtuple
import sqlite3
import copy
import dictionary

# Search for words to help sove WordBrain puzzles

class Grid:
    """ A 2D grid organised as a list of lists of letters, 
        a non-null cell value is walkable. 
        The grid is zero based; 0,0 is top left. """
    def __init__(self, grid):
        self.grid = grid

    def is_walkable(self, x, y):
        if x >= 0 and x < len(self.grid[0]):
            if y >= 0 and y < len(self.grid):
                if self.grid[y][x] == '':
                    return False
                return True
        return False
    
    def letter(self, x, y):
        if x >= 0 and x < len(self.grid[0]):
            if y >= 0 and y < len(self.grid):
                return self.grid[y][x]
        return ''
    
    def adjacent(self, x, y):
        """ return a list of adjcent cells as a list of tuples """
        cells = []
        point = namedtuple('point', ['x', 'y'])
        if self.is_walkable(x+1, y):
            cells.append(point(x+1, y))
        if self.is_walkable(x-1, y):
            cells.append(point(x-1, y))
        if self.is_walkable(x, y+1):
            cells.append(point(x, y+1))
        if self.is_walkable(x, y-1):
            cells.append(point(x, y-1))
        if self.is_walkable(x-1, y-1):
            cells.append(point(x-1, y-1))
        if self.is_walkable(x+1, y+1):
            cells.append(point(x+1, y+1))
        if self.is_walkable(x+1, y-1):
            cells.append(point(x+1, y-1))
        if self.is_walkable(x-1, y+1):
            cells.append(point(x-1, y+1))
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
    
    def cell_as_token(self):
        """ tokenise a cell x,y reference. 3,4 becomes 003004 """
        return "{:0>2}{:0>2}".format(self.x, self.y)
    
    def token_from_path(self):
        """ Create a tokenised string of the path to use as a unique 
            identifier.
        """
        token = ""
        cell:Cell = copy.copy(self)
        token = cell.cell_as_token()
        while (cell.parent != None):
            cell = cell.parent
            token = cell.cell_as_token() + '-' + token
        return token
    
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
        cell = copy.copy(node)
        word = cell.letter
        while (cell.parent != None):
            cell = cell.parent
            word = cell.letter + word
        return word


def dfs(conn, maze, start_x, start_y, target_length):
    grid = Grid(maze)
    frontier = PathList()
    explored_paths = set()
    words = []
    start_point = Cell(start_x,start_y,grid.letter(start_x,start_y))
    frontier.path.append(start_point)

    while frontier.path:
        cell:Cell = frontier.path.pop() #current node
        path_token = cell.token_from_path()
        if path_token in explored_paths:
            continue
        possible_word = frontier.word_from_node(cell)
        (valid_word , word_count) = validate_word(conn, possible_word)
        if word_count ==0:
            continue
        if  valid_word and len(possible_word) == target_length:
            words.append(possible_word)
            explored_paths.add(path_token)
            #print('possible word: {0} ({1}) {2} {3}'.format(possible_word, word_count, valid_word, explored_paths))
        if len(possible_word) < target_length:
            adjacent = grid.adjacent(cell.x, cell.y)
            if adjacent:
                explored_paths.add(path_token)
            for point in adjacent:
                letter = grid.letter(point.x,point.y)
                next_cell = Cell(point.x, point.y, letter, cell, cell.step+1)
                cell_token = next_cell.cell_as_token()
                if cell_token not in path_token:
                    frontier.path.append(next_cell)

    print('Words: ')
    print(words)

# defined as a global type
Point = namedtuple('point', ['x', 'y'])

def validate_word(conn, word):
    """ create a database connection to an SQLite database """
    rows = []
    try:
        cursor = conn.cursor()
        # check if a word is in the dictionary
        search = word
        sql = """ select * from words where word = (?) """
        cursor.execute(sql, (search,))
        rows = cursor.fetchone()
        valid_word = True if rows and len(rows) == 1 else False
        # check if there are words beginning with 
        search = word+'%'
        sql = """ select count(*) from words where word like (?) """
        cursor.execute(sql, (search,))
        rows = cursor.fetchone()
        word_count = rows[0] if len(rows) == 1 else 0
    except sqlite3.Error as e:
        print(e)

    return (valid_word, word_count)

def create_dictionary():
    conn = None
    filename = 'words_alpha.txt'

    try:
        conn = sqlite3.connect(':memory:')
        print(sqlite3.sqlite_version)
    except sqlite3.Error as e:
        print(e)
    
    sql_drop_table = """
        DROP TABLE IF EXISTS words;
    """
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS words ( word TEXT );
        """

    # create a database connection
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql_drop_table)
            cursor.execute(sql_create_table)
            conn.commit()
            print("table 'words' created")
    except sqlite3.Error as e:
        print(e)

    print("Adding words to the dictionary")
    try:    
        with open(filename) as word_file:
            for word in word_file.read().split():
                sql = ''' INSERT INTO words VALUES (?) '''
                cursor.execute(sql, (word,))
            conn.commit()  
    except sqlite3.Error as e:
        print(e)

    return conn

if __name__ == '__main__':
    conn = create_dictionary()
    #bfs()
    maze = [
        ['g','n','e','',''],
        ['w','i','r','a',''],
        ['r','o','s','u',''],
        ['r','a','d','o',''],
        ['l','f','i','n','']
    ]

    # dfs(conn, maze, 2, 3, 3) # find the word 'tie'

    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] != '':
                letter = maze[y][x]
                print("x,y {0},{1} = {2}".format(x,y,letter))
                dfs(conn, maze, x, y, 8)