import pygame
import random
import time
from collections import deque

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 850
WINDOW_HEIGHT = 950
GRID_SIZE = 100
GRID_START_X = 25
GRID_START_Y = 25
GRID_END_X = 825
GRID_END_Y = 825
GRID_PIXEL_SIZE = 8
SLIDER_HEIGHT = 100
STEP_DELAY = 0.25

# Colors
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
LIGHT_GREY = (225,225,225)


class PercolationSimulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Percolation Simulation")
        self.clock = pygame.time.Clock()

        # Grid state: 0 = empty, 1 = filled, 2 = percolated
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.p = 0.5  # Percolation probability
        self.running = True
        self.percolating = False
        self.percolation_queue = deque()
        self.last_step_time = time.time()

        # Sliders
        self.slider_width = 300
        self.slider_height = 15

        # Probability slider
        self.p_slider_x = 50
        self.p_slider_y = WINDOW_HEIGHT - 80
        self.p_slider_dragging = False

        # Tick time slider
        self.tick_slider_x = 450
        self.tick_slider_y = WINDOW_HEIGHT - 80
        self.tick_slider_dragging = False
        self.tick_time = 0.01 # Current tick time
        self.min_tick_time = 0.01  # Minimum tick time (fast)
        self.max_tick_time = 1.0   # Maximum tick time (slow)

        self.reset_simulation()

    def reset_simulation(self):
        """Reset the simulation with all squares white except middle square red"""
        # Initialize all squares as white (empty)
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Clear percolation queue
        self.percolation_queue = deque()

        # Set middle square to red (percolated)
        middle = GRID_SIZE // 2
        self.grid[middle][middle] = 2  # Mark as percolated (red)

        self.percolating = True

    def get_neighbors(self, row, col):
        """Get valid neighboring cells"""
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                neighbors.append((new_row, new_col))

        return neighbors

    def percolation_step(self):
        """Perform one step of probabilistic percolation"""
        if not self.percolating:
            return

        # Find all current red squares
        red_squares = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == 2:  # Red square
                    red_squares.append((i, j))

        # If no red squares, stop percolating
        if not red_squares:
            self.percolating = False
            return

        # For each red square, try to spread to adjacent white squares with probability p
        new_red_squares = []
        for row, col in red_squares:
            for neighbor_row, neighbor_col in self.get_neighbors(row, col):
                if self.grid[neighbor_row][neighbor_col] == 0:  # White (empty) square
                    if random.random() < self.p:  # With probability p
                        self.grid[neighbor_row][neighbor_col] = 2  # Make it red
                        new_red_squares.append((neighbor_row, neighbor_col))

        # Turn all old red squares to blue
        for row, col in red_squares:
            self.grid[row][col] = 1  # Mark as blue (filled)

        # If no new red squares were created, stop percolating
        if not new_red_squares:
            self.percolating = False

    def handle_slider(self, mouse_pos, mouse_pressed):
        """Handle slider interaction"""
        mouse_x, mouse_y = mouse_pos

        # Handle probability slider
        if mouse_pressed[0]:  # Left mouse button
            if (self.p_slider_x <= mouse_x <= self.p_slider_x + self.slider_width and
                    self.p_slider_y <= mouse_y <= self.p_slider_y + self.slider_height):
                self.p_slider_dragging = True

        if self.p_slider_dragging:
            if mouse_pressed[0]:
                # Update p value based on slider position
                relative_x = mouse_x - self.p_slider_x
                relative_x = max(0, min(relative_x, self.slider_width))
                self.p = relative_x / self.slider_width
            else:
                self.p_slider_dragging = False

        # Handle tick time slider
        if mouse_pressed[0]:  # Left mouse button
            if (self.tick_slider_x <= mouse_x <= self.tick_slider_x + self.slider_width and
                    self.tick_slider_y <= mouse_y <= self.tick_slider_y + self.slider_height):
                self.tick_slider_dragging = True

        if self.tick_slider_dragging:
            if mouse_pressed[0]:
                # Update tick time based on slider position
                relative_x = mouse_x - self.tick_slider_x
                relative_x = max(0, min(relative_x, self.slider_width))
                self.tick_time = self.min_tick_time + (
                        relative_x / self.slider_width) * (self.max_tick_time - self.min_tick_time)
            else:
                self.tick_slider_dragging = False

    def draw_grid(self):
        """Draw the percolation grid"""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = GRID_START_X + j * GRID_PIXEL_SIZE
                y = GRID_START_Y + i * GRID_PIXEL_SIZE

                # Choose color based on cell state
                if self.grid[i][j] == 0:  # Empty
                    color = WHITE
                elif self.grid[i][j] == 1:  # Filled
                    color = BLUE
                else:  # Percolated
                    color = RED

                # Draw cell
                pygame.draw.rect(self.screen, color,
                                 (x, y, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE))

                # Draw grid lines
                pygame.draw.rect(self.screen, GREY,
                                 (x, y, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), 1)

    def draw_sliders(self):
        """Draw the probability and tick time sliders"""
        # Draw probability slider background
        pygame.draw.rect(self.screen, LIGHT_GREY,
                         (self.p_slider_x, self.p_slider_y, self.slider_width, self.slider_height))

        # Draw probability slider handle
        p_handle_x = self.p_slider_x + int(self.p * self.slider_width)
        pygame.draw.circle(self.screen, BLACK,
                           (p_handle_x, self.p_slider_y + self.slider_height // 2), 10)

        # Draw tick time slider background
        pygame.draw.rect(self.screen, LIGHT_GREY,
                         (self.tick_slider_x, self.tick_slider_y, self.slider_width, self.slider_height))

        # Draw tick time slider handle
        tick_handle_x = self.tick_slider_x + int(
            (self.tick_time - self.min_tick_time) / (self.max_tick_time - self.min_tick_time) * self.slider_width)
        pygame.draw.circle(self.screen, BLACK,
                           (tick_handle_x, self.tick_slider_y + self.slider_height // 2), 10)

        # Draw labels
        font = pygame.font.Font(None, 36)
        p_text = font.render(f"p = {self.p:.2f}", True, BLACK)
        self.screen.blit(p_text, (self.p_slider_x, self.p_slider_y - 30))

        tick_time_text = font.render(f"Tick time = {self.tick_time:.2f}s", True, BLACK)
        self.screen.blit(tick_time_text, (self.tick_slider_x, self.tick_slider_y - 30))

        # Draw instructions
        instruction_text = font.render("Space: Reset | Drag sliders: Change p and tick time", True, BLACK)
        self.screen.blit(instruction_text, (self.p_slider_x, self.p_slider_y + 30))

    def run(self):
        """Main game loop"""
        while self.running:
            current_time = time.time()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.reset_simulation()

            # Handle sliders
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            self.handle_slider(mouse_pos, mouse_pressed)

            # Perform percolation step
            if self.percolating and current_time - self.last_step_time >= self.tick_time:
                self.percolation_step()
                self.last_step_time = current_time

            # Draw everything
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_sliders()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


# Run the simulation
if __name__ == "__main__":
    sim = PercolationSimulation()
    sim.run()