from newout import sudoku_grid

def legal_move(sudoku_grid, row, col, number):
    
    block_row = 3 * (row // 3)
    block_col = 3 * (col // 3)
    
    for i in range(9):
        
        if (sudoku_grid[row][i] == number or
            sudoku_grid[i][col] == number or
            sudoku_grid[block_row + i // 3][block_col + i % 3] == number):
            
            return False
        
    return True
        
def solve(sudoku_grid, row, col):
    
    if col == 9:
        if row == 8:
            return True
        row += 1
        col = 0
    
    if sudoku_grid[row][col] > 0:
        return solve(sudoku_grid, row, col + 1)
    
    for num in range(1, 10): 
        if legal_move(sudoku_grid, row, col, num):
            sudoku_grid[row][col] = num
            if solve(sudoku_grid, row, col + 1):
                return True
        
        sudoku_grid[row][col] = 0
    
    return False

if __name__ == "__main__":
    if solve(sudoku_grid, 0, 0):
        print("Solved puzzle:")
        for i in range(9):
            for j in range(9):
                print(sudoku_grid[i][j], end=" ")
            print()
    else:
        print("No Solution For This Sudoku")
    
    