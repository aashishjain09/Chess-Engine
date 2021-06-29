"""
This file is the main driver file. It will be responsible for handling user input and
displaying the current GameState object.
"""

import pygame as p
import pygame.event

from Chess_Engine.CHESS import ChessEngineAdvanced, SmartMoveFinder

WIDTH = HEIGHT = 512  # Choose 400 for shorter board. For bigger board, choose 640 or 768
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15  # For animations later on [MAYBE]
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
    gs = ChessEngineAdvanced.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # Flag that checks if a move has been made
    animate = False  # Flag that decides if a move should be animated or not
    loadImages()  # Only to be called once so that it doesn't unnecessarily lag our programme
    gameOver = False
    running = True
    sqSelected = ()
    playerClicks = []  # Keeps track of player clicks. (Two tuples: [(6, 4), (4, 4)]

    # These flags will be True if a Human is playing white else False.
    playerOne = False
    playerTwo = False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in pygame.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # Find location coordinate of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col):  # The user clicked same square twice
                        playerClicks = [sqSelected]
                        sqSelected = ()
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # Append for both clicks from the user
                    if len(playerClicks) == 2:  # After 2nd click, we ask the board to make the move.
                        move = ChessEngineAdvanced.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # Key Handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when "z" key is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:  # Reset the board when "r" key is pressed
                    gs = ChessEngineAdvanced.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        # AI Move Finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        # This code animates a move made by Players
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs, validMoves, sqSelected)

        # Check whether checkmate or stalemate has occurred and end the game
        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by Checkmate')
            else:
                drawText(screen, 'White wins by Checkmate')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'STALEMATE')

        clock.tick(MAX_FPS)
        pygame.display.flip()


"""
Responsible for all graphics within the current GameState
"""
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # This function will draw squares on the board
    # This function will highlight the selected Square and also highlight the possible valid moves with that piece
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # This function will draw the pieces on top of the squares


"""
Draws the squares up on the screen. The top left square in the board is always light colored.  
[HINT] You can change color theme of the board from here...
"""
def drawBoard(screen):
    global colors
    colors = [p.Color('light gray'), p.Color('dark green')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Highlighs Square Selected and possible moves for the Piece on that Square
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # Selected Piece is a piece that can be Moved

            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Transparency Value
            s.fill(p.Color('cornflowerblue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # Highlight Valid Moves
            s.fill(p.Color('darkslategray1'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


"""
Draws the pieces on the board using the current GameState.board
[HINT] This is a separate function so that we can implement piece highlighting and Piece Animation too.
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Animating a Move
"""
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 8
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount+1):
        r, c = (move.startRow + dR * frame/frameCount, move.startCol + dC * frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase piece moved from it's ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Draw captured piece at every frame until the moving piece gets there
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont('Helvetica', 36, True)
    msg = font.render(text, False, p.Color('gray69'))
    msgbox = p.Rect(0, 0, WIDTH, HEIGHT).move((WIDTH - msg.get_width())/2, (HEIGHT - msg.get_height())/2)
    screen.blit(msg, msgbox)
    msg_shadow = font.render(text, False, p.Color('black'))
    screen.blit(msg_shadow, msgbox.move(2, -2))
if __name__ == "__main__":
    main()
