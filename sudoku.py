import pygame as pg
import sys

pg.init()
screen_size = 750, 750
screen = pg.display.set_mode(screen_size)
font = pg.font.SysFont(None, 80)
small_font = pg.font.SysFont(None, 40)

# Default grid setup
# default_grid = [
#     [7, 8, 0, 4, 0, 0, 1, 2, 0],
#     [6, 0, 0, 0, 7, 5, 0, 0, 9],
#     [0, 0, 3, 6, 0, 1, 0, 7, 8],
#     [0, 5, 7, 0, 4, 0, 2, 6, 0],
#     [0, 0, 1, 0, 5, 0, 9, 3, 0],
#     [9, 0, 4, 0, 6, 0, 0, 0, 5],
#     [0, 7, 0, 3, 0, 0, 0, 1, 2],
#     [1, 2, 0, 0, 0, 7, 4, 0, 0],
#     [0, 4, 9, 2, 8, 6, 0, 0, 7]
# ]

# Demo Grid to Show Win Condition
default_grid = [
    [0, 1, 6, 5, 7, 8, 4, 9, 2],
    [5, 2, 9, 1, 3, 4, 7, 6, 8],
    [4, 8, 7, 6, 2, 9, 5, 3, 1],
    [2, 6, 3, 4, 1, 5, 9, 8, 7],
    [9, 7, 4, 8, 6, 3, 1, 2, 5],
    [8, 5, 1, 7, 9, 2, 6, 4, 3],
    [1, 3, 8, 9, 4, 7, 2, 5, 6],
    [6, 9, 2, 3, 5, 1, 8, 7, 4],
    [7, 4, 5, 2, 8, 6, 3, 1, 9]
]


user_grid = [row[:] for row in default_grid]  # Copy of the grid for user inputs
selected_cell = None  # Track selected cell for input

# Draw grid background and lines
def draw_background():
    screen.fill(pg.Color("white"))
    pg.draw.rect(screen, pg.Color("black"), pg.Rect(15, 15, 720, 720), 10)

    i = 1
    while (i * 80) < 720:
        line_width = 5 if i % 3 > 0 else 10
        pg.draw.line(screen, pg.Color("black"), pg.Vector2((i * 80) + 15, 15), pg.Vector2((i * 80) + 15, 730), line_width)
        pg.draw.line(screen, pg.Color("black"), pg.Vector2(15, (i * 80) + 15), pg.Vector2(730, (i * 80) + 15), line_width)
        i += 1

# Draw numbers on the grid
def draw_numbers():
    for row in range(9):
        for col in range(9):
            num = user_grid[row][col]
            if num != 0:
                color = pg.Color("black") if default_grid[row][col] != 0 else pg.Color("blue")
                n_text = font.render(str(num), True, color)
                screen.blit(n_text, pg.Vector2((col * 80) + 43, (row * 80) + 34))


def show_message(text):
    # Semi-transparent background
    small_font=pg.font.SysFont(None, 50)
    overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with some transparency

    # Render the message
    text_surface = small_font.render(text, True, pg.Color("white"))
    text_rect = text_surface.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2))

    # Display the overlay and text
    screen.blit(overlay, (0, 0))
    screen.blit(text_surface, text_rect)
    pg.display.flip()

    # Wait for a key or close event to dismiss the message
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                waiting = False


# Highlight the selected cell
def draw_selected_cell():
    if selected_cell:
        row, col = selected_cell
        pg.draw.rect(screen, pg.Color("yellow"), pg.Rect((col * 80) + 15, (row * 80) + 15, 80, 80), 5)

# Validate if a number can be placed in the specified row, column, and square
def is_valid_move(grid, row, col, num):
    # Check row and column
    if num in grid[row] or num in [grid[i][col] for i in range(9)]:
        return False
    # Check 3x3 sub-grid
    start_row, start_col = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if grid[start_row + i][start_col + j] == num:
                return False
    return True

# Check if the puzzle is complete
def is_board_complete(grid):
    # Check rows and columns for unique values 1-9
    for i in range(9):
        row = [grid[i][j] for j in range(9)]
        col = [grid[j][i] for j in range(9)]
        if len(set(row)) != 9 or len(set(col)) != 9 or 0 in row or 0 in col:
            return False

    # Check 3x3 sub-grids for unique values 1-9
    for row in range(0, 9, 3):
        for col in range(0, 9, 3):
            subgrid = [grid[row + i][col + j] for i in range(3) for j in range(3)]
            if len(set(subgrid)) != 9 or 0 in subgrid:
                return False

    return True

# Main game loop to handle events and updates
def game_loop():
    global selected_cell
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            x, y = pg.mouse.get_pos()
            row, col = (y - 15) // 80, (x - 15) // 80
            if 0 <= row < 9 and 0 <= col < 9:
                selected_cell = (row, col)
        elif event.type == pg.KEYDOWN:
            if selected_cell:
                row, col = selected_cell
                if default_grid[row][col] == 0:  # Allow input only on empty cells
                    if event.key == pg.K_0 or event.key == pg.K_DELETE or event.key == pg.K_BACKSPACE:
                        user_grid[row][col] = 0
                    elif pg.K_1 <= event.key <= pg.K_9:
                        num = event.key - pg.K_0
                        if is_valid_move(user_grid, row, col, num):
                            user_grid[row][col] = num
                            if is_board_complete(user_grid):
                                show_message("Congratulations! You solved the puzzle!")
                        else:
                            show_message("Invalid move!")

    draw_background()
    draw_numbers()
    draw_selected_cell()
    pg.display.flip()

# Run the game loop
while True:
    game_loop()
