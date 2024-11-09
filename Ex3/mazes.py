#! /usr/bin/env python3
''' Run cool maze generating algorithms. '''
import random
import heapq

class Cell:
    ''' Represents a single cell of a maze.  Cells know their neighbors
        and know if they are linked (connected) to each.  Cells have
        four potential neighbors, in NSEW directions.
    '''  
    def __init__(self, row, column):
        assert row >= 0
        assert column >= 0
        self.row = row
        self.column = column
        self.links = {}
        self.north = None
        self.south = None
        self.east  = None
        self.west  = None

    def link(self, cell, bidirectional=True):
        ''' Carve a connection to another cell (i.e. the maze connects them)'''
        assert isinstance(cell, Cell)
        self.links[cell] = True
        if bidirectional:
            cell.link(self, bidirectional=False)

    def unlink(self, cell, bidirectional=True):
        ''' Remove a connection to another cell (i.e. the maze 
            does not connect the two cells)
            
            Argument bidirectional is here so that I can call unlink on either
            of the two cells and both will be unlinked.
        '''
        assert isinstance(cell, Cell)
        del self.links[cell]
        if bidirectional:
            cell.unlink(self, bidirectional=False)

    def is_linked(self, cell):
        ''' Test if this cell is connected to another cell.
            
            Returns: True or False
        '''
        assert isinstance(cell, Cell)
        return cell in self.links
        
    def all_links(self):
        ''' Return a list of all cells that we are connected to.'''
        return list(self.links.keys())
        
    def link_count(self):
        ''' Return the number of cells that we are connected to.'''
        return len(self.links)
        
    def neighbors(self):
        ''' Return a list of all geographical neighboring cells, regardless
            of any connections.  Only returns actual cells, never a None.
        '''
        neighbors = [self.north, self.south, self.east, self.west]
        return [neighbor for neighbor in neighbors if neighbor is not None]


    def __str__(self):
        return f'Cell at {self.row}, {self.column}'
        
    def __lt__(self, other):
        ''' A bit of Python magic to make cells compare such that the one
            in a lower row (or lower column if in the same row) will be
            consistently chosen when comparing two cells.  This is useful,
            for instance, when taking cells out of a frontier in "lowest cost"
            fashion.
        '''
        if self.row < other.row:
            return True
        if self.row == other.row and self.column < other.column:
            return True
        return False
        
    def __eq__(self, other):
        ''' Also needed to make comparisons work, based on row/col.'''
        return isinstance(other,type(self)) and \
               self.row == other.row and self.column == other.column
        
    def __hash__(self):
        ''' Must redefine hash, anytime you redefine equality. '''
        return hash(self.row) ^ hash(self.column)
        
class Grid:
    ''' A container to hold all the cells in a maze. The grid is a 
        rectangular collection, with equal numbers of columns in each
        row and vis versa.
    '''

    def __init__(self, num_rows, num_columns):
        assert num_rows > 0
        assert num_columns > 0
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.grid = self.create_cells()
        self.connect_cells()

    def create_cells(self):
        ''' Call the cells into being.  Keep track of them in a list
            for each row and a list of all rows (i.e. a 2d list-of-lists).
            
            Do not connect the cells, as their neighbors may not yet have
            been created.
        '''
        # cells = []
        # for i in range(self.num_rows):
        #    row = []
        #    for j in range(self.num_columns):
        #        row.append(Cell(i, j))
        #    cells.append(row)
        cells = [[Cell(row, col) for col in range(self.num_columns)] for row in range(self.num_rows)]
        return cells

    def connect_cells(self):
        ''' Now that all the cells have been created, connect them to 
            each other - set the north/south/east/west attributes. 
        '''
        # 这个和gpt差不多
        for row in range(self.num_rows):
            for col in range(self.num_columns):
                cell = self.grid[row][col]
                if row > 0:
                    cell.north = self.grid[row - 1][col]
                if row < self.num_rows - 1:
                    cell.south = self.grid[row + 1][col]
                if col > 0:
                    cell.west = self.grid[row][col - 1]
                if col < self.num_columns - 1:
                    cell.east = self.grid[row][col + 1]

    def cell_at(self, row, column):
        ''' Retrieve the cell at a particular row/column index.'''
        if 0 <= row < self.num_rows and 0 <= column < self.num_columns:
            return self.grid[row][column]
        return None

    def deadends(self):
        ''' Return a list of all cells that are deadends (i.e. only link to
            one other cell).
        '''
        # result = []
        # for row in self.grid:
        #     for cell in row:
        #         if len(cell.links) == 1:
        #             result.append(cell)
        # return result
        return [cell for row in self.grid for cell in row if cell.link_count() == 1]

    def each_cell(self):
        ''' A generator.  Each time it is called, it will return one of 
            the cells in the grid.
        '''
        for row in range(self.num_rows):
            for col in range(self.num_columns):
                c = self.cell_at(row, col)
                yield c

    def each_row(self):
        ''' A row is a list of cells.'''
        for row in self.grid:
            yield row

    def random_cell(self):
        ''' Chose one of the cells in an independent, uniform distribution. '''
        row = random.randint(0, self.num_rows - 1)
        col = random.randint(0, self.num_columns - 1)
        return self.grid[row][col]
        
    def size(self):
        ''' How many cells are in the grid? '''
        return self.num_columns * self.num_rows
        
    def set_markup(self, markup):
        ''' Warning: this is a hack.
            Keep track of a markup, for use in representing the grid
            as a string.  It is used in the __str__ function and probably
            shouldn't be used elsewhere.
        '''
        self.markup = markup
        
    def __str__(self):
        ret_val = '+' + '---+' * self.num_columns + '\n'
        for row in self.grid:
            ret_val += '|'
            for cell in row:
                cell_value = self.markup[cell]
                ret_val += '{:^3s}'.format(str(cell_value))
                if not cell.east:
                    ret_val += '|'
                elif cell.east.is_linked(cell):
                    ret_val += ' '
                else:
                    ret_val += '|'
            ret_val += '\n+'
            for cell in row:
                if not cell.south:
                    ret_val += '---+'
                elif cell.south.is_linked(cell):
                    ret_val += '   +'
                else:
                    ret_val += '---+'
            ret_val += '\n'
        return ret_val
        
class Markup:
    ''' A Markup is a way to add data to a grid.  It is associated with
        a particular grid.
        
        In this case, each cell can have a single object associated with it.
        
        Subclasses could have other stuff, of course
    '''

    def __init__(self, grid, default=' '):
        self.grid = grid
        self.marks = {}  # Key: cell, Value = some object
        self.default = default

    def reset(self):
        self.marks = {}
        
    def __setitem__(self, cell, value):
        self.marks[cell] = value
        
    def __getitem__(self, cell):
        return self.marks.get(cell, self.default)
        
    def set_item_at(self, row, column, value):
        assert row >= 0 and row < self.grid.num_rows
        assert column >= 0 and column < self.grid.num_columns
        cell = self.grid.cell_at(row, column)
        if cell:
            self.marks[cell]=value
        else:
            raise IndexError
    
    def get_item_at(self, row, column):
        assert row >= 0 and row < self.grid.num_rows
        assert column >= 0 and column < self.grid.num_columns
        cell = self.grid.cell_at(row, column)
        if cell:
            return self.marks.get(cell)
        else:
            raise IndexError
            
    def max(self):
        ''' Return the cell with the largest markup value. '''
        return max(self.marks.keys(), key=self.__getitem__)

    def min(self):
        ''' Return the cell with the largest markup value. '''
        return min(self.marks.keys(), key=self.__getitem__)

class DijkstraMarkup(Markup):
    ''' A markup class that will run Djikstra's algorithm and keep track
        of the distance values for each cell.
    '''

    def __init__(self, grid, root_cell : Cell, default=0):
        ''' Execute the algorithm and store each cell's value in self.marks[]
        '''
        # 实际上是广搜
        super().__init__(grid, default)
        self[root_cell] = 0
        frontier = [(0, root_cell)]

        while len(frontier) > 0:
            dist, cell = heapq.heappop(frontier)

            if (dist > self[cell]):
                continue

            for neighbor in cell.all_links():
                if (neighbor not in self.marks or dist + 1 < self[neighbor]):
                    self[neighbor] = dist + 1
                    heapq.heappush(frontier, (dist + 1, neighbor))

    def farthest_cell(self):
        ''' Find the cell with the largest markup value, which will
            be the one farthest away from the root_call.
            
            Returns: Tuple of (cell, distance)
        '''
        cell = max(self.marks, key=self.marks.get)
        return (cell, self[cell])

class ShortestPathMarkup(DijkstraMarkup):
    ''' Given a starting cell and a goal cell, create a Markup that will
        have the shortest path between those two cells marked.  
    '''

    def __init__(self, grid, start_cell, goal_cell, 
                 path_marker='*', non_path_marker=' ', end_marker='^'):
        super().__init__(grid, start_cell)
        
        path = {}
        for cell in self.grid.each_cell():
            path[cell] = non_path_marker

        current = goal_cell
        while current is not start_cell:
            path[current] = path_marker
            # for link in current.all_links():
            #     if self[link] < self[current]:
            #         current = link
            current = min([neighbor for neighbor in current.all_links()], key = lambda cell: self.marks[cell])

        path[start_cell] = end_marker
        path[goal_cell] = end_marker
        self.marks = path

class LongestPathMarkup(ShortestPathMarkup):
    ''' Create a markup with the longest path in the graph marked.
        Note: Shortest path is dependent upon the start and target cells chosen.
              This markup is the longest path to be found _anywhere_ in the maze.
    '''

    def __init__(self, grid, path_marker='*', non_path_marker=' ', end_marker='^'):
        start_cell = grid.random_cell()
        dm = DijkstraMarkup(grid, start_cell)
        farthest, _ = dm.farthest_cell()
        dm = DijkstraMarkup(grid, farthest)
        next_farthest, _ = dm.farthest_cell()   
        super().__init__(grid, farthest, next_farthest, path_marker, non_path_marker, end_marker)

class ColorizedMarkup(Markup):
    ''' Markup a maze with various colors.  Each value in the markup is
        an RGB triplet.
    '''

    def __init__(self, grid, channel='R'):
        assert channel in 'RGB'
        super().__init__(grid)
        self.channel = channel
        
    def colorize_dijkstra(self, start_row = None, start_column = None):
        ''' Provide colors for the maze based on their distance from
            some cell.  By default, from the center cell.
        '''
        if not start_row:
            start_row = self.grid.num_rows // 2
        if not start_column:
            start_column = self.grid.num_columns // 2
        start_cell = self.grid.cell_at(start_row, start_column)
        dm = DijkstraMarkup(self.grid, start_cell)
        self.intensity_colorize(dm)
                
    def intensity_colorize(self, markup):
        ''' Given a markup of numeric values, colorize based on
            the relationship to the max numeric value.
        '''
        max = markup.max()
        max_value = markup[max]
        for c in self.grid.each_cell():
            cell_value = markup[c]
            intensity = (max_value - cell_value) / max_value
            dark   = round(255 * intensity)
            bright = round(127 * intensity) + 128
            if self.channel == 'R':
                self.marks[c] = [bright, dark, dark]
            elif self.channel == 'G':
                self.marks[c] = [dark, bright, dark]
            else:
                self.marks[c] = [dark, dark, bright]   
                                       
def binary_tree(grid : Grid):
    ''' The Binary Tree Algorithm.
      
        This algorithm works by visiting each cell and randomly choosing
        to link it to the cell to the east or the cell to the north.
        If there is no cell to the east, then always link to the north
        If there is no cell to the north, then always link to the east.
        Except if there are no cells to the north or east (in which case
        don't link it to anything.)
    '''
    for cell in grid.each_cell():
        # if cell.east is None and cell.north is None:
        #     continue
        # if cell.east is None:
        #     cell.link(cell.north)
        #     continue
        # if cell.north is None:
        #     cell.link(cell.east)
        #     continue
        # cell.link(random.choice(cell.neighbors()))
        neighbors = []
        if cell.north:
            neighbors.append(cell.north)
        if cell.east:
            neighbors.append(cell.east)
        if neighbors:
            cell.link(random.choice(neighbors))

def sidewinder(grid, odds=.5):
    ''' The Sidewinder algorithm.
    
        Considers each row, one at a time.
        For each row, start with the cell on the west end and an empty list 
        (the run).  Append the cell to the run list.
        Choose a random number between 0 and 1.  If it is greater 
        than the odds parameter, then add the eastern cell to the run list and
        link it to the current cell.  That eastern cell then becomes the 
        current cell.
        If the random number was less than the odds parameter, then you are
        done with the run.  Choose one of the cells in the run and link it to 
        the cell to the north.
        
        Be careful, these instructions don't cover the cases where the row
        is the northernmost one (which will need to be a single, linked run) 
        or for cells at the far east (which automatically close the run)
    '''
    assert odds >= 0.0
    assert odds < 1.0    
    for row in grid.each_row():
        run = []
        for cell in row:
            run.append(cell)
            if (cell.row == 0 or random.random() > odds) and cell.east:
                cell.link(cell.east)
            elif cell.row > 0:
                cell = random.choice(run)
                cell.link(cell.north)
                run = []

def aldous_broder(grid):
    ''' The Aldous-Broder algorithm is a random-walk algorithm.
    
        Start in a random cell.  Choose a random direction.  If the cell
        in that direction has not been visited yet, link the two cells.
        Otherwise, don't link.
        Move to that randomly chosen cell, regardless of whether it was
        linked or not.
        Continue until all cells have been visited.
    '''
    current = grid.random_cell()
    visited = [current]
    iteration_count = 0
    while (len(visited) < grid.size()):
        neighbor = random.choice(current.neighbors())
        
        if neighbor not in visited:
            neighbor.link(current)
            visited.append(neighbor)
        current = neighbor
        iteration_count += 1
    print(f'Aldous-Broder executed on a grid of size {grid.size()} in {iteration_count} steps.')
    
def wilson(grid):
    ''' Wilson's algorithm is a random-walk algorithm.
    
        1) Choose a random cell.  Mark it visited.
        2) Choose a random unvisited cell (note, this will necessarily not be the 
          same cell from step 1).  Perform a "loop-erased" random walk until
          running into a visited cell.  The cells chosen during this random
          walk are not yet marked as visited.
        3) Add the path from step 2 to the maze.  Mark all of the cells as visited.
          Connect all the cells from the path, one to each other, and to the 
          already-visited cell it ran into.
        4) Repeat steps 2 and 3 until all cells are visited.
        
        Great.  But, what is a "loop-erased" random walk?  At each step, one 
        random neighbor gets added to the path (which is kept track
        of in order).  Then, check if the neighbor is already in the path.  If 
        so, then the entire loop is removed from the path.  So, if the 
        path consisted of cells at locations (0,0), (0,1), (0,2), (1,2), (1,3),
        (2,3), (2,2), and the random neighbor is (1,2), then there is a loop.
        Chop the path back to (0,0), (0,1), (0,2), (1,2) and continue 
        
        BTW, it  may be easier to manage a  list of unvisited cells, which 
        makes it simpler to choose a random unvisited cell, for instance.   
    '''
    unvisited = [cell for cell in grid.each_cell()]
    unvisited.remove(grid.random_cell())
    
    random_choices = 0
    loops_removed = 0

    while len(unvisited) > 0:
        start = random.choice(unvisited)
        path = [start]

        while path[-1] in unvisited:
            next = random.choice(path[-1].neighbors())
            random_choices += 1

            if next in path:
                while path[-1] != next:
                    path.pop()
                loops_removed += 1
            else:
                path.append(next)

        for i in range(len(path) - 1):
            path[i].link(path[i + 1])
            unvisited.remove(path[i])

    print(f'Wilson executed on a grid of size {grid.size()} with {random_choices}', end='')
    print(f' random cells choosen and {loops_removed} loops removed')

def hybrid(grid, threshold = 0.5):
    current = grid.random_cell()
    unvisited = [cell for cell in grid.each_cell()]
    unvisited.remove(current)
    random_choices = 0
    loops_removed = 0
    
    while (len(unvisited) > grid.size() * threshold):
        neighbor = random.choice(current.neighbors())
        random_choices += 1
        
        if neighbor in unvisited:
            neighbor.link(current)
            unvisited.remove(neighbor)
        current = neighbor

    while len(unvisited) > 0:
        start = random.choice(unvisited)
        path = [start]

        while path[-1] in unvisited:
            next = random.choice(path[-1].neighbors())
            random_choices += 1

            if next in path:
                while path[-1] != next:
                    path.pop()
                loops_removed += 1
            else:
                path.append(next)

        for i in range(len(path) - 1):
            path[i].link(path[i + 1])
            unvisited.remove(path[i])

    print(f'Wilson executed on a grid of size {grid.size()} with {random_choices}', end='')
    print(f' random cells choosen and {loops_removed} loops removed')


def recursive_backtracker(grid, start_cell=None):
    ''' Recursive Backtracker is a high-river maze algorithm.
    
        1) if start_cell is None, choose a random cell for the start
        2) Examine all neighbors and make a list of those that have not been visited
           Note: you can tell it hasn't been visited if it is not linked to any cell
        3) Randomly choose one of the cells from this list.  Link to and move to that 
           neighbor
        3a) If there are no neighbors in the list, then you must backtrack to the last
            cell you visited and repeat.
            
        Suggestion: Use an explicit stack.  You can write this implicitly (in fact,
        the code will be quite short), but for large mazes you will be making lots of 
        function calls and you risk running out of stack space.
    '''
    if not start_cell:
        start_cell = grid.random_cell()
    visited = [start_cell]
    stack = [start_cell]
    while stack:
        current = stack[-1]
        unvisited_neighbors = [neighbor for neighbor in current.neighbors() if neighbor not in visited]
        if unvisited_neighbors:
            neighbor = random.choice(unvisited_neighbors)
            current.link(neighbor)
            visited.append(neighbor)
            stack.append(neighbor)
        else:
            stack.pop()