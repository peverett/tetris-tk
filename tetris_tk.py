#!/usr/bin/env python

# TODO: Game over logic
# TODO: COORD CLASS WITH ADD SUBTRACT EQUALS (possibly)
# TODO: Whole file PEP8 coding style
# TODO: TBoard that centres the shape exactly
# TODO: Add version and Author vars
# TODO: Doesn't clear to the top line.

"""
Tetris Tk - A tetris clone written in Python using the Tkinter GUI library.

Controls:
    Left Arrow      Move left
    Right Arrow     Move right
    Down Arrow      Move down
    Up Arrow        Drop Tetronimoe to the bottom
    'a'             Rotate anti-clockwise (to the left)
    'b'             Rotate clockwise (to the right)
    'p'             Pause the game.
"""

from Tkinter import *
import tkFont
from random import randint
import tkMessageBox
import sys
from collections import namedtuple

SCALE = 30
OFFSET = 3
MAXX = 10
MAXY = 22

NO_OF_LEVELS = 10

LEFT = "left"
RIGHT = "right"
DOWN = "down"

direction_d = { "left": (-1, 0), "right": (1, 0), "down": (0, 1) }

# Game States
READY = "READY"
GAME_OVER = "GAME OVER"
PAUSED = "PAUSED"
PLAYING = "PLAYING"

Coord = namedtuple("Coord", ['x', 'y'])


def level_thresholds( first_level, no_of_levels ):
    """
    Calculates the score at which the level will change, for n levels.
    """
    thresholds =[]
    for x in xrange( no_of_levels ):
        multiplier = 2**x
        thresholds.append( first_level * multiplier )
    
    return thresholds


class TBoard(Frame):
    """
    A Frame containing a Canvas, on which blocks can be displayed, moved and deleted, at will. A block is just a Canvas
    rectangle. Tetrominoes are made up of blocks.

    This is simplifying the Canvas object so that the blocks can be placed and manipulated by coordinated in an
    X, Y Grid, and this class will scale them appropriately.
    """
    def __init__(self, parent, scale, max_x, max_y, offset):
        """
        Created the TBoard. It is up to the creator to Pack/Grid this.
        :param parent: The parent TKinter object
        :param scale: Scale e.g. scale an x by y 'block' by 'scale' pixels.
        :param max_x: max X coordinate
        :param max_y: max Y coordinate
        :param offset: Offset from top left for block creation.
        """
        Frame.__init__(self, parent)
        self.parent = parent
        self.scale = scale
        self.max_x = max_x
        self.max_y = max_y
        self.offset = offset

        self.canvas = Canvas(
            self,
            height=(max_y * scale) + offset,
            width=(max_x * scale) + offset,
            bg="black"
            )

        self.canvas.pack()

    def add_block(self, coord, colour):
            """
            Add a block (rectangle of size (1 * SCALE)**2)
            :param self: instance
            :param x: Coordinate
            :param y: Coordinate
            :param colour: Block colour
            :return: The Tkinter ID of the block (rectangle) on the canvas.
            """
            rx = (coord.x * self.scale) + self.offset
            ry = (coord.y * self.scale) + self.offset

            return self.canvas.create_rectangle(rx, ry, rx + self.scale, ry + self.scale, fill=colour)

    def move_block(self, id, coord):
            """
            Move a block by relative x, y coordinate distance.
            :param self: instance
            :param id: Canvas id of the block (rectangle)
            :param x: relative X coordinate distance to move
            :param y: relative Y coordinate distance to move
            """
            self.canvas.move(id, coord.x * self.scale, coord.y * self.scale)

    def delete_block(self, id):
            """
            Delete the identified block
            :param self: instance
            :param id: Canvas id of the block (rectangle) to delete.
            :return:
            """
            self.canvas.delete(id)


class TetrisBoard(TBoard):
    """
    The board represents the tetris playing area. A grid of x by y blocks.
    """
    def __init__(self, parent, scale=20, max_x=10, max_y=20, offset=3):
        """
        Init and config the tetris board, default configuration:
        Scale (block size in pixels) = 20
        max X (in blocks) = 10
        max Y (in blocks) = 20
        offset (in pixels) = 3
        """
        TBoard.__init__(self, parent, scale, max_x, max_y, offset)
        self.landed = {}

    def check_for_complete_row( self, blocks ):
        """
        Look for a complete row of blocks, from the bottom up until the top row
        or until an empty row is reached.
        """
        rows_deleted = 0

        # TO DO - This is not atomic and could be improved.
        # Add the blocks to those in the grid that have already 'landed'
        for block in blocks:
            self.landed[block.coord] = block.id
        
        empty_row = 0

        # find the first empty row
        for y in xrange(self.max_y -1, -1, -1):
            row_is_empty = True
            for x in xrange(self.max_x):
                if self.landed.get(Coord(x, y), None):
                    row_is_empty = False
                    break;
            if row_is_empty:
                empty_row = y
                break

        # Now scan up and until a complete row is found. 
        y = self.max_y - 1
        while y > empty_row:
 
            complete_row = True
            for x in xrange(self.max_x):
                if self.landed.get(Coord(x, y), None) is None:
                    complete_row = False
                    break;

            if complete_row:
                rows_deleted += 1
                
                #delete the completed row
                for x in xrange(self.max_x):
                    block = self.landed.pop(Coord(x, y))
                    self.delete_block(block)
                    del block

                    
                # move all the rows above it down
                for ay in xrange(y-1, empty_row, -1):
                    for x in xrange(self.max_x):
                        block = self.landed.get(Coord(x, ay), None)
                        if block:
                            block = self.landed.pop(Coord(x, ay))
                            dx,dy = direction_d[DOWN]

                            tx, ty = direction_d[DOWN]   # FIX THIS
                            self.move_block(block, Coord(tx, ty))
                            self.landed[Coord(x+dx, ay+dy)] = block

                # move the empty row down index down too
                empty_row +=1
                # y stays same as row above has moved down.
                
            else:
                y -= 1
                
        #self.output() # non-gui diagnostic
        
        # return the score, calculated by the number of rows deleted.        
        return (100 * rows_deleted) * rows_deleted

    def output( self ):
        for y in xrange(self.max_y):
            line = []
            for x in xrange(self.max_x):
                if self.landed.get(Coord(x, y), None):
                    line.append("X")
                else:
                    line.append(".")
            print "".join(line)

    def check_block(self, coord):
        """
        Check if the x, y coordinate can have a block placed there.
        That is; if there is a 'landed' block there or it is outside the
        board boundary, then return False, otherwise return true.
        """
        if coord.x < 0 or coord.x >= self.max_x or coord.y >= self.max_y:
            return False
        elif self.landed.has_key(coord):
            return False
        else:
            return True


class Block(object):
    # This could be replaced with a named tuple
    def __init__( self, id, coord):
        self.id = id
        self.coord = coord


class Shape(object):
    """
    Shape is the  Base class for the game pieces e.g. square, T, S, Z, L,
    reverse L and I. Shapes are constructed of blocks. 
    """
    def __init__(self, board, coords, colour, offset=None):
        """
        Initialise the shape base.
        """
        self.board = board
        self.blocks = []

        if offset is not None:
            coords = map(lambda c: Coord(c.x+offset.x, c.y+offset.y), coords)
        
        for coord in coords:
            block = Block(self.board.add_block(coord, colour), coord)
            
            self.blocks.append(block)
            
    def move( self, direction ):
        """
        Move the blocks in the direction indicated by adding (dx, dy) to the
        current block coordinates
        """
        d_x, d_y = direction_d[direction]
        
        for block in self.blocks:

            x = block.coord.x + d_x
            y = block.coord.y + d_y
            
            if not self.board.check_block(Coord(x, y)):
                return False
            
        for block in self.blocks:
            
            x = block.coord.x + d_x
            y = block.coord.y + d_y
            
            self.board.move_block(block.id, Coord(d_x, d_y))

            block.coord = Coord(x, y)

        return True
            
    def rotate(self, clockwise=True):
        """
        Rotate the blocks around the 'middle' block, 90-degrees. The
        middle block is always the index 0 block in the list of blocks
        that make up a shape.
        """
        # TO DO: Refactor for DRY
        middle = self.blocks[0].coord
        rel_blocks = []
        for block in self.blocks:
            rel_blocks.append( Coord(block.coord.x-middle.x, block.coord.y-middle.y ) )
            
        # to rotate 90-degrees (x,y) = (-y, x)
        # First check that the there are no collisions or out of bounds moves.
        for rel in rel_blocks:
            if clockwise:
                x = middle.x+rel.y
                y = middle.y-rel.x
            else:
                x = middle.x-rel.y
                y = middle.y+rel.x
            
            if not self.board.check_block(Coord(x, y)):
                return False
            
        for rel, act in zip(rel_blocks, self.blocks):
            if clockwise:
                x = middle.x+rel.y
                y = middle.y-rel.x
            else:
                x = middle.x-rel.y
                y = middle.y+rel.x

            diff_x = x - act.coord.x
            diff_y = y - act.coord.y
            
            self.board.move_block( act.id, Coord(diff_x, diff_y) )
            
            act.coord = Coord(x, y)

        return True

    # def __del__(self):
    #     for block in self.blocks:
    #         self.board.delete_block(block.id)


class LimitedRotateShape(Shape):
    """
    This is a base class for the shapes like the S, Z and I that don't fully
    rotate (which would result in the shape moving *up* one block on a 180).
    Instead they toggle between 90 degrees clockwise and then back 90 degrees
    anti-clockwise.
    """
    def __init__( self, board, coords, colour, offset ):
        self.clockwise = True
        super(LimitedRotateShape, self).__init__(board, coords, colour, offset)
    
    def rotate(self, clockwise=True):
        """
        Clockwise, is used to indicate if the shape should rotate clockwise
        or back again anti-clockwise. It is toggled.
        """
        super(LimitedRotateShape, self).rotate(clockwise=self.clockwise)
        if self.clockwise:
            self.clockwise=False
        else:
            self.clockwise=True

class SquareShape(Shape):
    """
      0 1 2 .
    0 X X
    1 X X
    2
    .
    """
    def __init__(self, board, offset=None):
        """
        :param board: A TBoard canvas object that the shape is drawn on.
        :param offset: Offset (x, y) to where the shape is initially drawn
        """
        coords = [Coord(0, 0), Coord(0, 1), Coord(1, 0), Coord(1, 1)]
        super(SquareShape, self).__init__(board, coords, "red", offset)

    HEIGHT = 2
    WIDTH =2

    def rotate(self, clockwise=True):
        """
        Override the rotate method for the square shape to do exactly nothing!
        """
        pass


class TShape(Shape):
    """
      0 1 2 .
    0 X X X
    1   X
    2
    .
    """
    def __init__(self, board, offset=None):
        """
        :param board: A TBoard canvas object that the shape is drawn on.
        :param offset: Offset (x, y) to where the shape is initially drawn
        """
        coords = [Coord(1, 0), Coord(0, 0),  Coord(2, 0), Coord(1, 1)]
        super(TShape, self).__init__(board, coords, "yellow", offset)

    HEIGHT = 2
    WIDTH = 3

class LShape(Shape):
    """
      0 1 2 .
    0 X
    1 X
    2 X X
    .
    """
    def __init__(self, board, offset=None):
        """
        Create this shape
        :param board: A TBoard canvas object that the shape is drawn on.
        :param offset: Offset (x, y) to where the shape is initially drawn
        """
        coords = [ Coord(0, 1), Coord(0, 0),  Coord(0, 2), Coord(1, 2)]
        super(LShape, self).__init__(board, coords, "orange", offset)

    HEIGHT = 3
    WIDTH = 2


class JShape(Shape):
    """
      0 1 2 .
    0   X
    1   X
    2 X X
    .
    """
    def __init__(self, board, offset=None):
        """
        :param board: A TBoard canvas object that the shape is drawn on.
        :param offset: Offset (x, y) to where the shape is initially drawn
        """
        coords = [ Coord(1, 1), Coord(1, 0),   Coord(0, 2), Coord(1, 2)]
        super(JShape, self).__init__(board, coords, "green", offset)

    HEIGHT = 3
    WIDTH = 2


class ZShape(LimitedRotateShape):
    """
      0 1 2 3 .
    0   X
    1 X X
    2 X
    .
    """
    def __init__(self, board, offset=None):
        """
        :param board: A TBoard canvas object that the shape is drawn on.
        :param offset: Offset (x, y) to where the shape is initially drawn
        """
        coords = [Coord(0, 1), Coord(1, 0), Coord(1, 1), Coord(0, 2)]
        super(ZShape, self).__init__(board, coords, "purple", offset)

    HEIGHT = 3
    WIDTH = 2


class SShape(LimitedRotateShape):
    """
      0 1 2 3 .
    0 X
    1 X X
    2   X
    .
    """
    def __init__(self, board, offset=None):
        """
        :param board: A TBoard canvas object that the shape is drawn on.
        :param offset: Offset (x, y) to where the shape is initially drawn
        """
        coords = [Coord(0, 1), Coord(0, 0), Coord(1, 1), Coord(1, 2)]
        super(SShape, self).__init__(board, coords, "cyan", offset)

    HEIGHT = 3
    WIDTH = 2

class IShape(LimitedRotateShape):
    """
       0 1 .
     0 X
     1 X
     2 X
     3 X
     .
     """
    def __init__(self, board, offset=None):
        """
        :param board: A TBoard canvas object that the shape is drawn on.
        :param offset: Offset (x, y) to where the shape is initially drawn
        """
        coords = [Coord(0, 1), Coord(0, 0),   Coord(0, 2), Coord(0, 3)]
        super(IShape, self).__init__(board, coords, "blue", offset)

    HEIGHT = 4
    WIDTH = 1

WID = 10


class InfoPanel(Frame):
    """The info panel has a grid layout manager and displays the following game info:
    * The score
    * The level
    * Preview panel - next tetrominoe.
    * keyboard controls
    * Quit button
    * New game button
    * Status e.g. if the game is Paused"""

    def __init__(self, parent, new_game_fn, quit_fn):
        """Init the info panel e.g. do all the setup for it."""
        Frame.__init__(self, parent, bg="grey")

        self.parent = parent
        self.score_var = StringVar()
        self.level_var = StringVar()
        self.state_var = StringVar()
        self.update_score(0)
        self.update_level(0)

        my_font = tkFont.Font(root=self.parent, family="Times New Roman", size=16, weight="normal")
        Label(self, text="Tetris TK", justify=CENTER, font=my_font, pady=5).pack(side=TOP, fill=X)

        slf = LabelFrame(self, padx=5, pady=5)
        slf.pack(side=TOP, fill=X)
        Label(slf, text="Score:", anchor=W, justify=LEFT, width=10).grid(column=0, row=0)
        score_lbl = Label(slf, bd=5, relief=SUNKEN, anchor=E, textvariable=self.score_var, width=10)
        score_lbl.grid(column=1, row=0)

        Label(slf, text="Level:", anchor=W, justify=LEFT, width=10).grid(column=0, row=1)
        level_lbl = Label(slf, bd=5, relief=SUNKEN, anchor=E, textvariable=self.level_var, width=10)
        level_lbl.grid(column=1, row=1)

        self.preview = TBoard(self, scale=SCALE, max_x=4, max_y=4, offset=OFFSET)
        self.preview.pack()

        ctrl_frame = LabelFrame(self, text="Controls", padx=5, pady=5)
        ctrl_frame.pack(side=TOP, fill=X)

        Label(ctrl_frame, text="Pause:", anchor=W, justify=LEFT, width=8).grid(column=0, row=0, columnspan=2)
        Label(ctrl_frame, text="P", width=5, relief=GROOVE).grid(column=2, row=0)

        Label(ctrl_frame, text="   ").grid(column=2, row=1) # blank line

        Label(ctrl_frame, text="Drop:", anchor=W, justify=LEFT, width=8).grid(column=0, row=2, columnspan=2)
        Label(ctrl_frame, text="^", width=5, relief=GROOVE).grid(column=3, row=2)

        Label(ctrl_frame, text="Move:", anchor=W, justify=LEFT, width=8).grid(column=0, row=3, columnspan=2)
        Label(ctrl_frame, text="<", width=5, relief=GROOVE).grid(column=2, row=3)
        Label(ctrl_frame, text="v", width=5, relief=GROOVE).grid(column=3, row=3)
        Label(ctrl_frame, text=">", width=5, relief=GROOVE).grid(column=4, row=3)

        Label(ctrl_frame, text="Left").grid(column=2, row=4)
        Label(ctrl_frame, text="Down").grid(column=3, row=4)
        Label(ctrl_frame, text="Right").grid(column=4, row=4)

        Label(ctrl_frame, text="Rotate:", anchor=W, justify=LEFT, width=8).grid(column=0, row=5, columnspan=2)
        Label(ctrl_frame, text="A", width=5, relief=GROOVE).grid(column=2, row=5)
        Label(ctrl_frame, text="S", width=5, relief=GROOVE).grid(column=4, row=5)

        state_frame = LabelFrame(self, text="State", padx=5, pady=5)
        state_frame.pack(side=TOP, fill=X)
        Label(state_frame, textvariable=self.state_var, justify=CENTER, font=my_font).pack(side=TOP, fill=X)

        btn_frame = LabelFrame(self, padx=5, pady=5)
        btn_frame.pack(side=BOTTOM, fill=X)
        self.new_game_bttn = Button(btn_frame, text="New Game", padx=5, pady=5, command=new_game_fn)
        self.new_game_bttn.pack(side=BOTTOM, fill=X)
        self.quit_bttn = Button(btn_frame, text = "Quit", padx=5, pady=5, command=quit_fn)
        self.quit_bttn.pack(side=TOP, fill=X)

    def update_score(self, score):
        self.score_var.set("{:>010d}".format(score))

    def update_level(self, level):
        self.level_var.set("{:>10d}".format(level))

    def update_state(self, state):
        self.state_var.set(state)
        if state not in PLAYING:
            self.new_game_bttn.config(state=NORMAL)
        else:
            self.new_game_bttn.config(state=DISABLED)


class game_controller(object):
    """
    Main game loop and receives GUI callback events for keypresses etc...
    """
    def __init__(self, parent):
        """
        Intialise the game...
        """
        self.parent = parent
        self.delay = 1000    #ms
        
        # lookup table
        self.shapes = [SquareShape,
                       TShape,
                       LShape,
                       JShape,
                       ZShape,
                       SShape,
                       IShape]
        
        self.thresholds = level_thresholds( 500, NO_OF_LEVELS )
        
        self.board = TetrisBoard(
            parent,
            scale=SCALE,
            max_x=MAXX,
            max_y=MAXY,
            offset=OFFSET
            )

        self.score = 0
        self.level = 0

        self.info_panel = InfoPanel(parent, self.new_game_fn, self.quit_fn)

        self.board.pack(side=LEFT, fill=Y)
        self.info_panel.pack(side=LEFT, fill=Y)

        self.parent.bind("<Left>", self.left_callback)
        self.parent.bind("<Right>", self.right_callback)
        self.parent.bind("<Up>", self.up_callback)
        self.parent.bind("<Down>", self.down_callback)
        self.parent.bind("a", self.a_callback)
        self.parent.bind("s", self.s_callback)
        self.parent.bind("p", self.p_callback)

        self.state = READY
        self.info_panel.update_state(self.state)
        # must press 'New Game' to start.
        #self.board.output()
        self.after_id = None
        self.next_shape = None
        self.preview_shape = None
        self.shape = None

    def new_game_fn(self):
        self.state = PLAYING
        self.info_panel.update_state(self.state)
        self.score = 0
        self.level = 0
        self.get_preview_shape()
        self.shape = self.get_next_shape()
        self.after_id = self.parent.after(self.delay, self.move_my_shape)

    def handle_move(self, direction):
        # if you can't move then you've hit something
        if not self.shape.move( direction ):
            
            # if your heading down then the shape has 'landed'
            if direction == DOWN:
                self.score += self.board.check_for_complete_row(
                    self.shape.blocks
                    )
                self.info_panel.update_score(self.score)
                del self.shape
                self.shape = self.get_next_shape()

                # TODO: Check is there room on the top line for the new shape!
                # If the shape returned is None, then this indicates that
                # that the check before creating it failed and the
                # game is over!
                if self.shape is None:
                    tkMessageBox.showwarning(
                        title="GAME OVER",
                        message ="Score: %7d\tLevel: %d\t" % (
                            self.score, self.level),
                        parent=self.parent
                        )
                    Toplevel().destroy()
                    self.parent.destroy()
                    sys.exit(0)
                
                # do we go up a level?
                if self.level < NO_OF_LEVELS and self.score >= self.thresholds[ self.level]:
                    self.level+=1
                    self.info_panel.update_level(self.level)
                    self.delay-=100
                    
                # Signal that the shape has 'landed'
                return False
        return True

    def left_callback( self, event ):
        if self.state in PLAYING and self.shape:
            self.handle_move( LEFT )
        
    def right_callback( self, event ):
        if self.state in PLAYING and self.shape:
            self.handle_move( RIGHT )

    def up_callback( self, event ):
        if self.state in PLAYING and self.shape:
            # drop the tetrominoe to the bottom
            while self.handle_move( DOWN ):
                pass

    def down_callback( self, event ):
        if self.state in PLAYING and self.shape:
            self.handle_move( DOWN )
            
    def a_callback( self, event):
        if self.state in PLAYING and self.shape:
            self.shape.rotate(clockwise=True)
            
    def s_callback( self, event):
        if self.state in PLAYING and self.shape:
            self.shape.rotate(clockwise=False)
        
    def p_callback(self, event):
        """Pause play"""
        if self.state in PLAYING:
            self.parent.after_cancel(self.after_id)
            self.state = PAUSED
            self.info_panel.update_state(self.state)
        elif self.state in PAUSED:
            self.state = PLAYING
            self.info_panel.update_state(self.state)
            self.after_id = self.parent.after(self.delay, self.move_my_shape)

    def move_my_shape( self ):
        if self.state in PLAYING and self.shape:
            self.handle_move( DOWN )
            self.after_id = self.parent.after( self.delay, self.move_my_shape )

    def get_preview_shape(self):
        """Randomly select a tetromino and put it in the preview window"""
        self.next_shape = self.shapes[randint(0, len(self.shapes)-1)]
        self.preview_shape = self.next_shape(
            self.info_panel.preview,
            offset=Coord(2-self.next_shape.WIDTH/2, 2-self.next_shape.HEIGHT/2)
        )

    def get_next_shape( self ):
        """
        Draw the next shape on the game board so it is in play and return its ref.
        Delete the previous preview shape and get a new one, display it in the preview box.
        """
        this_shape = self.next_shape(self.board, offset=Coord(4, 0-self.next_shape.HEIGHT))
        for block in self.preview_shape.blocks:
            self.info_panel.preview.delete_block(block.id)
        del self.preview_shape
        self.get_preview_shape()
        return this_shape

    def quit_fn(self):
        self.parent.quit()


if __name__ == "__main__":
    root = Tk()
    root.title("Tetris Tk")
    theGame = game_controller( root )
    
    root.mainloop()
