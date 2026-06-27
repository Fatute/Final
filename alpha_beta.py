def alphabeta(board, alpha, beta):

    global nodes
    nodes += 1

    if len(find_blank(board)) == 0 or check_winner(board) is not False:
        return utility(board), []

    turn = current_player(board)

    if turn == 'X':

        value = -float('inf')
        best_path = []

        for move in find_blank(board):

            child = result(board, move[0], move[1], 'X')
            score, path = alphabeta(child, alpha, beta)
            
            if score > value:
                value = score
                best_path = [move] + path

            alpha = max(alpha, value)

            if alpha >= beta:
                break
            
        return value, best_path

    else:

        value = float('inf')
        best_path = []

        for move in find_blank(board):
            child = result(board, move[0], move[1], 'O')
            score, path = alphabeta(child, alpha, beta)

            if score < value:
                value = score
                best_path = [move] + path

            beta = min(beta, value)

            if alpha >= beta:
                break

        return value, best_path