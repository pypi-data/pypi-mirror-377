# Changelog

This file summarizes the changes since the last commit to the `main` branch.

## Native C++ changes to pix

- **`src/context.hpp`**:
    - Added `log_to` to log draw commands.
    - Added `round_line` for drawing lines with variable width.
    - Added `flood_fill`.
    - Added `backface_culling` flag.
- **`src/full_console.hpp`**:
    - Added `set_readline_callback` to allow custom handling of line input.
    - Added `autoscroll` and `wrap_lines` properties.
    - Added `scroll_pos` to support horizontal scrolling.
- **`src/glfw_system.cpp`**:
    - Added clipboard support (`get_clipboard`, `set_clipboard`).
    - Added scroll events.
    - Added `set_visible` to hide/show window.
- **`src/screen.hpp`**:
    - The `Screen` class is now a proper class with a static instance.
    - Added `crop` and `split` methods.
- **`src/system.hpp`**:
    - Added `quit_loop` to allow programmatic exit from the main loop.
    - Added `get_clipboard` and `set_clipboard`.
    - Added `ScrollEvent`.
- **`src/treesitter.hpp`**, **`src/treesitter.cpp`**:
    - New files to integrate the Tree-sitter parsing library.
- **`src/vec2.hpp`**:
    - Added tweening and animation support for `Float2` (`tween_to`, `tween_from`, `tween_velocity`).

## Changes to the python interface

- **`src/python.cpp`**:
    - Added `treesitter` module.
    - Added `add_event_listener` and `remove_event_listener`.
    - Added `quit_loop`.
    - Added `get_clipboard` and `set_clipboard`.
    - The main loop (`run_loop`) now handles events in a more robust way.
- **`src/python/class_canvas.hpp`**:
    - Exposed `log_to`, `rounded_line`, `flood_fill`, `backface_culling`.
- **`src/python/class_console.hpp`**:
    - Exposed `set_readline_callback`, `autoscroll`, `wrap_lines`.
- **`src/python/class_font.hpp`**:
    - Added `text_size` method to `Font` class.
- **`src/python/class_image.hpp`**:
    - Added `update` method to update image from raw bytes.
- **`src/python/class_screen.hpp`**:
    - Exposed `crop` and `split` methods.
    - Added `swap_async` for asynchronous screen updates.
- **`src/python/class_vec2.hpp`**:
    - Exposed tweening functions (`tween_to`, `tween_from`, `tween_velocity`).
- **`src/python/mod_event.hpp`**:
    - Added `ScrollEvent`.
- **`src/python/mod_treesitter.hpp`**:
    - New file to expose Tree-sitter functionality to Python.
