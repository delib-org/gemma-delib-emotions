import ollama
import tkinter as tk
from tkinter import scrolledtext
import threading

class GemmaChat:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemma 3 Chat")
        self.root.geometry("700x600")
        self.root.configure(bg="#1e1e1e")

        # Conversation history
        self.messages = [
            {
                'role': 'system',
                'content': 'You are a neutral mediator specialized in deliberative democracy.'
            }
        ]

        # Stop flag
        self.stop_generation = False

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="white",
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        self.chat_display.config(state=tk.DISABLED)

        # Configure tags for styling
        self.chat_display.tag_configure("user", foreground="#7eb6ff", font=("Helvetica", 12, "bold"))
        self.chat_display.tag_configure("gemma", foreground="#98c379", font=("Helvetica", 12, "bold"))
        self.chat_display.tag_configure("system", foreground="#e06c75", font=("Helvetica", 10, "italic"))

        # Input frame
        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        # Input field
        self.input_field = tk.Text(
            input_frame,
            height=3,
            font=("Helvetica", 12),
            bg="#3d3d3d",
            fg="#ffffff",
            insertbackground="white",
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind("<Return>", self.on_enter)
        self.input_field.bind("<Shift-Return>", lambda e: None)  # Allow shift+enter for newline

        # Button frame
        button_frame = tk.Frame(input_frame, bg="#1e1e1e")
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))

        # Send button
        self.send_button = tk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            font=("Helvetica", 11),
            bg="#4CAF50",
            fg="white",
            width=8,
            cursor="hand2"
        )
        self.send_button.pack(pady=(0, 5))

        # Stop button
        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            command=self.stop_response,
            font=("Helvetica", 11),
            bg="#f44336",
            fg="white",
            width=8,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_button.pack()

        # Welcome message
        self.append_to_chat("System", "Welcome! Chat with Gemma 3. Press Enter to send, Shift+Enter for new line.\n", "system")

    def on_enter(self, event):
        if not event.state & 0x1:  # If Shift is not pressed
            self.send_message()
            return "break"

    def append_to_chat(self, sender, message, tag):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def append_streaming(self, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_message(self):
        user_input = self.input_field.get("1.0", tk.END).strip()
        if not user_input:
            return

        # Clear input field
        self.input_field.delete("1.0", tk.END)

        # Display user message
        self.append_to_chat("You", user_input, "user")

        # Add to conversation history
        self.messages.append({'role': 'user', 'content': user_input})

        # Disable send button, enable stop button
        self.send_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.stop_generation = False

        # Start response in a thread
        thread = threading.Thread(target=self.get_response, daemon=True)
        thread.start()

    def get_response(self):
        try:
            # Display "Gemma:" prefix
            self.root.after(0, lambda: self.append_to_chat("Gemma", "", "gemma"))

            # Remove the extra newlines from append_to_chat
            self.root.after(0, self.remove_last_newlines)

            stream = ollama.chat(model='gemma3n', messages=self.messages, stream=True)

            assistant_message = ""
            for chunk in stream:
                if self.stop_generation:
                    self.root.after(0, lambda: self.append_streaming(" [stopped]"))
                    break
                content = chunk['message']['content']
                assistant_message += content
                self.root.after(0, lambda c=content: self.append_streaming(c))

            # Add newlines after response
            self.root.after(0, lambda: self.append_streaming("\n\n"))

            # Save to history
            if assistant_message:
                self.messages.append({'role': 'assistant', 'content': assistant_message})

        except Exception as e:
            self.root.after(0, lambda: self.append_to_chat("Error", str(e), "system"))
        finally:
            self.root.after(0, self.reset_buttons)

    def remove_last_newlines(self):
        self.chat_display.config(state=tk.NORMAL)
        # Remove the last 2 newlines that append_to_chat added
        content = self.chat_display.get("1.0", tk.END)
        if content.endswith("\n\n\n"):
            self.chat_display.delete("end-3c", "end-1c")
        self.chat_display.config(state=tk.DISABLED)

    def stop_response(self):
        self.stop_generation = True

    def reset_buttons(self):
        self.send_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = GemmaChat(root)
    root.mainloop()

if __name__ == "__main__":
    main()
