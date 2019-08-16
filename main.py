import pygame
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["SDL_VIDEO_MAC_FULLSCREEN_SPACES"] = "0"


def configure_app():
    """Tkinter setup window for initial configuration."""
    root = tk.Tk()
    root.withdraw()

    try:
        rows = simpledialog.askinteger("Rows", "Enter number of rows (e.g., 50):", minvalue=1, maxvalue=100)
        cols = simpledialog.askinteger("Columns", "Enter number of columns (e.g., 50):", minvalue=1, maxvalue=100)
        show_grid_input = simpledialog.askstring("Show Grid", "Show grid lines? (yes/no):", initialvalue="yes")
        show_grid = show_grid_input.lower() == "yes"
        root.destroy()
        return rows, cols, show_grid
    except Exception as e:
        root.destroy()
        print(f"Error during configuration: {e}")
        raise


class PixelArtApp:
    def __init__(self, width=600, height=600, rows=50, cols=50, show_grid=True):
        pygame.init()
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.show_grid = show_grid
        self.grid = [[(255, 255, 255) for _ in range(cols)] for _ in range(rows)]
        self.current_color = (0, 0, 0)  # Default color is black
        self.thickness = 1
        self.selected_tool = "Draw"
        self.tools = ["Draw", "Erase", "Fill", "Clear", "Save", "Load"]
        self.colors = [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]
        self.selected_color_index = 0
        self.screen = pygame.display.set_mode((self.width, self.height + 150))
        pygame.display.set_caption("PixelCanvas")
        self.clock = pygame.time.Clock()

    def draw_grid(self):
        block_width = self.width // self.cols
        block_height = self.height // self.rows

        for row in range(self.rows):
            for col in range(self.cols):
                color = self.grid[row][col]
                rect = pygame.Rect(col * block_width, row * block_height, block_width, block_height)
                pygame.draw.rect(self.screen, color, rect)

                if self.show_grid:
                    pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def handle_click(self, pos):
        if pos[1] > self.height:
            return
        row = pos[1] // (self.height // self.rows)
        col = pos[0] // (self.width // self.cols)

        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.selected_tool == "Draw":
                self.grid[row][col] = self.current_color
            elif self.selected_tool == "Erase":
                self.grid[row][col] = (255, 255, 255)
            elif self.selected_tool == "Fill":
                self.flood_fill(row, col, self.grid[row][col], self.current_color)

    def flood_fill(self, row, col, target_color, replacement_color):
        if target_color == replacement_color:
            return
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            if self.grid[r][c] == target_color:
                self.grid[r][c] = replacement_color
                neighbors = [
                    (r + 1, c),
                    (r - 1, c),
                    (r, c + 1),
                    (r, c - 1),
                ]
                for nr, nc in neighbors:
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        stack.append((nr, nc))

    def clear_grid(self):
        self.grid = [[(255, 255, 255) for _ in range(self.cols)] for _ in range(self.rows)]

    def save_to_file(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return
        try:
            with open(file_path, 'w') as file:
                file.write(f"{self.rows} {self.cols}\n")
                for row in self.grid:
                    file.write(" ".join(",".join(map(str, color)) for color in row) + "\n")
            messagebox.showinfo("Success", "File saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def load_from_file(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                self.rows, self.cols = map(int, lines[0].split())
                self.grid = [
                    [tuple(map(int, color.split(','))) for color in line.strip().split()]
                    for line in lines[1:]
                ]
            self.show_grid = True
            pygame.display.set_mode((self.width, self.height + 150))  # Adjust grid size if needed
            messagebox.showinfo("Success", "File loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {e}")

    def draw_tools(self):
        tool_width = self.width // len(self.tools)
        pygame.draw.rect(self.screen, (220, 220, 220), (0, self.height, self.width, 50))
        font = pygame.font.SysFont(None, 30)

        for i, tool in enumerate(self.tools):
            x = i * tool_width
            y = self.height
            rect = pygame.Rect(x, y, tool_width, 50)

            # Highlight the selected tool
            if tool == self.selected_tool:
                pygame.draw.rect(self.screen, (180, 180, 250), rect)
            else:
                pygame.draw.rect(self.screen, (220, 220, 220), rect)

            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)  # Border for each button
            text = font.render(tool, True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def draw_color_palette(self):
        color_width = self.width // len(self.colors)
        y_offset = self.height + 50
        for i, color in enumerate(self.colors):
            x = i * color_width
            rect = pygame.Rect(x, y_offset, color_width, 50)

            if i == self.selected_color_index:
                pygame.draw.rect(self.screen, (200, 200, 200), rect)
            else:
                pygame.draw.rect(self.screen, color, rect)

            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

    def handle_tool_click(self, pos):
        tool_width = self.width // len(self.tools)
        if pos[1] > self.height and pos[1] <= self.height + 50:
            index = pos[0] // tool_width
            if 0 <= index < len(self.tools):
                selected_tool = self.tools[index]
                if selected_tool == "Clear":
                    self.clear_grid()
                elif selected_tool == "Save":
                    self.save_to_file()
                elif selected_tool == "Load":
                    self.load_from_file()
                else:
                    self.selected_tool = selected_tool

    def handle_color_click(self, pos):
        color_width = self.width // len(self.colors)
        if pos[1] > self.height + 50:
            index = pos[0] // color_width
            if 0 <= index < len(self.colors):
                self.selected_color_index = index
                self.current_color = self.colors[index]

    def run(self):
        running = True
        while running:
            self.screen.fill((255, 255, 255))
            self.draw_grid()
            self.draw_tools()
            self.draw_color_palette()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if pos := event.pos:
                        if pos[1] > self.height + 50:
                            self.handle_color_click(pos)
                        elif pos[1] > self.height:
                            self.handle_tool_click(pos)
                        else:
                            self.handle_click(pos)

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    rows, cols, show_grid = configure_app()
    app = PixelArtApp(rows=rows, cols=cols, show_grid=show_grid)
    app.run()
