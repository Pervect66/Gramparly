import tkinter as tk
from tkinter import messagebox
import openai
import os
import pyperclip
import difflib
import threading
import pystray
from PIL import Image, ImageDraw

# Load the OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

def paste_text(event=None):
    input_text.insert(tk.INSERT, root.clipboard_get())

def new_text():
    input_text.delete("1.0", tk.END)
    input_text.focus_set()
    clear_output_box()

def clear_output_box(event=None):
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.config(state=tk.DISABLED)

def copy_text():
    pyperclip.copy(result_text.get("1.0", tk.END).strip())
    input_text.delete("1.0", tk.END)
    input_text.focus_set()

def move_text_to_input():
    result_content = result_text.get("1.0", tk.END)
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, result_content)
    input_text.focus_set()

def highlight_changes(original, checked):
    sequence = difflib.SequenceMatcher(None, original, checked)
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    
    for tag, i1, i2, j1, j2 in sequence.get_opcodes():
        if tag == 'equal':
            result_text.insert(tk.END, original[i1:i2])
        elif tag == 'replace' or tag == 'insert':
            result_text.insert(tk.END, checked[j1:j2], 'highlight')
        elif tag == 'delete':
            result_text.insert(tk.END, original[i1:i2])
    
    result_text.config(state=tk.DISABLED)

def check_text():
    user_input = input_text.get("1.0", tk.END)
    if not user_input.strip():
        messagebox.showwarning("Input Error", "Please enter some text.")
        return
    
    # Call the OpenAI API for grammar and spellcheck
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a grammar and spell checker. Correct the grammar and spelling of the following text without interpreting it as a question or prompt. Retain the original language."},
                {"role": "user", "content": user_input}
            ]
        )
        checked_text = response['choices'][0]['message']['content']
        
        # Highlight changes in the result box
        highlight_changes(user_input, checked_text)
        
    except Exception as e:
        messagebox.showerror("API Error", str(e))

def simplify_text():
    user_input = input_text.get("1.0", tk.END)
    if not user_input.strip():
        messagebox.showwarning("Input Error", "Please enter some text.")
        return
    
    # Call the OpenAI API to simplify text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a text simplifier. Simplify the following text and make it more informal without interpreting it as a question or prompt. Retain the original language."},
                {"role": "user", "content": user_input}
            ]
        )
        simplified_text = response['choices'][0]['message']['content']
        
        # Show the simplified text in the result box
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, simplified_text)
        result_text.config(state=tk.DISABLED)
        
    except Exception as e:
        messagebox.showerror("API Error", str(e))

def rewrite_text():
    user_input = input_text.get("1.0", tk.END)
    if not user_input.strip():
        messagebox.showwarning("Input Error", "Please enter some text.")
        return
    
    # Call the OpenAI API to rewrite text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a text rewriter. Rewrite the following text to make it better structured and compelling without interpreting it as a question or prompt. Do not translate the text; retain the original language."},
                {"role": "user", "content": user_input}
            ]
        )
        rewritten_text = response['choices'][0]['message']['content']
        
        # Show the rewritten text in the result box
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, rewritten_text)
        result_text.config(state=tk.DISABLED)
        
    except Exception as e:
        messagebox.showerror("API Error", str(e))

def on_closing():
    root.withdraw()  # Hide the window instead of destroying it
    icon.notify("Gramparly is still running in the system tray.")

def quit_app(icon, item=None):
    icon.stop()
    root.quit()

# Set up the GUI
root = tk.Tk()
root.title("Gramparly")

font_family = "Calibri"
font_size = 12

input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

input_label = tk.Label(input_frame, text="Enter text to check:")
input_label.pack(anchor="w")

input_text = tk.Text(input_frame, wrap=tk.WORD, height=10, font=(font_family, font_size))
input_text.pack(expand=True, fill=tk.BOTH)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

check_button = tk.Button(button_frame, text="Spell/grammar check", command=check_text)
check_button.pack(side=tk.LEFT, padx=5)

simplify_button = tk.Button(button_frame, text="Simplify Text", command=simplify_text)
simplify_button.pack(side=tk.LEFT, padx=5)

rewrite_button = tk.Button(button_frame, text="Rewrite Text", command=rewrite_text)
rewrite_button.pack(side=tk.LEFT, padx=5)

quit_button = tk.Button(button_frame, text="Quit", command=lambda: quit_app(icon))
quit_button.pack(side=tk.RIGHT, padx=5)

# Right-click menu for paste function
def show_context_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Paste", command=paste_text)

input_text.bind("<Button-3>", show_context_menu)
input_text.bind("<Button-1>", clear_output_box)  # Clear output box on left-click in input box

# Result frame for showing the checked text
result_frame = tk.Frame(root)
result_frame.pack(pady=10, fill=tk.BOTH, expand=True)

result_text = tk.Text(result_frame, wrap=tk.WORD, height=10, font=(font_family, font_size))
result_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
result_text.tag_config('highlight', background='yellow')
result_text.config(state=tk.DISABLED)

button_frame_2 = tk.Frame(result_frame)
button_frame_2.pack(pady=10)

new_button = tk.Button(button_frame_2, text="New Text", command=new_text)
new_button.pack(side=tk.LEFT, padx=5)

copy_button = tk.Button(button_frame_2, text="Copy Text", command=copy_text)
copy_button.pack(side=tk.LEFT, padx=5)

move_text_button = tk.Button(button_frame_2, text="⬆Move text to input box⬆", command=move_text_to_input)
move_text_button.pack(side=tk.LEFT, padx=5)

# Ensure the cursor is in the input box when the script starts
input_text.focus_set()

# Function to send clipboard content to Gramparly input box
def send_to_gramparly(icon, item):
    clipboard_content = pyperclip.paste()
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, clipboard_content)
    root.deiconify()
    input_text.focus_set()

# Function to create an image for the system tray icon
def create_image():
    width = 64
    height = 64
    color1 = "white"
    color2 = "black"

    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        [width // 2, 0, width, height // 2],
        fill=color2)
    dc.rectangle(
        [0, height // 2, width // 2, height],
        fill=color2)

    return image

# Function to setup and run the system tray icon with the context menu
def setup_tray():
    global icon
    icon_image = create_image()
    menu = pystray.Menu(
        pystray.MenuItem("Send to Gramparly", send_to_gramparly),
        pystray.MenuItem("Quit", quit_app)
    )
    icon = pystray.Icon("Gramparly", icon_image, "Gramparly", menu)
    icon.run()

# Run the tray icon in a separate thread
tray_thread = threading.Thread(target=setup_tray)
tray_thread.daemon = True
tray_thread.start()

# Override the window close event to minimize to tray
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
