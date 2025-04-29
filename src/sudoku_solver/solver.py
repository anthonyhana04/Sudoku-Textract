def legal_move(grid, row, col, number):
    br = 3*(row//3); bc = 3*(col//3)
    for i in range(9):
        if (grid[row][i]==number or
            grid[i][col]==number or
            grid[br + i//3][bc + i%3]==number):
            return False
    return True

def solve(grid, row=0, col=0):
    if col == 9:
        row += 1; col = 0
        if row == 9:
            return True
    if grid[row][col] != 0:
        return solve(grid, row, col+1)
    for num in range(1,10):
        if legal_move(grid, row, col, num):
            grid[row][col] = num
            if solve(grid, row, col+1):
                return True
    grid[row][col] = 0
    return False
