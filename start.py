
import tkinter as tk
import random
from pathlib import Path
import pyautogui
import math
import time


# ---------------- CONFIGURATION ----------------

BASE_PATH = Path(r"D:\PROJECTS\Pet")

PET_SIZE = 100
MOVE_SPEED = 6

IDLE_AFTER = 5       # Seconds before idle mode
SLEEP_AFTER_IDLE = 5 # Seconds before sleeping

IDLE_EVENTS = [1, 2, 3, 4]
WALK_LEFT_EVENTS = [6, 7]
WALK_RIGHT_EVENTS = [8, 9]
SLEEP_EVENTS = [10, 11, 12, 13, 15]

x = 300
y = 300
cycle = 0
check = 0
event_number = random.randint(1, 15)

# Cursor tracking
last_mouse_position = tuple(pyautogui.position())
last_mouse_move_time = time.monotonic()

# Buddy behaviour
pet_state = "follow"
state_started = time.monotonic()

# ---------------- CREATE WINDOW FIRST ----------------

window = tk.Tk()
window.withdraw()

# ---------------- LOAD GIF FRAMES ----------------

def load_gif(filename, frame_count):

    path = BASE_PATH / filename

    if not path.exists():
        raise FileNotFoundError(f"GIF not found: {path}")

    frames = []

    for i in range(frame_count):
        frame = tk.PhotoImage(
            file=str(path),
            format=f"gif -index {i}",
            master=window
        )
        frames.append(frame)

    print(f"Loaded {filename}: {len(frames)} frames")

    return frames


idle = load_gif("idle.gif", 5)
idle_to_sleep = load_gif("idle_sleep.gif", 8)
sleep = load_gif("sleep.gif", 3)
sleep_to_idle = load_gif("sleep_idle.gif", 8)

# Correct walking directions
walk_left = load_gif("left.gif", 8)
walk_right = load_gif("right.gif", 8)

# ---------------- GIF FRAME CONTROL ----------------

def gif_work(cycle, frames, event_number, first_num, last_num):

    if cycle < len(frames) - 1:
        cycle += 1

    else:
        cycle = 0
        event_number = random.randint(first_num, last_num)

    return cycle, event_number


# ---------------- EVENT CONTROL ----------------

def event(cycle, check, event_number, x):

    if event_number in IDLE_EVENTS:
        check = 0
        delay = 100

    elif event_number == 5:
        check = 1
        delay = 100

    elif event_number in WALK_LEFT_EVENTS:
        check = 4
        delay = 100

    elif event_number in WALK_RIGHT_EVENTS:
        check = 5
        delay = 100

    elif event_number in SLEEP_EVENTS:
        check = 2
        delay = 500

    elif event_number == 14:
        check = 3
        delay = 100

    else:
        check = 0
        delay = 100

    window.after(
        delay,
        update,
        cycle,
        check,
        event_number,
        x
    )


# ---------------- MAIN ANIMATION ----------------



def update(cycle, check, event_number, x):

    global y
    global last_mouse_position
    global last_mouse_move_time
    global pet_state
    global state_started

    now = time.monotonic()

    # Get cursor position
    mouse_x, mouse_y = pyautogui.position()
    current_mouse_position = (mouse_x, mouse_y)

    # Detect cursor movement
    if current_mouse_position != last_mouse_position:

        last_mouse_position = current_mouse_position
        last_mouse_move_time = now

        # Wake Buddy if sleeping or transitioning
        if pet_state in ("sleep", "sleep_transition"):
            pet_state = "wake"
            cycle = 0

        elif pet_state == "idle":
            pet_state = "follow"
            cycle = 0

    # Check how long cursor has been stationary
    idle_time = now - last_mouse_move_time

    # Start idle mode
    if pet_state == "follow" and idle_time >= IDLE_AFTER:
        pet_state = "idle"
        cycle = 0
        state_started = now

    # Start sleeping after idle
    if pet_state == "idle":
        if now - state_started >= SLEEP_AFTER_IDLE:
            pet_state = "sleep_transition"
            cycle = 0

    # ---------------- FOLLOW MODE ----------------

    if pet_state == "follow":

        target_x = mouse_x - PET_SIZE // 2
        target_y = mouse_y - PET_SIZE // 2

        dx = target_x - x
        dy = target_y - y

        distance = math.sqrt(dx**2 + dy**2)

        if distance > 20:

            # Choose walking direction
            if dx < 0:
                frames = walk_left
            else:
                frames = walk_right

            # Move towards cursor
            x += round(MOVE_SPEED * dx / distance)
            y += round(MOVE_SPEED * dy / distance)

        else:
            frames = idle

        frame = frames[cycle % len(frames)]
        cycle = (cycle + 1) % len(frames)

    # ---------------- IDLE MODE ----------------

    elif pet_state == "idle":

        frame = idle[cycle % len(idle)]
        cycle = (cycle + 1) % len(idle)

    # ---------------- IDLE TO SLEEP ----------------

    elif pet_state == "sleep_transition":

        frame = idle_to_sleep[cycle]

        if cycle < len(idle_to_sleep) - 1:
            cycle += 1
        else:
            pet_state = "sleep"
            cycle = 0

    # ---------------- SLEEP MODE ----------------

    elif pet_state == "sleep":

        frame = sleep[cycle % len(sleep)]
        cycle = (cycle + 1) % len(sleep)

    # ---------------- WAKE UP MODE ----------------

    elif pet_state == "wake":

        frame = sleep_to_idle[cycle]

        if cycle < len(sleep_to_idle) - 1:
            cycle += 1
        else:
            pet_state = "follow"
            cycle = 0

    # ---------------- SCREEN BOUNDARIES ----------------

    max_x = window.winfo_screenwidth() - PET_SIZE
    max_y = window.winfo_screenheight() - PET_SIZE

    x = max(0, min(x, max_x))
    y = max(0, min(y, max_y))

    # ---------------- DISPLAY BUDDY ----------------

    window.geometry(
        f"{PET_SIZE}x{PET_SIZE}+{x}+{y}"
    )

    label.configure(image=frame)

    # Schedule next animation frame
    window.after(
        100,
        update,
        cycle,
        check,
        event_number,
        x
    )



# ---------------- WINDOW CONFIGURATION ----------------

window.overrideredirect(True)
window.wm_attributes("-topmost", True)
window.wm_attributes("-transparentcolor", "black")

window.config(
    bg="black",
    highlightbackground="black"
)

label = tk.Label(
    window,
    bd=2,
    bg="black"
)


label.pack()

# SHOW WINDOW
window.deiconify()
window.update_idletasks()


# ---------------- START ----------------

print("Buddy is starting...")

window.after(
    100,
    update,
    cycle,
    check,
    event_number,
    x
)

window.mainloop()
