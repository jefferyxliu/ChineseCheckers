#!/usr/bin/env python
# coding: utf-8
import turtle
class Tile:
    def __init__(self, x, y, z):
        #Hexagonal Coordinate System. Uses lattice points (x,y,z) confined to the plane x+y+z = 0
        #
        #e.g.:
        #    (0,-1,1) (-1,0,1)
        #
        #(1,-1,0) (0,0,0) (-1,1,0)
        #
        #    (1,0,-1) (0,1,-1)
        if x + y + z != 0: #projects z to the plane if not on plane.
            z = -x - y
        
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return '({}, {}, {})'.format(self.x, self.y, self.z)
    
    def __repr__(self):
        return str(self)

    def triple(self):
        return self.x, self.y, self.z
    
    #Hash:
    def __hash__(self):
        return hash((self.x,self.y))
        #Every Tile is uniquely determined by its x and y coordinate, so that tuple is used for the hash.
        #This is necessary for creating sets of Tiles.
    
    #Possibly Useful Operations (essentially vector operations):
    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)
    
    def __sub__(self, other):
        return Tile(self.x - other.x, self.y - other.y, self.z-other.z)
    
    def __neg__(self):
        return Tile(-self.x, -self.y, -self.z)
    
    def __add__(self, other):
        return Tile(self.x - other.x, self.y - other.y, self.z-other.z)
    
    #Scalar Multiplication:
    def __mul__(self, other):
        return Tile(self.x * other, self.y * other, self.z * other)
    
    #Rectilinear or 'Taxicab' Distance. Adjacent tiles have distance 1:
    def distance(self, other): 
        return (abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z-other.z))//2

    #Returns the coordinates of the hexagonal coordinate system mapped to a 2D plane.
    def rect(self, index = 2, sgn = -1):
         
        x = sgn*(self.x, self.y, self.z)[(index+1)%3]
        y = sgn*(self.y, self.z, self.x)[(index+1)%3]
        
        return (x-y, x+y) #second coordinate should be multiplied by sqrt 3 when drawn to preserve lengths.

    
class ChineseCheckers:
    def __init__(self):
        #Pieces and location stored in dict in the form {color: [tile1,tile2,tile3,...,tile10]}
        self.pieces = {}
        
        #Home tile is the vertex in the starting triangle farthest from center. In the form {color: tile}
        #used to check for the win condition
        self.home = {}
        
    
        #Six cardinal directions:
        #useful for adding to tile to get adjacent tiles.
        self.directions = [Tile(1,0,-1),Tile(0,1,-1),Tile(-1,0,1),Tile(0,-1,1),Tile(1,-1,0),Tile(-1,1,0)]
        self.playing = False
        self.drawn = False
        
        
    def set_up(self, gamemode = 2):
        self.reset()
        #Different setups (gamemode is number of players/colors, default 2):
        if gamemode == 2:
            self.pieces['red'] = []
            self.pieces['blue'] = []
            for x in range(1,5):
                for y in range(5-x,5):
                    self.pieces['red'].append(Tile(x,y,-x-y))
                    self.pieces['blue'].append(Tile(-x,-y,x+y))
            self.home['red'] = Tile(4,4,-8)
            self.home['blue'] = Tile(-4,-4,8)
            
        if gamemode == 3:
            self.pieces['red'] = []
            self.pieces['blue'] = []
            self.pieces['green'] = []
            for x in range(1,5):
                for y in range(5-x,5):
                    self.pieces['red'].append(Tile(x,y,-x-y))
                    self.pieces['blue'].append(Tile(-x-y,x,y))
                    self.pieces['green'].append(Tile(y,-x-y,x))
            self.home['red'] = Tile(4,4,-8)
            self.home['blue'] = Tile(-8,4,4)
            self.home['green'] = Tile(4,-8,4)
            
        if gamemode == 4:
            self.pieces['red'] = []
            self.pieces['blue'] = []
            self.pieces['green'] = []
            self.pieces['yellow'] = []
            for x in range(1,5):
                for y in range(5-x,5):
                    self.pieces['red'].append(Tile(x,y,-x-y))
                    self.pieces['blue'].append(Tile(-x,-y,x+y))
                    self.pieces['green'].append(Tile(y,-x-y,x))
                    self.pieces['yellow'].append(Tile(-y,x+y,-x))
            self.home['red'] = Tile(4,4,-8)
            self.home['blue'] = Tile(-4,-4,8)
            self.home['green'] = Tile(4,-8,4)
            self.home['yellow'] = Tile(-4,8,-4)
        
        if gamemode == 6:
            self.pieces['red'] = []
            self.pieces['blue'] = []
            self.pieces['green'] = []
            self.pieces['yellow'] = []
            self.pieces['cyan'] = []
            self.pieces['magenta'] = []
            for x in range(1,5):
                for y in range(5-x,5):
                    self.pieces['red'].append(Tile(x,y,-x-y))
                    self.pieces['blue'].append(Tile(-x,-y,x+y))
                    self.pieces['green'].append(Tile(y,-x-y,x))
                    self.pieces['yellow'].append(Tile(-y,x+y,-x))
                    self.pieces['cyan'].append(Tile(-x-y,x,y))
                    self.pieces['magenta'].append(Tile(x+y,-x,-y))
            self.home['red'] = Tile(4,4,-8)
            self.home['blue'] = Tile(-4,-4,8)
            self.home['green'] = Tile(4,-8,4)
            self.home['yellow'] = Tile(-4,8,-4)
            self.home['cyan'] = Tile(-8,4,4)
            self.home['magenta'] = Tile(8,-4,-4)
        self.playing = True
                    
    def reset(self):
        self.playing = False
        self.pieces = {}
        self.home = {}
     
    def __repr__(self):
        return str(self.pieces)
    
    #Mathematically defined boundaries, the union of two large equilateral triangles to get hexagram:
    def in_bounds(self, tile):
        return (tile.x <= 4 and tile.y <= 4 and tile.z <= 4) or (tile.x >= -4 and tile.y >= -4 and tile.z >= -4)
    
    #Useful test functions:
    def occupied_tiles(self):
        occupied = []
        for x in self.pieces.values():
            occupied.extend(x)
        return occupied
    
    def is_occupied(self, tile):
        return tile in self.occupied_tiles()
    
    def is_empty(self, tile): 
        return tile not in self.occupied_tiles()
        
    #Moving pieces:
    #first tests if move is legal (see below)
    def move(self, loc, dest):
        if self.in_bounds(dest):
            for color in self.pieces:
                for i in range(len(self.pieces[color])):
                    if self.pieces[color][i] == loc:
                        self.pieces[color][i] = dest
    
    #Finding all possible connected 'jumps' from a given tile:
    #builds the set of connected tiles (ensures no duplication)
    #keeps checking all 6 jump directions
    #only checks 'new' adjacent tiles for efficiency
    #terminates when no new tiles are found
    def connection(self, tile):
        connected = set()
        new = set([tile])
        
        while len(new) > 0:
            connected.update(new)
            for x in new.copy():
                for direction in self.directions:
                    if self.is_occupied(x + direction) and self.in_bounds(x+direction*2) and self.is_empty(x+direction*2):
                        new.add(x+direction*2)
            new = new - connected
        
        return connected
    
    #Test for legal moves:
    #move must be to adjacent tile or tile connected by jumps
    def is_legal(self, loc, dest):
        if self.is_occupied(loc):
            if self.is_empty(dest) and self.in_bounds(dest):
                if loc.distance(dest)==1:
                    return True, 'step'
                elif dest in self.connection(loc)-set([loc]):
                    return True, 'jump'
                
                else:
                    return False, 'no path found'
            else:
                return False, 'destination occupied or out of bound'
                
        else:
            return False, 'no piece to move'
    
    #Win condition:
    #if all pieces are more than distance 12 from start, they must be in the opposite triangle, assuming they are in bounds.
    def has_won(self, color):
        return all([piece.distance(self.home[color]) > 12 for piece in self.pieces[color]])

    #Returns a dictionary of pieces with in rectangular coordinates remember multiply second coordinate by sqrt(3) to preserve length.
    #Send this to client after a move. Client draw on Tkinter canvas.
    def to_plane(self, home):
        for i in range(3):
            if abs(home.triple()[i]) == 8:
                index = i
                sgn = home.triple()[i]//8

        self.plane = {}
        for color in self.pieces:
            self.plane[color] = [tile.rect(index, sgn) for tile in self.pieces[color]]
        return self.plane

    #Test drawing with turtle graphics.
    def draw(self, home):
        if not self.drawn:
            self.turtle = turtle.Turtle()
            self.turtle.speed(10)
            self.turtle.hideturtle()
            self.drawn = True
        pieces = self.to_plane(home)
        self.turtle.clear()
        for color in pieces:
            for x in pieces[color]:
                self.turtle.penup()
                self.turtle.goto(20*x[0], 20*1.73*x[1])
                self.turtle.pendown()
                self.turtle.dot(25,color)
                
            
            
        
        








#Example
'''
C = ChineseCheckers()
print(C.pieces['red'])
print(C.connection(C.pieces['red'][4]))
C.move(Tile(3, 3, -6),Tile(3, 1, -4))


print(C.pieces['red'][4])
print(C.has_won('red'))
print(C.pieces['red'][4].distance(C.home['red']))
'''




