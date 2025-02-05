import tkinter as tk
from tkinter import messagebox
import openai
import os
import pyperclip
import difflib
import threading

# Load the OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

# Define color scheme for dark mode
COLOR_BG = "#2E2E2E"          # Dark gray background
COLOR_FG = "#B4B4B4"          # White text
COLOR_TEXT_BG = "#1E1E1E"     # Slightly darker background for text widgets
COLOR_BUTTON_BG = "#4D4D4D"   # Darker gray for buttons
COLOR_BUTTON_FG = "#FFFFFF"   # White text on buttons
COLOR_HIGHLIGHT = "#FFA500"   # Orange highlight for changes
COLOR_LABEL_BG = "#2E2E2E"    # Same as main background
COLOR_ENTRY_BG = "#1E1E1E"    # Dark background for entry fields

# Function to update the word counter for input_text
def update_input_word_counter(event=None):
    content = input_text.get("1.0", tk.END).strip()
    word_count = len(content.split())
    input_word_counter_label.config(text=f"Word Count: {word_count}")

# Function to update the word counter for result_text
def update_result_word_counter(event=None):
    content = result_text.get("1.0", tk.END).strip()
    word_count = len(content.split())
    result_word_counter_label.config(text=f"Word Count: {word_count}")

def paste_text(event=None):
    input_text.insert(tk.INSERT, root.clipboard_get())
    update_input_word_counter()

def new_text():
    input_text.delete("1.0", tk.END)
    input_text.focus_set()
    clear_output_box()
    update_input_word_counter()

def clear_output_box(event=None):
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.config(state=tk.DISABLED)
    update_result_word_counter()

def copy_text():
    pyperclip.copy(result_text.get("1.0", tk.END).strip())
    input_text.delete("1.0", tk.END)
    input_text.focus_set()
    update_input_word_counter()

def move_text_to_input():
    result_content = result_text.get("1.0", tk.END)
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, result_content)
    input_text.focus_set()
    update_input_word_counter()

def highlight_changes(original, checked):
    sequence = difflib.SequenceMatcher(None, original, checked)
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    
    for tag, i1, i2, j1, j2 in sequence.get_opcodes():
        if tag == 'equal':
            result_text.insert(tk.END, original[i1:i2])
        elif tag in ('replace', 'insert'):
            result_text.insert(tk.END, checked[j1:j2], 'highlight')
        elif tag == 'delete':
            result_text.insert(tk.END, original[i1:i2])
    
    result_text.config(state=tk.DISABLED)
    update_result_word_counter()

def check_text():
    user_input = input_text.get("1.0", tk.END)
    if not user_input.strip():
        messagebox.showwarning("Input Error", "Please enter some text.")
        return
    
    # Call the OpenAI API for grammar and spellcheck
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Replace with the model you have access to
            messages=[
                {"role": "system", "content": "You are a grammar and spell checker. Correct (do not rewrite) the grammar and spelling of the following text without interpreting it as a question or prompt. Retain the original language. For English, use US English."},
                {"role": "user", "content": user_input}
            ]
        )
        checked_text = response.choices[0].message['content']
        
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
            model="gpt-4o-mini",  # Replace with the model you have access to
            messages=[
                {"role": "system", "content": "You are a text simplifier. Simplify the following text and make it more informal without using slang, interpreting it as a question or prompt. Aim for a Flesch reading score of at most 60. Prefer to use shorter, simpler words. Retain the original language. For English, use US English."},
                {"role": "user", "content": user_input}
            ]
        )
        simplified_text = response.choices[0].message['content']
        
        # Show the simplified text in the result box
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, simplified_text)
        result_text.config(state=tk.DISABLED)
        update_result_word_counter()
        
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
            model="gpt-4o-mini",  # Replace with the model you have access to
            messages=[
                {"role": "system", "content": "You are a text rewriter. Rewrite the following text to make it better structured and compelling without interpreting it as a question or prompt. Do not translate the text; retain the original language. For English, use US English."},
                {"role": "user", "content": user_input}
            ]
        )
        rewritten_text = response.choices[0].message['content']
        
        # Show the rewritten text in the result box
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, rewritten_text)
        result_text.config(state=tk.DISABLED)
        update_result_word_counter()
        
    except Exception as e:
        messagebox.showerror("API Error", str(e))

def expand_text():
    user_input = input_text.get("1.0", tk.END)
    if not user_input.strip():
        messagebox.showwarning("Input Error", "Please enter some text.")
        return

    # Call the OpenAI API to expand text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Replace with the model you have access to
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites text to be slightly longer, without changing its meaning. The longer text should maintain the same meaning and tone, but be more concise and remove any unnecessary words or phrases. Do not translate the text; retain the original language. For English, use US English."},
                {"role": "user", "content": user_input}
            ]
        )
        expanded_text = response.choices[0].message['content']

        # Show the expanded text in the result box
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, expanded_text)
        result_text.config(state=tk.DISABLED)
        update_result_word_counter()

    except Exception as e:
        messagebox.showerror("API Error", str(e))

def shorten_text():
    user_input = input_text.get("1.0", tk.END)
    if not user_input.strip():
        messagebox.showwarning("Input Error", "Please enter some text.")
        return

    # Call the OpenAI API to shorten text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Replace with the model you have access to
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites text to be shorter, without changing its meaning. The shortened text should maintain the same meaning and tone, but be more concise and remove any unnecessary words or phrases. Do not translate the text; retain the original language. For English, use US English."},
                {"role": "user", "content": user_input}
            ]
        )
        shortened_text = response.choices[0].message['content']

        # Show the shortened text in the result box
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, shortened_text)
        result_text.config(state=tk.DISABLED)
        update_result_word_counter()

    except Exception as e:
        messagebox.showerror("API Error", str(e))

# Set up the GUI
root = tk.Tk()
root.title("Gramparly")

icon = tk.PhotoImage(file="Gramparly.png")
root.iconphoto(False, icon)

# Set the main window background
root.configure(bg=COLOR_BG)

font_family = "Calibri"
font_size = 12

input_frame = tk.Frame(root, bg=COLOR_BG)
input_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

input_label = tk.Label(input_frame, text="Enter text to check:", bg=COLOR_LABEL_BG, fg=COLOR_FG)
input_label.pack(anchor="w")

input_text = tk.Text(input_frame, wrap=tk.WORD, height=10, font=(font_family, font_size),
                     bg=COLOR_TEXT_BG, fg=COLOR_FG, insertbackground=COLOR_FG, 
                     selectbackground="#555555", selectforeground=COLOR_FG)
input_text.pack(expand=True, fill=tk.BOTH)

# Word counter label for input text
input_word_counter_label = tk.Label(input_frame, text="Word Count: 0", anchor="e",
                                    bg=COLOR_LABEL_BG, fg=COLOR_FG)
input_word_counter_label.pack(fill=tk.X, padx=10, pady=5)

# Bind the input_text to the update_input_word_counter function
input_text.bind("<KeyRelease>", update_input_word_counter)
input_text.bind("<ButtonRelease>", update_input_word_counter)

button_frame = tk.Frame(root, bg=COLOR_BG)
button_frame.pack(pady=10)

# Function to create styled buttons
def create_button(parent, text, command):
    return tk.Button(parent, text=text, command=command, bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                    activebackground="#666666", activeforeground=COLOR_BUTTON_FG, borderwidth=0, padx=10, pady=5)

check_button = create_button(button_frame, "Spell/Grammar Check", check_text)
check_button.pack(side=tk.LEFT, padx=5)

simplify_button = create_button(button_frame, "Simplify Text", simplify_text)
simplify_button.pack(side=tk.LEFT, padx=5)

rewrite_button = create_button(button_frame, "Rewrite Text", rewrite_text)
rewrite_button.pack(side=tk.LEFT, padx=5)

# Add the new buttons "+" and "-"
expand_button = create_button(button_frame, "+", expand_text)
expand_button.pack(side=tk.LEFT, padx=5)

shorten_button = create_button(button_frame, "-", shorten_text)
shorten_button.pack(side=tk.LEFT, padx=5)

# Right-click menu for paste function
def show_context_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

context_menu = tk.Menu(root, tearoff=0, bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                       activebackground="#666666", activeforeground=COLOR_BUTTON_FG)
context_menu.add_command(label="Paste", command=paste_text)

input_text.bind("<Button-3>", show_context_menu)
# Remove or modify the following line to prevent clearing the output box on left-click in input box
# input_text.bind("<Button-1>", clear_output_box)  # Clear output box on left-click in input box

# Result frame for showing the checked text
result_frame = tk.Frame(root, bg=COLOR_BG)
result_frame.pack(pady=10, fill=tk.BOTH, expand=True)

result_text = tk.Text(result_frame, wrap=tk.WORD, height=10, font=(font_family, font_size),
                      bg=COLOR_TEXT_BG, fg=COLOR_FG, insertbackground=COLOR_FG, 
                      selectbackground="#555555", selectforeground=COLOR_FG)
result_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
result_text.tag_config('highlight', background=COLOR_HIGHLIGHT, foreground=COLOR_BG)
result_text.config(state=tk.DISABLED)

# Word counter label for result text
result_word_counter_label = tk.Label(result_frame, text="Word Count: 0", anchor="e",
                                     bg=COLOR_LABEL_BG, fg=COLOR_FG)
result_word_counter_label.pack(fill=tk.X, padx=10, pady=5)

# Bind the result_text to the update_result_word_counter function
result_text.bind("<KeyRelease>", update_result_word_counter)
result_text.bind("<ButtonRelease>", update_result_word_counter)

button_frame_2 = tk.Frame(result_frame, bg=COLOR_BG)
button_frame_2.pack(pady=10)

new_button = create_button(button_frame_2, "New Text", new_text)
new_button.pack(side=tk.LEFT, padx=5)

copy_button = create_button(button_frame_2, "Copy Text", copy_text)
copy_button.pack(side=tk.LEFT, padx=5)

move_text_button = create_button(button_frame_2, "⬆ Move Text to Input Box ⬆", move_text_to_input)
move_text_button.pack(side=tk.LEFT, padx=5)

# Ensure the cursor is in the input box when the script starts
input_text.focus_set()

# Update the word counters at startup
update_input_word_counter()
update_result_word_counter()

root.mainloop()
