import random
import os
import pygame
import keyboard
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import pystray
from PIL import Image, ImageTk, ImageDraw
import threading
import sys

# Initialize pygame mixer
pygame.mixer.init()

# Define the resource directory
if hasattr(sys, '_MEIPASS'):
    resource_path = os.path.join(sys._MEIPASS)
else:
    resource_path = os.path.dirname(__file__)

# Define the sounds directory
sounds_dir = os.path.join(resource_path, "sounds")

# Define a mapping for special keys
special_keys = {
    'backspace': 'backspace.mp3',
    'space': 'space.mp3'
}

# Path to the general sound file for all basic keys
general_sound = os.path.join(sounds_dir, 'A.mp3')

# Define a set to keep track of keys currently being held down
keys_held_down = set()

# Define a variable for volume control
volume = 1.0

# Define a function to play sound
def play_sound(sound_path):
    if os.path.exists(sound_path):
        sound = pygame.mixer.Sound(sound_path)
        sound.set_volume(volume)
        sound.play()
        print(f"Playing sound: {sound_path} at volume: {volume}")  # Debug info
    else:
        print(f"Sound file not found at {sound_path}.")

# Define a callback function for keyboard events
def on_key_event(event):
    key = event.name
    if event.event_type == 'down' and key not in keys_held_down:
        keys_held_down.add(key)
        if key in special_keys:
            play_sound(os.path.join(sounds_dir, special_keys[key]))
        else:
            play_sound(general_sound)
    elif event.event_type == 'up' and key in keys_held_down:
        keys_held_down.remove(key)

# Hook the callback function to keyboard events
keyboard.hook(on_key_event)

# Function to update volume
def update_volume(val):
    global volume, canvas, volume_value_label
    volume = float(val) / 100
    canvas.itemconfig(volume_value_label, text=f"{int(float(val))}")

# Custom button creation function
def create_rounded_button(canvas, x, y, width, height, radius, text, command=None):
    # Draw the rounded rectangle
    points = [
        (x + radius, y),
        (x + width - radius, y),
        (x + width - radius, y + radius),
        (x + width, y + radius),
        (x + width, y + height - radius),
        (x + width - radius, y + height - radius),
        (x + width - radius, y + height),
        (x + radius, y + height),
        (x + radius, y + height - radius),
        (x, y + height - radius),
        (x, y + radius),
        (x + radius, y + radius)
    ]
    
    button_bg = canvas.create_polygon(points, smooth=True, fill="red", outline="red")
    
    # Add text on top of the rounded rectangle
    button_text = canvas.create_text(x + width / 2, y + height / 2, text=text, fill="black", font=("Helvetica", 14), activefill="darkgrey")

    # Bind the click event to the command
    if command:
        def on_button_click(event):
            if x < event.x < x + width and y < event.y < y + height:
                command()
        
        canvas.tag_bind(button_bg, "<Button-1>", on_button_click)
        canvas.tag_bind(button_text, "<Button-1>", on_button_click)

# Set up the GUI
def setup_gui():
    global root, canvas, volume_value_label, gradient_image
    root = ThemedTk(theme='breeze')
    root.title("Keyboard Sound Player")
    
    icon_path = os.path.join(resource_path, 'ico.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)  # Set the window icon
    else:
        print(f"Icon file not found at {icon_path}")
    
    root.geometry("400x200")

    # Set up the background gradient
    canvas = tk.Canvas(root, width=400, height=200, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Create a diagonal gradient background
    def create_gradient(width, height, color1, color2):
        base = Image.new('RGB', (width, height), color1)
        top = Image.new('RGB', (width, height), color2)
        mask = Image.new('L', (width, height))
        mask_data = []
        for y in range(height):
            for x in range(width):
                mask_data.append(int(255 * (x / width * 0.5 + y / height * 0.5)))
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return ImageTk.PhotoImage(base)

    gradient_image = create_gradient(400, 200, '#B330E1', '#5C73B9')
    canvas.create_image(0, 0, anchor=tk.NW, image=gradient_image)
    canvas.image = gradient_image  # Keep a reference to avoid garbage collection

    # Custom style for the slider to remove the background
    style = ttk.Style(root)
    style.configure("TScale",
                    troughcolor='#B330E1',  # Match the start color of the gradient
                    background='#B330E1',
                    sliderlength=30,
                    sliderthickness=10)

    # Volume slider
    volume_slider = ttk.Scale(root, style="TScale", from_=0, to=100, orient='horizontal', command=update_volume)
    volume_slider.set(100)  # Set initial volume to 100%
    canvas.create_window(200, 100, anchor=tk.CENTER, window=volume_slider)

    # Labels using canvas.create_text for transparency
    canvas.create_text(200, 60, text="Volume", font=("Helvetica", 14), fill="white")
    volume_value_label = canvas.create_text(200, 120, text="100", font=("Helvetica", 14), fill="white")

    canvas.create_text(100, 100, text="0", font=("Helvetica", 12), fill="white")
    canvas.create_text(300, 100, text="100", font=("Helvetica", 12), fill="white")

    # Custom close button with rounded corners
    create_rounded_button(canvas, 150, 130, 100, 40, 20, "Quit", command=on_quit_direct)

    root.protocol("WM_DELETE_WINDOW", hide_window)
    root.withdraw()

def hide_window():
    root.withdraw()

def show_window(icon, item):
    root.deiconify()

def on_quit(icon, item):
    icon.stop()
    root.quit()

def on_quit_direct():
    icon.stop()
    root.quit()

# Function to create the tray icon
def create_image():
    icon_path = os.path.join(resource_path, 'ico.ico')
    if os.path.exists(icon_path):
        return Image.open(icon_path)  # Load the provided image for the tray icon
    else:
        print(f"Icon file not found at {icon_path}")
        return Image.new('RGB', (16, 16), 'black')  # Fallback to a blank icon

icon_image = create_image()
menu = (pystray.MenuItem('Open', show_window), pystray.MenuItem('Quit', on_quit))
icon = pystray.Icon("keyboard_sounds", icon_image, "Keyboard Sound Player", menu)

# Function to run the tray icon
def run_tray():
    icon.run()

# Run the GUI setup
setup_gui()

# Run the tray icon in a separate thread
tray_thread = threading.Thread(target=run_tray)
tray_thread.daemon = True
tray_thread.start()

# Start the keyboard hook in the main thread
print("Keyboard sound script is running. Adjust settings from the tray icon.")
root.mainloop()
