import pytest
from sudoku_solver.solver import legal_move, solve

def test_legal_move_conflict():
    g = [[0]*9 for _ in range(9)]
    g[1][1] = 5
    assert not legal_move(g, 1, 2, 5)

def test_solve_almost_done():
    # a 9×9 grid with only one missing cell at (0,0)
    g = [[i+1 if j==i else j+1 for j in range(9)] for i in range(9)]
    # fix duplication: make cell (0,0) empty and fill rest with valid row
    g[0] = [0,2,3,4,5,6,7,8,9]
    assert solve(g)
    assert g[0][0] == 1
