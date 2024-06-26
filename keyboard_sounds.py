import os
import sys
import threading
import time

start_time = time.time()  # Start timing for profiling

# Global variables
resource_path = ""
sounds_dir = ""
keys_held_down = set()
volume = 1.0
mixer_initialized = False
special_keys = {
    'backspace': 'backspace.mp3',
    'space': 'space.mp3'
}
general_sound = ""

# Function to initialize pygame mixer
def init_pygame_mixer():
    global mixer_initialized
    import pygame
    try:
        pygame.mixer.init()
        mixer_initialized = True
    except pygame.error as e:
        print(f"Error initializing mixer: {e}")
        mixer_initialized = False

# Function to initialize keyboard hook
def init_keyboard_hook():
    import keyboard
    def on_key_event(event):
        key = event.name
        if mixer_initialized:
            if event.event_type == 'down' and key not in keys_held_down:
                keys_held_down.add(key)
                if key in special_keys:
                    play_sound(os.path.join(sounds_dir, special_keys[key]))
                else:
                    play_sound(general_sound)
            elif event.event_type == 'up' and key in keys_held_down:
                keys_held_down.remove(key)
    keyboard.hook(on_key_event)

# Function to initialize the GUI
def setup_gui():
    global root, canvas, volume_value_label, gradient_image
    from ttkthemes import ThemedTk
    import tkinter as tk
    from tkinter import ttk
    root = ThemedTk(theme='breeze')
    root.title("Keyboard Sound Player")

    icon_path = os.path.join(resource_path, 'ico.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)  
    else:
        print(f"Icon file not found at {icon_path}")
    
    root.geometry("400x200")

    canvas = tk.Canvas(root, width=400, height=200, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def create_gradient(width, height, color1, color2):
        from PIL import Image, ImageTk
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
    canvas.image = gradient_image  

    style = ttk.Style(root)
    style.configure("TScale",
                    troughcolor='#B330E1',  
                    background='#B330E1',
                    sliderlength=30,
                    sliderthickness=10)

    volume_slider = ttk.Scale(root, style="TScale", from_=0, to=100, orient='horizontal', command=update_volume)
    volume_slider.set(100)  
    canvas.create_window(200, 100, anchor=tk.CENTER, window=volume_slider)

    canvas.create_text(200, 60, text="Volume", font=("Helvetica", 14), fill="white")
    volume_value_label = canvas.create_text(200, 120, text="100", font=("Helvetica", 14), fill="white")

    canvas.create_text(100, 100, text="0", font=("Helvetica", 12), fill="white")
    canvas.create_text(300, 100, text="100", font=("Helvetica", 12), fill="white")

    style.configure("Red.TButton", background="red", foreground="black", font=("Helvetica", 14))

    close_button = ttk.Button(root, text="Quit", command=on_quit_direct, style="Red.TButton")
    canvas.create_window(200, 150, anchor=tk.CENTER, window=close_button)

    root.protocol("WM_DELETE_WINDOW", hide_window)

# Function to update volume
def update_volume(val):
    global volume
    volume = float(val) / 100
    canvas.itemconfig(volume_value_label, text=f"{int(float(val))}")

# Function to play sound
def play_sound(sound_path):
    if mixer_initialized and os.path.exists(sound_path):
        import pygame
        sound = pygame.mixer.Sound(sound_path)
        sound.set_volume(volume)
        sound.play()
        print(f"Playing sound: {sound_path} at volume: {volume}")  
    else:
        print(f"Sound file not found or mixer not initialized at {sound_path}.")

# Function to hide the GUI window
def hide_window():
    root.withdraw()

# Function to show the GUI window
def show_window(icon, item):
    root.deiconify()

# Function to quit the program
def quit_program():
    import pygame
    import keyboard
    icon.visible = False
    icon.stop()
    root.quit()
    root.destroy()
    pygame.quit()
    keyboard.unhook_all()
    os._exit(0)

# Function to quit from tray icon
def on_quit(icon, item):
    quit_program()

# Function to quit directly from the GUI
def on_quit_direct():
    quit_program()

# Function to create the tray icon image
def create_image():
    icon_path = os.path.join(resource_path, 'ico.ico')
    if os.path.exists(icon_path):
        from PIL import Image
        return Image.open(icon_path)  
    else:
        print(f"Icon file not found at {icon_path}")
        from PIL import Image
        return Image.new('RGB', (16, 16), 'black')  

# Set up paths and global variables
if hasattr(sys, '_MEIPASS'):
    resource_path = os.path.join(sys._MEIPASS)
else:
    resource_path = os.path.dirname(__file__)

sounds_dir = os.path.join(resource_path, "sounds")
general_sound = os.path.join(sounds_dir, 'A.mp3')

# Initialize pygame mixer and keyboard hook in parallel
init_thread = threading.Thread(target=init_pygame_mixer)
init_thread.start()

# Setup pystray icon
import pystray
icon_image = create_image()
menu = (pystray.MenuItem('Open', show_window), pystray.MenuItem('Quit', on_quit))
icon = pystray.Icon("keyboard_sounds", icon_image, "Keyboard Sound Player", menu)

# Start the tray icon in a separate thread
tray_thread = threading.Thread(target=icon.run)
tray_thread.daemon = True
tray_thread.start()

# Wait for pygame mixer initialization to complete
init_thread.join()

# Setup keyboard hook after pygame mixer initialization
init_keyboard_hook()

# Initialize the GUI after starting the tray icon
setup_gui()
root.withdraw()

print(f"Initialization completed in {time.time() - start_time:.2f} seconds.")
print("Keyboard sound script is running. Adjust settings from the tray icon.")
root.mainloop()