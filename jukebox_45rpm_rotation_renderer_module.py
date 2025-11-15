"""
Jukebox 45RPM Rotation Renderer Module
Displays a rotating vinyl record with authentic Wurlitzer paddle tonearm animation.

This module provides a visual simulation of a jukebox turntable with:
- Rotating 45 RPM vinyl record
- Authentic Wurlitzer paddle-style tonearm
- Smooth tonearm animations (park -> play -> end -> park)
- Realistic tracking movement across the record

Usage:
    from jukebox_45rpm_rotation_renderer_module import display_record_with_tonearm

    # Display with default 30-second playback
    display_record_with_tonearm('final_record_pressing.png')

    # Display with custom duration
    display_record_with_tonearm('final_record_pressing.png', duration=45)

    # Loop forever until window closed
    display_record_with_tonearm('final_record_pressing.png', duration=None)
"""

import pygame
import math
from enum import Enum


# ============================================================================
# TONEARM STATE AND BASE CLASS
# ============================================================================

class ToneArmState(Enum):
    """States for tonearm animation."""
    PARKED = "parked"
    SWINGING_OUT = "swinging_out"
    LOWERING = "lowering"
    PLAYING = "playing"
    LIFTING = "lifting"
    RETURNING = "returning"


class ToneArm:
    """
    Base class for turntable tonearm with animation states.
    Provides common functionality for tonearm movement and state management.
    """

    def __init__(self, x, y, length=200):
        """
        Initialize tonearm at pivot position.

        Args:
            x: X coordinate of pivot point
            y: Y coordinate of pivot point
            length: Length of tonearm in pixels
        """
        self.pivot_x = x
        self.pivot_y = y
        self.length = length

        # Angle positions (in degrees)
        self.park_angle = -90      # Parked position
        self.play_angle = -45      # Playing start position
        self.end_angle = -20       # End of record position
        self.current_angle = -90   # Current angle
        self.target_angle = -90    # Target angle for smooth movement

        # State management
        self.state = ToneArmState.PARKED

        # Animation parameters
        self.swing_speed = 45      # degrees per second (swing out/return)
        self.lower_speed = 2.0     # seconds to lower/lift
        self.lower_timer = 0.0
        self.current_height = 0    # Vertical offset (0 = down, positive = up)
        self.lift_height = 30      # How high to lift when moving

        # Visual effects
        self.play_wobble = 0       # Small wobble during playback
        self.wobble_timer = 0

        # Colors (can be overridden by subclasses)
        self.needle_color = (200, 50, 50)

    def play_record(self):
        """Start playing - swing out to record."""
        if self.state == ToneArmState.PARKED:
            self.state = ToneArmState.SWINGING_OUT
            self.target_angle = self.play_angle
            self.current_height = self.lift_height

    def return_to_park(self):
        """Return to parked position."""
        if self.state == ToneArmState.PLAYING:
            self.state = ToneArmState.LIFTING
            self.lower_timer = 0.0

    def is_playing(self):
        """Check if currently playing."""
        return self.state == ToneArmState.PLAYING

    def is_parked(self):
        """Check if parked."""
        return self.state == ToneArmState.PARKED

    def get_state(self):
        """Get current state."""
        return self.state

    def update(self, dt):
        """
        Update tonearm animation.

        Args:
            dt: Delta time in seconds
        """
        # Update wobble effect during playback
        if self.state == ToneArmState.PLAYING:
            self.wobble_timer += dt * 3
            self.play_wobble = math.sin(self.wobble_timer) * 0.5
        else:
            self.play_wobble = 0

        # State machine for tonearm movement
        if self.state == ToneArmState.SWINGING_OUT:
            # Swing from park to play position
            angle_diff = self.target_angle - self.current_angle
            if abs(angle_diff) > 0.5:
                move = self.swing_speed * dt
                if angle_diff > 0:
                    self.current_angle += min(move, angle_diff)
                else:
                    self.current_angle += max(-move, angle_diff)
            else:
                self.current_angle = self.target_angle
                self.state = ToneArmState.LOWERING
                self.lower_timer = 0.0

        elif self.state == ToneArmState.LOWERING:
            # Lower onto record
            self.lower_timer += dt
            progress = min(self.lower_timer / self.lower_speed, 1.0)
            self.current_height = self.lift_height * (1.0 - progress)

            if progress >= 1.0:
                self.current_height = 0
                self.state = ToneArmState.PLAYING

        elif self.state == ToneArmState.LIFTING:
            # Lift from record
            self.lower_timer += dt
            progress = min(self.lower_timer / self.lower_speed, 1.0)
            self.current_height = self.lift_height * progress

            if progress >= 1.0:
                self.current_height = self.lift_height
                self.state = ToneArmState.RETURNING
                self.target_angle = self.park_angle

        elif self.state == ToneArmState.RETURNING:
            # Return to park position
            angle_diff = self.target_angle - self.current_angle
            if abs(angle_diff) > 0.5:
                move = self.swing_speed * dt
                if angle_diff > 0:
                    self.current_angle += min(move, angle_diff)
                else:
                    self.current_angle += max(-move, angle_diff)
            else:
                self.current_angle = self.target_angle
                self.current_height = 0
                self.state = ToneArmState.PARKED

    def draw(self, surface):
        """
        Draw the tonearm. Override in subclasses for specific designs.

        Args:
            surface: Pygame surface to draw on
        """
        pass


# ============================================================================
# WURLITZER PADDLE TONEARM
# ============================================================================

class WurlitzerPaddleToneArm(ToneArm):
    """
    Authentic Wurlitzer jukebox tonearm with paddle design.
    Features straight tapered arm with large circular head and flared base.
    """

    def __init__(self, x, y, length=260):
        super().__init__(x, y, length)

        # Tonearm dimensions
        self.arm_length = length * 0.85       # Main paddle arm
        self.head_radius = length * 0.15      # Large circular head at top
        self.base_width = 100                 # Flared base width (pixels)
        self.top_width = 100                  # Top width of paddle (pixels)

        # Angle positions (override parent class defaults)
        self.park_angle = -80        # Parked position (more backward)
        self.play_angle = -44        # Playing position (start)
        self.end_angle = -20         # End position
        self.current_angle = -80     # Start at park position
        self.target_angle = -80      # Initial target

        # Visual parameters
        self.arm_color = (140, 140, 145)          # Gray metal
        self.arm_shadow = (100, 100, 105)         # Darker edge
        self.arm_highlight = (170, 170, 175)      # Light edge
        self.head_color = (130, 130, 135)         # Cartridge head
        self.base_color = (120, 120, 125)         # Base/pivot area
        self.pivot_brass = (180, 150, 100)        # Brass pivot hardware

    def update(self, dt):
        """Override parent update to handle tracking movement during playback."""
        # Call parent update first
        super().update(dt)

        # Additional tracking movement during PLAYING state
        if self.is_playing():
            # Smoothly move toward target angle during playback
            angle_diff = self.target_angle - self.current_angle
            if abs(angle_diff) > 0.1:
                # Slow, continuous tracking movement
                move_speed = 5  # degrees per second
                if angle_diff > 0:
                    self.current_angle += min(move_speed * dt, angle_diff)
                else:
                    self.current_angle += max(-move_speed * dt, angle_diff)

    def draw(self, surface):
        """
        Draw the Wurlitzer paddle-style tonearm.

        Args:
            surface: Pygame surface to draw on
        """
        # Calculate the actual pivot position with height offset
        pivot_x = self.pivot_x
        pivot_y = self.pivot_y + self.current_height

        # Base angle (for bottom pivot - arm extends upward)
        angle_rad = math.radians(self.current_angle + self.play_wobble)

        # Calculate head center position (top of arm)
        head_x = pivot_x + self.arm_length * math.sin(angle_rad)
        head_y = pivot_y - self.arm_length * math.cos(angle_rad)

        # Calculate the four corners of the tapered paddle
        # Bottom corners (wider)
        base_half = self.base_width / 2
        perp_angle = angle_rad + math.pi / 2

        base_left_x = pivot_x + base_half * math.cos(perp_angle)
        base_left_y = pivot_y + base_half * math.sin(perp_angle)
        base_right_x = pivot_x - base_half * math.cos(perp_angle)
        base_right_y = pivot_y - base_half * math.sin(perp_angle)

        # Top corners (narrower, at base of head)
        top_half = self.top_width / 2
        top_offset = self.arm_length * 0.85  # Leave room for head

        top_center_x = pivot_x + top_offset * math.sin(angle_rad)
        top_center_y = pivot_y - top_offset * math.cos(angle_rad)

        top_left_x = top_center_x + top_half * math.cos(perp_angle)
        top_left_y = top_center_y + top_half * math.sin(perp_angle)
        top_right_x = top_center_x - top_half * math.cos(perp_angle)
        top_right_y = top_center_y - top_half * math.sin(perp_angle)

        # Draw the flared base (bell shape)
        base_flare = self.base_width * 0.8
        base_points = []
        for i in range(8):
            angle_offset = (i / 7 - 0.5) * math.pi * 0.6
            base_angle = perp_angle + angle_offset
            bx = pivot_x + base_flare * math.cos(base_angle)
            by = pivot_y + base_flare * math.sin(base_angle)
            base_points.append((int(bx), int(by)))

        pygame.draw.polygon(surface, self.base_color, base_points)
        pygame.draw.polygon(surface, self.arm_shadow, base_points, 2)

        # Draw the main paddle arm (tapered trapezoid)
        paddle_points = [
            (int(base_left_x), int(base_left_y)),
            (int(base_right_x), int(base_right_y)),
            (int(top_right_x), int(top_right_y)),
            (int(top_left_x), int(top_left_y))
        ]

        # Main paddle body
        pygame.draw.polygon(surface, self.arm_color, paddle_points)

        # Left edge highlight (much thicker for wide paddle)
        pygame.draw.line(surface, self.arm_highlight,
                        (int(base_left_x), int(base_left_y)),
                        (int(top_left_x), int(top_left_y)), 50)

        # Right edge shadow (much thicker for wide paddle)
        pygame.draw.line(surface, self.arm_shadow,
                        (int(base_right_x), int(base_right_y)),
                        (int(top_right_x), int(top_right_y)), 50)

        # Draw the large circular head (cartridge assembly)
        pygame.draw.circle(surface, self.head_color,
                          (int(head_x), int(head_y)), int(self.head_radius))

        # Head outline
        pygame.draw.circle(surface, self.arm_shadow,
                          (int(head_x), int(head_y)), int(self.head_radius), 2)

        # Two parallel grooves on the head
        groove_length = self.head_radius * 0.6
        groove_spacing = self.head_radius * 0.25
        groove_angle = angle_rad

        for offset in [-groove_spacing, groove_spacing]:
            groove_start_x = head_x + offset * math.cos(perp_angle) - (groove_length/2) * math.sin(groove_angle)
            groove_start_y = head_y + offset * math.sin(perp_angle) + (groove_length/2) * math.cos(groove_angle)
            groove_end_x = head_x + offset * math.cos(perp_angle) + (groove_length/2) * math.sin(groove_angle)
            groove_end_y = head_y + offset * math.sin(perp_angle) - (groove_length/2) * math.cos(groove_angle)

            pygame.draw.line(surface, self.arm_shadow,
                           (int(groove_start_x), int(groove_start_y)),
                           (int(groove_end_x), int(groove_end_y)), 2)

        # Draw needle extending from bottom of head
        needle_length = self.head_radius * 0.4
        needle_x = head_x + (self.head_radius + needle_length) * math.sin(angle_rad)
        needle_y = head_y - (self.head_radius + needle_length) * math.cos(angle_rad)

        pygame.draw.line(surface, (80, 80, 85),
                        (head_x, head_y), (needle_x, needle_y), 3)

        # Needle tip
        pygame.draw.circle(surface, self.needle_color,
                          (int(needle_x), int(needle_y)), 3)

        # Draw brass pivot mechanism (visible on the arm)
        pivot_pos_y = pivot_y - self.arm_length * 0.3
        pivot_pos_x = pivot_x + self.arm_length * 0.3 * math.sin(angle_rad)

        pygame.draw.circle(surface, self.pivot_brass,
                          (int(pivot_pos_x), int(pivot_pos_y)), 8)
        pygame.draw.circle(surface, (150, 120, 80),
                          (int(pivot_pos_x), int(pivot_pos_y)), 8, 2)
        pygame.draw.circle(surface, (100, 80, 50),
                          (int(pivot_pos_x), int(pivot_pos_y)), 3)

        # Draw main pivot point at base
        pygame.draw.circle(surface, self.base_color, (pivot_x, pivot_y), 15)
        pygame.draw.circle(surface, self.arm_shadow, (pivot_x, pivot_y), 15, 2)
        pygame.draw.circle(surface, (80, 80, 85), (pivot_x, pivot_y), 6)
        pygame.draw.circle(surface, (60, 60, 65), (pivot_x, pivot_y), 3)


# ============================================================================
# MAIN DISPLAY FUNCTION
# ============================================================================

def display_record_with_tonearm(image_path, duration=30):
    """
    Display a rotating vinyl record with authentic Wurlitzer tonearm animation.

    This function creates a visual simulation of a jukebox turntable with:
    - Rotating 45 RPM vinyl record
    - Authentic Wurlitzer paddle-style tonearm with realistic animations
    - Smooth transitions (park -> swing out -> lower -> play -> lift -> return)
    - Tonearm tracking movement across the record during playback

    Args:
        image_path: Path to the record image (e.g., 'final_record_pressing.png')
        duration: Playback duration in seconds (default: 30)
                 Set to None to loop forever until window is closed

    Example:
        # Play for 30 seconds (default)
        display_record_with_tonearm('final_record_pressing.png')

        # Play for 45 seconds
        display_record_with_tonearm('final_record_pressing.png', duration=45)

        # Loop forever
        display_record_with_tonearm('final_record_pressing.png', duration=None)
    """
    # Initialize pygame
    pygame.init()

    # Display settings
    WIDTH = 800
    HEIGHT = 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jukebox 45RPM - Wurlitzer Tonearm")

    # Colors
    bg_color = (25, 20, 30)           # Dark background
    panel_color = (40, 35, 45)        # Panel color
    brown_background = (101, 67, 33)  # Dark brown for record background

    # Load and scale record image
    try:
        record_image = pygame.image.load(image_path)
        record_image = pygame.transform.scale(record_image, (288, 288))
        record_original = record_image.copy()
    except Exception as e:
        print(f"Error loading image '{image_path}': {e}")
        pygame.quit()
        return

    # Record position and rotation
    record_x = 400
    record_y = 400
    record_rotation = 0

    # Create Wurlitzer tonearm
    tonearm = WurlitzerPaddleToneArm(x=400, y=560, length=220)

    # Timing and animation settings
    clock = pygame.time.Clock()
    FPS = 60

    auto_start_delay = 2.0      # Wait 2 seconds before auto-playing
    elapsed_time = 0            # Time since app started
    auto_started = False        # Flag to track if auto-start happened

    play_time = 0               # Elapsed time while playing
    track_duration = duration if duration else 30  # Use provided duration

    end_wait_delay = 2.0        # Wait 2 seconds at end before stopping
    end_wait_time = 0           # Time waiting at end
    waiting_at_end = False      # Flag to track if waiting at end

    loop_forever = (duration is None)  # Loop mode flag

    running = True

    print("\n=== Jukebox 45RPM Rotation Renderer ===")
    print(f"Image: {image_path}")
    if loop_forever:
        print("Mode: Looping forever (close window to stop)")
    else:
        print(f"Duration: {duration} seconds")
    print("Press ESC or close window to quit")
    print("=" * 40 + "\n")

    # Main loop
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Auto-start after 2 seconds
        if not auto_started:
            elapsed_time += dt
            if elapsed_time >= auto_start_delay:
                auto_started = True
                play_time = 0
                tonearm.play_record()
                print("Starting playback...")

        # Update tonearm
        tonearm.update(dt)

        # Update record rotation - start as soon as tonearm starts moving
        if tonearm.get_state() in [ToneArmState.SWINGING_OUT, ToneArmState.LOWERING, ToneArmState.PLAYING]:
            # Rotate record at 45 RPM (270 degrees/second)
            record_rotation += 270 * dt
        elif tonearm.is_parked():
            # Stop rotation when parked
            record_rotation = 0
        else:
            # Slow down record rotation when returning
            if record_rotation > 0:
                record_rotation += 10 * dt
                record_rotation *= 0.95

        # Update tonearm tracking during playback
        if tonearm.is_playing():
            # Track play time and move tonearm across record
            play_time += dt

            # Calculate tonearm position based on elapsed time
            # Interpolate from play_angle to end_angle over track_duration
            progress = min(play_time / track_duration, 1.0)  # 0.0 to 1.0
            current_target = tonearm.play_angle + (tonearm.end_angle - tonearm.play_angle) * progress
            tonearm.target_angle = current_target

            # Check if we've reached the end
            if play_time >= track_duration and not waiting_at_end:
                waiting_at_end = True
                end_wait_time = 0
                print("Reached end of track...")

        # Handle waiting at end before auto-stopping or looping
        if waiting_at_end:
            end_wait_time += dt
            if end_wait_time >= end_wait_delay:
                if loop_forever:
                    # Loop: return to park and restart
                    print("Looping - restarting playback...")
                    play_time = 0
                    waiting_at_end = False
                    end_wait_time = 0
                    tonearm.return_to_park()
                    auto_started = False
                    elapsed_time = 0
                else:
                    # Stop and return to park
                    print("Stopping playback...")
                    tonearm.return_to_park()
                    play_time = 0
                    waiting_at_end = False
                    end_wait_time = 0

        # ====== DRAWING ======

        # Background
        screen.fill(bg_color)

        # Draw decorative panel
        panel = pygame.Rect(100, 150, 600, 500)
        pygame.draw.rect(screen, panel_color, panel, border_radius=10)
        pygame.draw.rect(screen, (60, 55, 65), panel, 2, border_radius=10)

        # Corner accents
        corner_color = (80, 75, 85)
        corners = [(110, 160), (680, 160), (110, 640), (680, 640)]
        for cx, cy in corners:
            pygame.draw.line(screen, corner_color, (cx - 10, cy), (cx + 10, cy), 2)
            pygame.draw.line(screen, corner_color, (cx, cy - 10), (cx, cy + 10), 2)

        # Draw dark brown background circle behind the record
        background_radius = 155
        pygame.draw.circle(screen, brown_background, (record_x, record_y), background_radius)

        # Rotate and draw the record image
        rotated_image = pygame.transform.rotate(record_original, -record_rotation)
        rotated_rect = rotated_image.get_rect(center=(record_x, record_y))
        screen.blit(rotated_image, rotated_rect)

        # Draw tonearm
        tonearm.draw(screen)

        # Update display
        pygame.display.flip()

    pygame.quit()
    print("Playback ended.\n")


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Example: Display with default 30-second duration
    display_record_with_tonearm('final_record_pressing.png')

    # Other examples:
    # display_record_with_tonearm('final_record_pressing.png', duration=45)
    # display_record_with_tonearm('final_record_pressing.png', duration=None)
