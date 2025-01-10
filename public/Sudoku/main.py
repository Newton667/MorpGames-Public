import pygame as pg
import sys
import asyncio
import random

# Initialize Pygame
pg.init()
screen_size = 850, 750
screen = pg.display.set_mode(screen_size)
font = pg.font.SysFont(None, 80)
small_font = pg.font.SysFont(None, 40)

# Sudoku board configurations
board_list = [
    [
        [3, 1, 6, 5, 7, 0, 4, 9, 2],
        [5, 2, 9, 1, 3, 4, 7, 6, 8],
        [0, 8, 7, 6, 2, 9, 5, 3, 1],
        [2, 6, 3, 4, 1, 5, 9, 8, 7],
        [9, 7, 4, 8, 6, 3, 1, 2, 5],
        [8, 5, 1, 7, 9, 2, 0, 4, 3],
        [1, 3, 8, 9, 4, 7, 2, 5, 6],
        [6, 9, 2, 3, 5, 1, 8, 7, 4],
        [7, 4, 0, 2, 8, 6, 3, 1, 9],
    ],
    [
        [3, 1, 6, 5, 7, 8, 4, 9, 0],
        [5, 2, 9, 1, 3, 4, 7, 6, 0],
        [4, 8, 7, 6, 2, 9, 5, 3, 1],
        [2, 6, 3, 4, 1, 5, 9, 8, 7],
        [0, 7, 4, 8, 6, 3, 1, 2, 5],
        [8, 5, 1, 7, 9, 2, 6, 4, 3],
        [1, 3, 8, 9, 4, 7, 2, 5, 6],
        [6, 9, 0, 3, 5, 1, 8, 7, 4],
        [7, 4, 0, 2, 8, 6, 3, 1, 9],
    ],
    [
        [0, 1, 6, 5, 7, 8, 4, 9, 2],
        [5, 2, 9, 1, 3, 4, 7, 6, 8],
        [4, 8, 7, 6, 2, 0, 5, 3, 1],
        [2, 6, 3, 4, 1, 5, 9, 8, 7],
        [9, 7, 4, 8, 6, 3, 1, 2, 5],
        [8, 5, 0, 7, 9, 2, 6, 4, 3],
        [1, 3, 0, 9, 4, 7, 2, 5, 0],
        [6, 9, 0, 3, 5, 1, 8, 7, 4],
        [7, 4, 0, 2, 8, 6, 3, 1, 9],
    ],
]

# Default and user grid setup
default_grid = random.choice(board_list)
user_grid = [row[:] for row in default_grid]
selected_cell = None
start_time = pg.time.get_ticks()

# Load and flip image horizontally
morp_image = pg.image.load("img/Morp_2.png")
morp_image_flipped = pg.transform.flip(morp_image, True, False)

# Draw the timer
def draw_timer():
    elapsed_time = (pg.time.get_ticks() - start_time) // 1000
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = f"{minutes:02}:{seconds:02}"
    timer_surface = small_font.render(timer_text, True, pg.Color("black"))
    screen.blit(timer_surface, (750, 0))

# Draw the background grid
def draw_background():
    screen.fill(pg.Color("white"))
    pg.draw.rect(screen, pg.Color("black"), pg.Rect(15, 15, 720, 720), 10)
    for i in range(1, 9):
        line_width = 5 if i % 3 != 0 else 10
        pg.draw.line(screen, pg.Color("black"), (15 + i * 80, 15), (15 + i * 80, 735), line_width)
        pg.draw.line(screen, pg.Color("black"), (15, 15 + i * 80), (735, 15 + i * 80), line_width)

# Draw numbers in the grid
def draw_numbers():
    for row in range(9):
        for col in range(9):
            num = user_grid[row][col]
            if num != 0:
                color = pg.Color("black") if default_grid[row][col] != 0 else pg.Color("blue")
                n_text = font.render(str(num), True, color)
                screen.blit(n_text, (col * 80 + 43, row * 80 + 34))

# Draw flipped image
def draw_flipped_image():
    image_rect = morp_image_flipped.get_rect()
    position = (screen_size[0] - image_rect.width, screen_size[1] - image_rect.height)
    screen.blit(morp_image_flipped, position)

# Validate move
def is_valid_move(grid, row, col, num):
    if num in grid[row] or num in [grid[i][col] for i in range(9)]:
        return False
    start_row, start_col = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if grid[start_row + i][start_col + j] == num:
                return False
    return True

# Display a message overlay
async def show_message(text):
    overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    text_surface = small_font.render(text, True, pg.Color("white"))
    text_rect = text_surface.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2))
    screen.blit(overlay, (0, 0))
    screen.blit(text_surface, text_rect)
    pg.display.flip()

    # Pause for a short time asynchronously
    await asyncio.sleep(.5)  # Wait for 1 second asynchronously


# Check if board is complete
def is_board_complete(grid):
    for i in range(9):
        row = [grid[i][j] for j in range(9)]
        col = [grid[j][i] for j in range(9)]
        if len(set(row)) != 9 or len(set(col)) != 9 or 0 in row or 0 in col:
            return False
    for row in range(0, 9, 3):
        for col in range(0, 9, 3):
            subgrid = [grid[row + i][col + j] for i in range(3) for j in range(3)]
            if len(set(subgrid)) != 9 or 0 in subgrid:
                return False
    return True

# Highlight the selected cell
def draw_selected_cell():
    if selected_cell:
        row, col = selected_cell
        cell_x = col * 80 + 15
        cell_y = row * 80 + 15
        pg.draw.rect(screen, pg.Color("yellow"), (cell_x, cell_y, 80, 80), 5)  # Draw the yellow outline
        
async def show_end_screen(final_time):
    replay_button = pg.Rect(screen_size[0] // 2 - 100, screen_size[1] // 2 + 50, 200, 50)
    overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Display solved message
    solved_text = "Solved! Good job"
    solved_surface = small_font.render(solved_text, True, pg.Color("white"))
    solved_rect = solved_surface.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2 - 100))
    screen.blit(solved_surface, solved_rect)

    # Display the time
    time_text = f"Time: {final_time // 60:02}:{final_time % 60:02}"
    time_surface = small_font.render(time_text, True, pg.Color("white"))
    time_rect = time_surface.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2 - 50))
    screen.blit(time_surface, time_rect)

    # Display the replay button
    pg.draw.rect(screen, pg.Color("white"), replay_button)
    replay_text = small_font.render("Replay", True, pg.Color("black"))
    replay_text_rect = replay_text.get_rect(center=replay_button.center)
    screen.blit(replay_text, replay_text_rect)

    pg.display.flip()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if replay_button.collidepoint(event.pos):  # Check if replay button is clicked
                    return True  # Replay the game
        await asyncio.sleep(0)  # Allow the game loop to remain responsive


# Main game loop
async def main():
    global selected_cell, default_grid, user_grid, start_time
    while True:  # Allow replay functionality
        # Ensure a new random board on replay
        previous_board = default_grid
        while True:
            default_grid = random.choice(board_list)
            if default_grid != previous_board:
                break
        user_grid = [row[:] for row in default_grid]
        selected_cell = None
        start_time = pg.time.get_ticks()

        game_running = True
        while game_running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    row, col = (y - 15) // 80, (x - 15) // 80
                    if 0 <= row < 9 and 0 <= col < 9:
                        selected_cell = (row, col)
                elif event.type == pg.KEYDOWN:
                    if selected_cell:
                        row, col = selected_cell
                        if default_grid[row][col] == 0:
                            if event.key == pg.K_0 or event.key in [pg.K_BACKSPACE, pg.K_DELETE]:
                                user_grid[row][col] = 0
                            elif pg.K_1 <= event.key <= pg.K_9:
                                num = event.key - pg.K_0
                                if is_valid_move(user_grid, row, col, num):
                                    user_grid[row][col] = num
                                    draw_background()
                                    draw_numbers()
                                    draw_selected_cell()
                                    draw_flipped_image()
                                    draw_timer()
                                    pg.display.flip()
                                    if is_board_complete(user_grid):
                                        final_time = (pg.time.get_ticks() - start_time) // 1000
                                        await asyncio.sleep(0.5)  # Allow the last number to show briefly
                                        if not await show_end_screen(final_time):  # Show the solved page
                                            break  # Exit the main loop if replay is not chosen
                                        else:
                                            game_running = False  # Trigger a reset for a new board
                                else:
                                    await show_message("Invalid move!")  # Show the invalid move message


            if not game_running:
                break

            draw_background()
            draw_numbers()
            draw_selected_cell()
            draw_flipped_image()
            draw_timer()
            pg.display.flip()
            await asyncio.sleep(0)

        # Show end screen and check for replay
        if not show_end_screen(final_time):
            break  # Exit the main loop if replay is not chosen

    pg.quit()
    sys.exit()


# Run the game
asyncio.run(main())

