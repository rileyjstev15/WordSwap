import pygame
import random
import string
import sys
import os
import time

# Constants
GRID_SIZE = 12
TILE_SIZE = 70
WINDOW_SIZE = GRID_SIZE * TILE_SIZE
LETTERS = list(string.ascii_uppercase)  # All uppercase letters

# Function to load valid words from a file
def load_valid_words(filename):
    try:
        with open(filename, 'r') as file:
            words = {line.strip().upper() for line in file}
        print(f"Loaded {len(words)} valid words.")
        return words
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return set()

# Load valid words
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'ValidWords.txt')
VALID_WORDS = load_valid_words(file_path)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 50))  # Extra space for score display
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)  # Font for drawing text

# Adjusted letter frequency distribution
LETTER_FREQUENCIES = {
    'A': 8.5, 'B': 1.49, 'C': 2.78, 'D': 5.0, 'E': 13.0,
    'F': 2.23, 'G': 2.02, 'H': 6.5, 'I': 7.5, 'J': 0.15,
    'K': 0.77, 'L': 4.03, 'M': 2.41, 'N': 7.0, 'O': 8.0,
    'P': 1.93, 'Q': 0.10, 'R': 6.5, 'S': 7.0, 'T': 10.0,
    'U': 2.76, 'V': 0.98, 'W': 2.36, 'X': 0.15, 'Y': 1.97, 'Z': 0.07
}

# Create a weighted list of letters based on frequency
weighted_letters = []
for letter, freq in LETTER_FREQUENCIES.items():
    weighted_letters.extend([letter] * int(freq * 10))  # Multiplying by 10 to get a more granular distribution

# Create a random grid of random letters
def create_grid():
    return [[random.choice(weighted_letters) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Constants for highlighting
HIGHLIGHT_COLOR = (0, 255, 0)  # Green
INVALID_COLOR = (255, 0, 0)    # Red
HINT_COLOR = (255, 255, 0)     # Yellow
HIGHLIGHT_THICKNESS = 4

# Function to draw the grid with random letters and highlighting for selected tiles
def draw_grid(grid, selected_tile=None, highlight_positions=set(), invalid_positions=set(), hint_position=None, display_score=True, offset=None, score=0, possible_words=0, time_left=60, hints_left=3):
    # Draw the grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pos_y = row * TILE_SIZE + 50
            if offset and (row, col) in offset:
                pos_y += offset[(row, col)]
            if highlight_positions and (row, col) in highlight_positions:
                # Highlight the valid word positions with green background
                pygame.draw.rect(
                    screen, HIGHLIGHT_COLOR,
                    (col * TILE_SIZE, pos_y, TILE_SIZE, TILE_SIZE), 0
                )
            elif invalid_positions and (row, col) in invalid_positions:
                # Highlight the invalid swap positions with red background
                pygame.draw.rect(
                    screen, INVALID_COLOR,
                    (col * TILE_SIZE, pos_y, TILE_SIZE, TILE_SIZE), 0
                )
            elif hint_position and (row, col) == hint_position:
                # Highlight the hint position with yellow background
                pygame.draw.rect(
                    screen, HINT_COLOR,
                    (col * TILE_SIZE, pos_y, TILE_SIZE, TILE_SIZE), 0
                )
            else:
                # Normal white background
                pygame.draw.rect(
                    screen, (255, 255, 255),
                    (col * TILE_SIZE, pos_y, TILE_SIZE, TILE_SIZE), 0
                )

            # Draw a black border around each tile
            pygame.draw.rect(
                screen, (0, 0, 0),
                (col * TILE_SIZE, pos_y, TILE_SIZE, TILE_SIZE), 2
            )

            # Draw the letter in the center of the tile
            letter = grid[row][col]
            if letter:
                text = font.render(letter, True, (0, 0, 0))  # Rendered in black
                text_rect = text.get_rect(center=(col * TILE_SIZE + TILE_SIZE // 2, pos_y + TILE_SIZE // 2))
                screen.blit(text, text_rect)

            # Highlight the selected tile with a thicker white border
            if selected_tile and selected_tile == (row, col):
                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    (col * TILE_SIZE, pos_y, TILE_SIZE, TILE_SIZE),
                    HIGHLIGHT_THICKNESS
                )

    # Draw the score
    if display_score:
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

    # Draw the hint button and the number of hints left
    hint_button = pygame.Rect(160, 10, 100, 40)
    pygame.draw.rect(screen, (255, 255, 0), hint_button)
    hint_text = font.render(f"Hint ({hints_left})", True, (0, 0, 0))
    screen.blit(hint_text, (hint_button.x + 5, hint_button.y + 5))

    # Draw the timer
    timer_text = font.render(f"Time Left: {time_left}", True, (255, 0, 0))
    screen.blit(timer_text, (WINDOW_SIZE // 2 - 50, 10))

    # Draw the number of possible words
    possible_words_text = font.render(f"Possible Words: {possible_words}", True, (0, 0, 0))
    screen.blit(possible_words_text, (WINDOW_SIZE - 250, 10))

    return hint_button

# Swap tiles
def swap_tiles(grid, pos1, pos2):
    grid[pos1[0]][pos1[1]], grid[pos2[0]][pos2[1]] = grid[pos2[0]][pos2[1]], grid[pos1[0]][pos1[1]]

# Check if the swap is valid (adjacent tiles)
def is_adjacent(pos1, pos2):
    row_diff = abs(pos1[0] - pos2[0])
    col_diff = abs(pos1[1] - pos2[1])
    return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)

# Check for valid words in rows and columns and return their positions
def check_for_words(grid):
    word_positions = set()

    # Check rows for words
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 4):  # We only need to check up to GRID_SIZE - 4 to avoid out of range
            word = ''.join(grid[row][col + i] for i in range(5))
            if word in VALID_WORDS:
                for i in range(5):
                    word_positions.add((row, col + i))

    # Check columns for words
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE - 4):  # We only need to check up to GRID_SIZE - 4 to avoid out of range
            word = ''.join(grid[row + i][col] for i in range(5))
            if word in VALID_WORDS:
                for i in range(5):
                    word_positions.add((row + i, col))

    return word_positions

# Check if there are possible moves that can form a valid word
def check_for_possible_moves(grid):
    possible_moves = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if col < GRID_SIZE - 1:
                swap_tiles(grid, (row, col), (row, col + 1))
                if check_for_words(grid):
                    possible_moves.append((row, col))
                swap_tiles(grid, (row, col), (row, col + 1))
            if row < GRID_SIZE - 1:
                swap_tiles(grid, (row, col), (row + 1, col))
                if check_for_words(grid):
                    possible_moves.append((row, col))
                swap_tiles(grid, (row, col), (row + 1, col))
    return possible_moves

# Display the game over screen with Play Again and Quit buttons
def display_game_over(score):
    play_again_button = pygame.Rect(WINDOW_SIZE // 2 - 100, WINDOW_SIZE // 2 - 30, 200, 50)
    quit_button = pygame.Rect(WINDOW_SIZE // 2 - 100, WINDOW_SIZE // 2 + 40, 200, 50)
    game_over = True

    while game_over:
        screen.fill((0, 0, 0))
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(game_over_text, (WINDOW_SIZE // 2 - game_over_text.get_width() // 2, WINDOW_SIZE // 2 - game_over_text.get_height() // 2 - 100))
        screen.blit(score_text, (WINDOW_SIZE // 2 - score_text.get_width() // 2, WINDOW_SIZE // 2 - score_text.get_height() // 2 - 50))

        pygame.draw.rect(screen, (0, 255, 0), play_again_button)
        pygame.draw.rect(screen, (255, 0, 0), quit_button)
        play_again_text = font.render("Play Again", True, (0, 0, 0))
        quit_text = font.render("Quit", True, (0, 0, 0))
        screen.blit(play_again_text, (play_again_button.x + 50, play_again_button.y + 10))
        screen.blit(quit_text, (quit_button.x + 70, quit_button.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos):
                    return True
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

    return False

# Remove the tiles that form valid words and update score
def remove_words(grid, word_positions, update_score=True):
    global score
    for row, col in word_positions:
        grid[row][col] = None
    if update_score:
        score += len(word_positions) * 100

# Make the tiles above fall down to fill the gaps
def collapse_grid_with_animation(grid):
    offset = {}
    for col in range(GRID_SIZE):
        empty_spots = []
        for row in reversed(range(GRID_SIZE)):
            if grid[row][col] is None:
                empty_spots.append(row)
            elif empty_spots:
                target_row = empty_spots.pop(0)
                grid[target_row][col] = grid[row][col]
                grid[row][col] = None
                empty_spots.append(row)

        # Animate the falling tiles
        for step in range(0, TILE_SIZE, 10):
            screen.fill((255, 255, 255))
            offset = {}
            for row in range(GRID_SIZE):
                if grid[row][col] is not None:
                    offset[(row, col)] = min(step, TILE_SIZE) if row in empty_spots else 0
            draw_grid(grid, offset=offset, display_score=False)
            pygame.display.flip()
            clock.tick(60)  # Limit the frame rate to 60 FPS

# Generate new random tiles for the empty spaces at the top
def refill_grid_with_animation(grid):
    new_tiles = []
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE):
            if grid[row][col] is None:
                grid[row][col] = random.choice(weighted_letters)
                new_tiles.append((row, col))

    # Animate the new tiles falling down
    for step in range(0, TILE_SIZE, 10):
        screen.fill((255, 255, 255))
        offset = {pos: min(step, TILE_SIZE) for pos in new_tiles}
        draw_grid(grid, offset=offset, display_score=False)
        pygame.display.flip()
        clock.tick(60)  # Limit the frame rate to 60 FPS

# Function to process the grid for any new words until no more are found
def process_grid(grid, update_score=True):
    while True:
        word_positions = check_for_words(grid)
        if word_positions:
            print("Valid word positions after drop:", word_positions)
            draw_grid(grid, highlight_positions=word_positions, display_score=False)
            pygame.display.flip()
            pygame.time.wait(1000)  # Wait for 1000 milliseconds (1 second)
            remove_words(grid, word_positions, update_score)
            collapse_grid_with_animation(grid)
            refill_grid_with_animation(grid)
        else:
            break

# Game loop
def main():
    global score
    while True:
        selected_tile = None
        hint_used = False
        hint_position = None
        hints_left = 3  # Start with 3 hints
        grid = create_grid()

        score = 0  # Reset the score for a new game
        process_grid(grid, update_score=False)  # Ensure no initial words and don't count towards score
        possible_moves = check_for_possible_moves(grid)  # Initial count of possible moves
        start_time = time.time()  # Start the timer

        while True:
            current_time = time.time()
            time_left = max(60 - int(current_time - start_time), 0)  # Calculate remaining time

            if time_left == 0:
                if display_game_over(score):
                    return  # Breaks out of the inner loop and restarts the game
                else:
                    pygame.quit()
                    sys.exit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Get the clicked tile
                    x, y = event.pos
                    if y >= 50:  # Ignore clicks in the score display area
                        row = (y - 50) // TILE_SIZE
                        col = x // TILE_SIZE
                        if selected_tile is None:
                            selected_tile = (row, col)
                        else:
                            new_tile = (row, col)
                            if is_adjacent(selected_tile, new_tile):
                                # Swap tiles if they're adjacent
                                swap_tiles(grid, selected_tile, new_tile)

                                # Check for words after swapping
                                word_positions = check_for_words(grid)
                                if word_positions:
                                    print("Valid word positions:", word_positions)
                                    # Highlight the words briefly
                                    screen.fill((255, 255, 255))
                                    draw_grid(grid, None, word_positions, score=score, possible_words=len(possible_moves), time_left=time_left, hints_left=hints_left)
                                    pygame.display.flip()
                                    pygame.time.wait(1000)  # Wait for 1000 milliseconds (1 second)

                                    # Remove the words and update score
                                    remove_words(grid, word_positions)
                                    # Collapse the grid
                                    collapse_grid_with_animation(grid)
                                    # Refill the grid with animation
                                    refill_grid_with_animation(grid)
                                    # Process the grid for any new words
                                    process_grid(grid)

                                    start_time = time.time()  # Reset the timer after finding a word
                                    hint_used = False  # Reset hint usage
                                    hint_position = None
                                else:
                                    # Highlight invalid swap positions
                                    draw_grid(grid, selected_tile, invalid_positions={selected_tile, new_tile}, score=score, possible_words=len(possible_moves), time_left=time_left, hints_left=hints_left)
                                    pygame.display.flip()
                                    pygame.time.wait(500)  # Wait for 500 milliseconds (0.5 second)
                                    
                                    # Swap back if no valid word is found and apply time penalty
                                    swap_tiles(grid, selected_tile, new_tile)
                                    start_time -= 5  # Subtract 5 seconds as penalty

                                    # If a hint was used, automatically lose the game
                                    if hint_used:
                                        if display_game_over(score):
                                            return  # Breaks out of the inner loop and restarts the game
                                        else:
                                            pygame.quit()
                                            sys.exit()

                                selected_tile = None  # Reset selected tile
                                
                                # Update the count of possible moves
                                possible_moves = check_for_possible_moves(grid)
                                
                                # Check for game over condition
                                if len(possible_moves) == 0:
                                    if display_game_over(score):
                                        return  # Breaks out of the inner loop and restarts the game
                                    else:
                                        pygame.quit()
                                        sys.exit()
                            else:
                                selected_tile = None  # Reset if the tiles aren't adjacent
                    else:
                        hint_button = draw_grid(grid, selected_tile, score=score, possible_words=len(possible_moves), time_left=time_left, hints_left=hints_left)
                        if hint_button.collidepoint(event.pos) and not hint_used and hints_left > 0 and possible_moves:
                            hint_position = random.choice(possible_moves)
                            hint_used = True
                            hints_left -= 1

            # Draw the grid with the selected tile and hint highlighted
            screen.fill((255, 255, 255))
            hint_button = draw_grid(grid, selected_tile, score=score, possible_words=len(possible_moves), time_left=time_left, hint_position=hint_position, hints_left=hints_left)
            pygame.display.flip()

            clock.tick(30)

if __name__ == "__main__":
    while True:
        main()
