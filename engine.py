import sys
import os

WIDTH = 100
HEIGHT = 100

# ANSI color codes
class Color:
    RESET  = "\033[0m"
    BLACK  = "\033[30m"
    RED    = "\033[31m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    BLUE   = "\033[34m"
    MAGENTA= "\033[35m"
    CYAN   = "\033[36m"
    WHITE  = "\033[37m"
    BOLD   = "\033[1m"

# Cursor/screen ANSI helpers
_CURSOR_HOME  = "\033[H"
_CURSOR_HIDE  = "\033[?25l"
_CURSOR_SHOW  = "\033[?25h"
_CLEAR_SCREEN = "\033[2J"


class Screen:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT, bg: str = " "):
        self.width  = width
        self.height = height
        self.bg     = bg
        self._buf: list[list[str]] = [[bg] * width for _ in range(height)]
        # color layer: None means no color applied to that cell
        self._colors: list[list[str | None]] = [[None] * width for _ in range(height)]
        self._first_render = True

    # ── buffer ops ──────────────────────────────────────────────────────────

    def clear(self) -> None:
        """Reset every cell to the background character."""
        for row in self._buf:
            for x in range(self.width):
                row[x] = self.bg
        for row in self._colors:
            for x in range(self.width):
                row[x] = None

    def put(self, x: int, y: int, char: str, color: str | None = None) -> None:
        """Write a single character at (x, y). Out-of-bounds writes are silently ignored."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self._buf[y][x] = char[0]
            self._colors[y][x] = color

    def draw_text(self, x: int, y: int, text: str, color: str | None = None) -> None:
        """Write a string starting at (x, y), clipping at screen edge."""
        for i, ch in enumerate(text):
            self.put(x + i, y, ch, color)

    def draw_box(self, x: int, y: int, w: int, h: int,
                 color: str | None = None,
                 fill: str | None = None) -> None:
        """Draw a single-line box. Optionally fill interior with `fill` char."""
        if w < 2 or h < 2:
            return
        # corners
        self.put(x,         y,         "┌", color)
        self.put(x + w - 1, y,         "┐", color)
        self.put(x,         y + h - 1, "└", color)
        self.put(x + w - 1, y + h - 1, "┘", color)
        # horizontal edges
        for cx in range(x + 1, x + w - 1):
            self.put(cx, y,         "─", color)
            self.put(cx, y + h - 1, "─", color)
        # vertical edges
        for cy in range(y + 1, y + h - 1):
            self.put(x,         cy, "│", color)
            self.put(x + w - 1, cy, "│", color)
        # optional fill
        if fill is not None:
            for cy in range(y + 1, y + h - 1):
                for cx in range(x + 1, x + w - 1):
                    self.put(cx, cy, fill)

    def draw_sprite(self, x: int, y: int, sprite: list[str],
                    color: str | None = None,
                    transparent: str = " ") -> None:
        """
        Draw a multi-line ASCII sprite. Lines in `sprite` are rows top-to-bottom.
        Characters equal to `transparent` are skipped (not drawn).
        """
        for dy, line in enumerate(sprite):
            for dx, ch in enumerate(line):
                if ch != transparent:
                    self.put(x + dx, y + dy, ch, color)

    # ── rendering ───────────────────────────────────────────────────────────

    def render(self) -> None:
        """Flush the framebuffer to stdout in a single write."""
        out_parts: list[str] = []

        if self._first_render:
            out_parts.append(_CLEAR_SCREEN)
            out_parts.append(_CURSOR_HIDE)
            self._first_render = False

        out_parts.append(_CURSOR_HOME)

        for row_chars, row_colors in zip(self._buf, self._colors):
            prev_color: str | None = None
            for ch, col in zip(row_chars, row_colors):
                if col != prev_color:
                    if prev_color is not None:
                        out_parts.append(Color.RESET)
                    if col is not None:
                        out_parts.append(col)
                    prev_color = col
                out_parts.append(ch)
            if prev_color is not None:
                out_parts.append(Color.RESET)
            out_parts.append("\n")

        sys.stdout.write("".join(out_parts))
        sys.stdout.flush()

    def close(self) -> None:
        """Restore terminal cursor visibility."""
        sys.stdout.write(_CURSOR_SHOW)
        sys.stdout.flush()


# ── convenience: pre-built screen layouts ───────────────────────────────────

def make_battle_screen(screen: Screen,
                       player_name: str, player_hp: int, player_max_hp: int,
                       enemy_name: str,  enemy_hp: int,  enemy_max_hp: int,
                       message: str = "") -> None:
    """
    Draws a classic Pokemon-style battle layout onto `screen`.

    Layout (100 x 100):
      - top 60 rows : battle field
      - rows 60-75  : enemy HUD  (top-right)
      - rows 60-75  : player HUD (bottom-left)
      - rows 76-99  : message / action box
    """
    screen.clear()

    # outer border
    screen.draw_box(0, 0, screen.width, screen.height, Color.WHITE)

    # battle field divider
    for x in range(1, screen.width - 1):
        screen.put(x, 60, "─", Color.WHITE)

    # enemy HUD box (top-right of HUD area)
    screen.draw_box(50, 61, 48, 8, Color.CYAN)
    screen.draw_text(52, 62, f"{enemy_name:<20}", Color.BOLD)
    screen.draw_text(52, 63, f"HP: {enemy_hp}/{enemy_max_hp}", Color.GREEN)
    _draw_hp_bar(screen, 52, 64, 40, enemy_hp, enemy_max_hp)

    # player HUD box (bottom-left of HUD area)
    screen.draw_box(2, 61, 48, 8, Color.CYAN)
    screen.draw_text(4, 62, f"{player_name:<20}", Color.BOLD)
    screen.draw_text(4, 63, f"HP: {player_hp}/{player_max_hp}", Color.GREEN)
    _draw_hp_bar(screen, 4, 64, 40, player_hp, player_max_hp)

    # message box
    screen.draw_box(1, 70, screen.width - 2, 28, Color.WHITE)
    if message:
        screen.draw_text(3, 72, message[:screen.width - 6], Color.WHITE)


def _draw_hp_bar(screen: Screen, x: int, y: int, length: int,
                 current: int, maximum: int) -> None:
    ratio = max(0, current) / max(1, maximum)
    filled = round(ratio * length)
    color = Color.GREEN if ratio > 0.5 else (Color.YELLOW if ratio > 0.25 else Color.RED)
    screen.draw_text(x, y, "█" * filled + "░" * (length - filled), color)