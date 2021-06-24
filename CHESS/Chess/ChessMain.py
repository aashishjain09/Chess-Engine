"""
This file is the main driver file. It will be responsible for handling user input and
displaying the current GameState object.
"""

import pygame as p
import pygame.event

from Chess import ChessEngine

WIDTH = HEIGHT = 512  # or choose 400 if you like
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15  # For animations later on (hopefully)
IMAGES = {}
"""
Initialises a global dictionary of Images of Chess pieces. This will be called only once in the Main.
"""
def loadImages():
    pieces = ['wK', 'wQ', 'wR', 'wB', 'wN', 'wp', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+piece+".png"), (SQ_SIZE, SQ_SIZE))

"""
The main driver of our code. It will be responsible for handling user input and updating the graphics
"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    loadImages()  # Only to be called once so that it doesn't unnecessarily lag our programme
    running = True
    sqSelected = ()
    playerClicks = []  # Keeps track of player clicks. (Two tuples: [(6, 4), (4, 4)]
    while running:
        for e in pygame.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # Find location coordinate of the mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):  # The user clicked same square twice
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)  # Append for both clicks from the user
                if len(playerClicks) == 2:  # After 2nd click, we ask the board to make the move.
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    gs.makeMove(move)
                    # Reset player's Clicks
                    sqSelected = ()
                    playerClicks = []

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        pygame.display.flip()

"""
Responsible for all graphics within the current GameState
"""
def drawGameState(screen, gs):
    drawBoard(screen)  # This function will draw squares on the board
    drawPieces(screen, gs.board)  # This function will draw the pieces on top of the squares

"""
Draws the squares up on the screen. The top left square in the board is always light colored.  
[HINT] You can change color theme of the board from here...
"""
def drawBoard(screen):
    colors = [p.Color('light gray'), p.Color('dark green')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draws the pieces on the board using the current GameState.board
[HINT] This is a separate function so that we can implement piece highlighting.
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))



if __name__ == "__main__":
    main()
