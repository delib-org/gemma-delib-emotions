# Gemma Chat with Emotions

A friendly chat application that runs on your computer! Chat with Gemma, an AI assistant that shows emotions through an animated face that changes based on the conversation.

![Gemma showing different emotions](https://img.shields.io/badge/Emotions-😊😢🤩🤔🥰-blue)

## What Does This Do?

This is a chat application where you can talk to an AI called Gemma. The special thing about this app is that Gemma has a **face that shows emotions**:

- 😊 **Happy** - When having a nice conversation
- 😢 **Sad** - When you share something difficult
- 🤩 **Excited** - When talking about amazing things
- 🤔 **Thinking** - When pondering a question
- 🥰 **Loving** - When showing care
- 🤗 **Empathetic** - When offering support

## For Non-Technical Users: Getting Help

**Don't worry if you've never coded before!** You can use AI assistants to help you set this up. Here's how:

### Use an AI Agent to Help You

Copy this message and send it to one of these AI assistants:

**ChatGPT**, **Claude**, **Gemini**, or **GitHub Copilot**

```
I want to run the Gemma Chat application from this GitHub repo:
https://github.com/delib-org/gemma-delib-emotions

I'm not technical. Please help me step-by-step to:
1. Install Python on my computer (I use [Windows/Mac/Linux])
2. Install Ollama
3. Download the Gemma model
4. Run the application

Please give me simple instructions I can follow, and explain what each step does.
```

The AI will guide you through each step!

---

## Step-by-Step Instructions

If you want to try yourself, here's what you need to do:

### Step 1: Install Python

Python is the programming language this app uses.

**On Mac:**
1. Open the "Terminal" app (search for it in Spotlight)
2. Copy and paste this command, then press Enter:
   ```
   brew install python
   ```
   (If you don't have Homebrew, the AI assistant can help you install it first)

**On Windows:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. Run the installer
4. **Important:** Check the box that says "Add Python to PATH"
5. Click "Install Now"

### Step 2: Install Ollama

Ollama is the tool that runs the AI on your computer.

1. Go to https://ollama.ai
2. Click "Download"
3. Install it like any other application

### Step 3: Download the Gemma Model

1. Open Terminal (Mac) or Command Prompt (Windows)
2. Type this and press Enter:
   ```
   ollama pull gemma3n
   ```
3. Wait for it to download (this may take a few minutes)

### Step 4: Download This Application

1. Go to https://github.com/delib-org/gemma-delib-emotions
2. Click the green "Code" button
3. Click "Download ZIP"
4. Unzip the file somewhere you can find it (like your Desktop)

### Step 5: Run the Application

1. Open Terminal (Mac) or Command Prompt (Windows)
2. Navigate to where you saved the file:
   ```
   cd Desktop/gemma-delib-emotions-main
   ```
3. Run the application:
   ```
   python3 gemma_web.py
   ```
4. Open your web browser and go to: **http://localhost:8080**

You should see Gemma's smiling face ready to chat!

---

## Troubleshooting

**"Command not found" error?**
- Make sure Python and Ollama are installed correctly
- Ask an AI assistant for help with the specific error message

**The face doesn't appear?**
- Try refreshing the page (Ctrl+R or Cmd+R)
- Make sure you're using a modern browser (Chrome, Firefox, Safari, Edge)

**Gemma doesn't respond?**
- Make sure Ollama is running
- Make sure you downloaded the gemma3n model

**Still stuck?**
Copy your error message and ask an AI assistant (ChatGPT, Claude, etc.) for help!

---

## About

This project was created to explore how AI can express emotions in conversations. It's part of experiments in deliberative democracy and human-AI interaction.

Created with help from Claude Code.

## License

MIT License - Feel free to use, modify, and share!
