"""
MP3 Metadata Generation Progress Bar Module
Displays a pygame progress bar in a separate thread during MP3 metadata generation
"""

import pygame
import threading
from typing import Optional, Callable


class MetadataProgressBar:
    """
    A threaded progress bar for MP3 metadata generation.
    Runs in a separate thread to avoid blocking the main process.
    """

    def __init__(self, total_files: int, window_title: str = "Convergence Jukebox Welcome"):
        """
        Initialize the progress bar.

        Args:
            total_files (int): Total number of files to process
            window_title (str): Title for the progress bar window
        """
        self.total_files = total_files
        self.window_title = window_title
        self.current_count = 0
        self.current_file = ""
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()

        # Pygame objects
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None

        # Window settings
        self.window_width = 450
        self.window_height = 160

    def start(self) -> bool:
        """
        Start the progress bar in a separate thread.

        Returns:
            bool: True if successfully started, False otherwise
        """
        try:
            if self.running:
                print("Progress bar is already running")
                return False

            self.running = True
            self.stop_flag.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("Metadata progress bar started")
            return True

        except Exception as e:
            print(f"Error starting progress bar: {e}")
            self.running = False
            return False

    def _run(self):
        """
        Main progress bar loop (runs in separate thread).
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            pygame.display.set_caption(self.window_title)
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 20)
            self.small_font = pygame.font.Font(None, 16)

            while self.running and not self.stop_flag.is_set():
                self._draw()
                self._handle_events()
                self.clock.tick(10)  # Update 10 times per second

            pygame.quit()
            print("Metadata progress bar closed")

        except Exception as e:
            print(f"Error in progress bar thread: {e}")
        finally:
            self.running = False

    def _draw(self):
        """
        Draw the progress bar UI.
        """
        try:
            # Clear screen with dark background
            self.screen.fill((30, 30, 30))

            # Draw title
            title_text = self.font.render("Loading Your Music Collection...", True, (255, 255, 255))
            self.screen.blit(title_text, (10, 10))

            # Calculate progress percentage
            progress_percent = (self.current_count / self.total_files) * 100 if self.total_files > 0 else 0

            # Draw progress bar background
            bar_width = self.window_width - 20
            bar_height = 20
            bar_x = 10
            bar_y = 40
            pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

            # Draw progress bar fill (green)
            fill_width = int(bar_width * (progress_percent / 100))
            if fill_width > 0:
                pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height))

            # Draw progress percentage and count
            progress_text = self.small_font.render(
                f"{progress_percent:.1f}% ({self.current_count}/{self.total_files})",
                True,
                (255, 255, 255)
            )
            self.screen.blit(progress_text, (10, 68))

            # Draw current filename (truncated if too long)
            max_filename_length = 60
            if len(self.current_file) > max_filename_length:
                display_filename = "..." + self.current_file[-max_filename_length:]
            else:
                display_filename = self.current_file

            filename_text = self.small_font.render(
                f"Processing: {display_filename}",
                True,
                (200, 200, 200)
            )
            self.screen.blit(filename_text, (10, 88))

            # Draw status line
            status_text = self.small_font.render(
                "Processing files...",
                True,
                (150, 255, 150)
            )
            self.screen.blit(status_text, (10, 110))

            pygame.display.flip()

        except Exception as e:
            print(f"Error drawing progress bar: {e}")

    def _handle_events(self):
        """
        Handle pygame events.
        """
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_flag.set()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.stop_flag.set()
        except Exception as e:
            print(f"Error handling events: {e}")

    def update(self, current_count: int, current_file: str):
        """
        Update the progress bar with new values.

        Args:
            current_count (int): Current file count
            current_file (str): Name of the current file being processed
        """
        self.current_count = current_count
        self.current_file = current_file

    def stop(self):
        """
        Stop the progress bar thread.
        """
        if self.running:
            self.stop_flag.set()
            self.running = False
            if self.thread:
                self.thread.join(timeout=2)
            print("Metadata progress bar stopped")

    def close(self):
        """
        Alias for stop() for convenience.
        """
        self.stop()
