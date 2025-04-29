# Sudoku Solver & Extractor

A two-step pipeline that:

1. **Extracts** digits from a Sudoku photo using AWS Textract  
2. **Solves** the puzzle via backtracking  

Ideal for automating Sudoku-solving workflows on the cloud.

---

## Features

- **AWS Textract** integration for robust OCR  
- Pre-processing (contrast, blur, binarization) to boost recognition accuracy  
- Clean, modular codebase: separate `extractor` and `solver` modules  
- CLI entry-points & importable package  
- Example puzzles in `resources/` and outputs in `output/`  

---

## Installation

```bash
git clone https://github.com/yourusername/sudoku-solver.git
cd sudoku-solver
pip install -r requirements.txt
