import random

pieceScore = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'p': 1}

Kweights = [[1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 3, 3, 3, 3, 2, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 2, 3, 3, 3, 3, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]]

Bweights = [[4, 3, 2, 1, 1, 2, 3, 4],
            [3, 4, 3, 2, 2, 3, 4, 3],
            [2, 3, 4, 3, 3, 4, 3, 2],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [2, 3, 4, 3, 3, 4, 3, 2],
            [3, 4, 3, 2, 2, 3, 4, 3],
            [1, 1, 1, 1, 1, 1, 1, 1]]

Qweights = [[1, 1, 1, 3, 1, 1, 1, 1],
            [1, 2, 3, 3, 3, 1, 1, 1],
            [1, 4, 3, 3, 3, 4, 2, 1],
            [1, 2, 3, 3, 3, 2, 2, 1],
            [1, 2, 3, 3, 3, 2, 2, 1],
            [1, 4, 3, 3, 3, 4, 2, 1],
            [1, 2, 3, 3, 3, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]]

Rweights = [[4, 3, 4, 4, 4, 4, 3, 4],
            [4, 4, 4, 4, 4, 4, 4, 4],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [4, 4, 4, 4, 4, 4, 4, 4],
            [4, 3, 4, 4, 4, 4, 3, 4]]

Wpweights = [[8, 8, 8, 8, 8, 8, 8, 8],
            [8, 8, 8, 8, 8, 8, 8, 8],
            [5, 6, 6, 7, 7, 6, 6, 5],
            [2, 3, 3, 5, 5, 3, 3, 2],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0]]

Bpweights = [[0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [2, 3, 3, 5, 5, 3, 3, 2],
            [5, 6, 6, 7, 7, 6, 6, 5],
            [8, 8, 8, 8, 8, 8, 8, 8],
            [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = {'N': Kweights, 'Q': Qweights, 'R': Rweights, 'B': Bweights, 'wp': Wpweights, 'bp': Bpweights}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

"""
Returns a random move from a list of moves.
"""
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


"""
Returns a best move based on material value only.
It applies MinMax algorithm on 2 turns non recursively.
"""
def findBestMoveOld(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)

                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()

        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove


"""
Helper method to make the first recursive call
"""
def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    # findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    # findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)


"""
Returns a best move by applying MinMax Algorithm with various depth of recursion
"""
def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False)  # Recursive Call
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, True)  # Recursive Call
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore


"""
This is a cleaner way of writing the MinMax Algorithm, but the functionality is same.
"""
def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


"""
This is based on Alpha-Beta Pruning of the MinMax Tree.
Improves the AI while decreasing the computing time of the next move.
Takes two more variables known as Alpha(the max value) and Beta(the min value).
"""
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    # Todo: Move ordering
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(move, maxScore)
        gs.undoMove()

        # This code performs pruning.
        if maxScore > alpha:
            alpha = maxScore

        # This is the break case of the algorithm which decides whether we have the best move or not.
        if alpha >= beta:
            break
    return maxScore


"""
Returns a score based on white's convention.
I.e. A positive score is better for white and bad for black and vice versa.
"""
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # Black wins by Checkmate
        else:
            return CHECKMATE  # White wins by Checkmate
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for r, row in enumerate(gs.board):
        for c, square in enumerate(row):
            if square != '--':
                piecePositionScore = 0
                if square[1] != 'K':  # No position table for a King, yet.
                    if square[1] == 'p':  # For a pawn we need it's color also
                        piecePositionScore = piecePositionScores[square][r][c]
                    else:  # For any other piece
                        piecePositionScore = piecePositionScores[square[1]][r][c]

                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * .1
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * .1

    return score


"""
Scores the board based on material only.
"""
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score
