import ollama
import sys
import tty
import termios
import select
import threading

# Global flag to stop generation
stop_generation = False

def check_for_escape():
    """Check if Escape key is pressed (non-blocking)."""
    global stop_generation
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        while not stop_generation:
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1)
                if key == '\x1b':  # Escape key
                    stop_generation = True
                    break
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

# Initialize conversation with system prompt
messages = [
    {
        'role': 'system',
        'content': 'You are a neutral mediator specialized in deliberative democracy.'
    }
]

print("Chat with Gemma 3 (type 'quit' to exit, press ESC to stop response)")
print("-" * 60)

while True:
    # Get user input
    user_input = input("\nYou: ").strip()

    if user_input.lower() in ['quit', 'exit', 'q']:
        print("Goodbye!")
        break

    if not user_input:
        continue

    # Add user message to history
    messages.append({'role': 'user', 'content': user_input})

    # Get response from Gemma with streaming
    print("\nGemma: ", end="", flush=True)

    # Reset stop flag and start escape key listener
    stop_generation = False
    escape_thread = threading.Thread(target=check_for_escape, daemon=True)
    escape_thread.start()

    stream = ollama.chat(model='gemma3n', messages=messages, stream=True)

    assistant_message = ""
    try:
        for chunk in stream:
            if stop_generation:
                print(" [stopped]", end="")
                break
            content = chunk['message']['content']
            print(content, end="", flush=True)
            assistant_message += content
    except Exception:
        pass

    # Signal thread to stop
    stop_generation = True

    print()  # New line after response

    # Add assistant response to history (even if partial)
    if assistant_message:
        messages.append({'role': 'assistant', 'content': assistant_message})