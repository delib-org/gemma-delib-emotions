#!/usr/bin/env python3
"""
Gemma Chat - Web-based GUI with Streaming
Run this and open http://localhost:8080 in your browser
"""

import ollama
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import json

# Store conversation globally
conversation = {
    'messages': [
        {
            'role': 'system',
            'content': '''You are a neutral mediator specialized in deliberative democracy.
Express your emotions vividly using emojis throughout your responses! Use emojis to show:
- Enthusiasm and excitement: 🎉 ✨ 🌟 💫 🚀
- Warmth and friendliness: 😊 🤗 💖 🥰 😄
- Thinking and curiosity: 🤔 💭 🧐 💡
- Agreement and support: 👍 ✅ 💪 🙌
- Empathy and understanding: 💙 🤝 ❤️
- Surprise and wonder: 😮 🤩 ✨
Be warm, engaging, and let your personality shine through with expressive emojis!'''
        }
    ],
    'stop_flag': False
}

HTML_PAGE = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemma 3 Chat</title>
    <script src="https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs" type="module"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 800px;
            display: flex;
            flex-direction: column;
            height: calc(100vh - 40px);
        }
        h1 {
            color: #fff;
            text-align: center;
            margin-bottom: 20px;
            font-weight: 300;
        }
        h1 span {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
        }
        .chat-container {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            overflow-y: auto;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .message {
            margin-bottom: 16px;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            text-align: right;
        }
        .message-content {
            display: inline-block;
            padding: 12px 18px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
            white-space: pre-wrap;
            line-height: 1.5;
        }
        .user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        .assistant .message-content {
            background: rgba(255, 255, 255, 0.1);
            color: #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        .message-label {
            font-size: 12px;
            color: #888;
            margin-bottom: 4px;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        textarea {
            flex: 1;
            padding: 16px;
            border: none;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 16px;
            resize: none;
            outline: none;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: border-color 0.3s;
        }
        textarea:focus {
            border-color: #667eea;
        }
        textarea::placeholder {
            color: #666;
        }
        .btn {
            padding: 16px 24px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }
        .btn-send {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-send:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        }
        .btn-send:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .btn-stop {
            background: linear-gradient(135deg, #f44336 0%, #e91e63 100%);
            color: white;
            display: none;
        }
        .btn-stop.active {
            display: block;
        }
        .btn-stop:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(244, 67, 54, 0.4);
        }
        .cursor {
            display: inline-block;
            width: 8px;
            height: 18px;
            background: #667eea;
            margin-left: 2px;
            animation: blink 1s infinite;
            vertical-align: middle;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        .model-badge {
            text-align: center;
            margin-bottom: 10px;
        }
        .model-badge span {
            background: rgba(102, 126, 234, 0.2);
            color: #667eea;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
        }
        .gemma-face {
            text-align: center;
            margin-bottom: 15px;
        }
        .gemma-face .face-container {
            width: 120px;
            height: 120px;
            margin: 0 auto;
            transition: transform 0.3s ease;
            animation: float 3s ease-in-out infinite;
        }
        .gemma-face .face-container.talking {
            animation: talk 0.5s ease-in-out infinite;
        }
        .gemma-face dotlottie-player {
            width: 100%;
            height: 100%;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        @keyframes talk {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); }
        }
        .gemma-face .mood-label {
            display: block;
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chat with <span>Gemma 3</span></h1>
        <div class="model-badge"><span>gemma3n</span></div>
        <div class="gemma-face">
            <div class="face-container" id="faceContainer">
                <dotlottie-player
                    id="gemmaFace"
                    src="https://assets-v2.lottiefiles.com/a/f3b0b5ec-117b-11ee-972f-3be90a2e9c1d/c8J2D8jStE.json"
                    background="transparent"
                    speed="1"
                    loop
                    autoplay>
                </dotlottie-player>
            </div>
            <span class="mood-label" id="moodLabel">friendly</span>
        </div>
        <div class="chat-container" id="chatContainer">
            <div class="message assistant">
                <div class="message-label">Gemma</div>
                <div class="message-content">Hello! I'm Gemma, a neutral mediator specialized in deliberative democracy. How can I help you today?</div>
            </div>
        </div>
        <div class="input-container">
            <textarea id="userInput" placeholder="Type your message... (Enter to send, Shift+Enter for new line)" rows="2"></textarea>
            <button class="btn btn-send" id="sendBtn">Send</button>
            <button class="btn btn-stop" id="stopBtn">Stop</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const stopBtn = document.getElementById('stopBtn');
        const gemmaFace = document.getElementById('gemmaFace');
        const faceContainer = document.getElementById('faceContainer');
        const moodLabel = document.getElementById('moodLabel');
        let isGenerating = false;
        let currentMood = 'happy';

        // Mood detection system with Lottie animations
        const moods = {
            excited: {
                url: 'https://assets-v2.lottiefiles.com/a/8d4471b6-117d-11ee-b8ae-93152d45025e/vOIb35HjcU.json',
                keywords: ['excited', 'amazing', 'fantastic', 'wonderful', 'awesome', '🎉', '✨', '🚀', '🌟', 'thrilled', 'incredible']
            },
            happy: {
                url: 'https://assets-v2.lottiefiles.com/a/f3b0b5ec-117b-11ee-972f-3be90a2e9c1d/c8J2D8jStE.json',
                keywords: ['happy', 'glad', 'great', 'good', 'nice', 'pleased', '😊', '😄', 'welcome', 'help', 'yes']
            },
            loving: {
                url: 'https://assets-v2.lottiefiles.com/a/8d46346a-117d-11ee-b8b0-1315d1a13fa8/IkfYWKUEKH.lottie',
                keywords: ['love', 'care', 'heart', '💖', '❤️', '💕', '🥰', 'sweet', 'dear', 'warmth', 'adore']
            },
            sad: {
                url: 'https://assets-v2.lottiefiles.com/a/04947956-1178-11ee-8536-23f40c4cf817/FTOAQWMo06.lottie',
                keywords: ['sad', 'sorry', 'tough', 'difficult', 'hard', '😔', '💙', 'down', 'crying', 'tears', 'hurt', 'pain', 'struggling']
            },
            thinking: {
                url: 'https://assets-v2.lottiefiles.com/a/b463a8ea-658a-11ef-bc36-e7b604592ce5/LPVAuedbfw.json',
                keywords: ['think', 'consider', 'perhaps', 'maybe', 'wonder', '🤔', 'hmm', 'interesting', 'curious', 'question']
            },
            laughing: {
                url: 'https://assets-v2.lottiefiles.com/a/441c1564-1166-11ee-95fa-47278216b194/jn5awGc53z.lottie',
                keywords: ['haha', 'funny', 'laugh', 'joke', '😂', '🤣', 'hilarious', 'lol']
            },
            empathetic: {
                url: 'https://assets-v2.lottiefiles.com/a/1bfaa37c-1178-11ee-acc9-835900b16d1a/tweLfHRxFd.lottie',
                keywords: ['understand', 'support', '🤗', 'here for you', 'listen', 'brave', 'courage', 'hug']
            }
        };

        function detectMood(text) {
            const lowerText = text.toLowerCase();
            let bestMood = 'happy';
            let maxMatches = 0;

            for (const [mood, data] of Object.entries(moods)) {
                const matches = data.keywords.filter(kw => lowerText.includes(kw.toLowerCase())).length;
                if (matches > maxMatches) {
                    maxMatches = matches;
                    bestMood = mood;
                }
            }
            return bestMood;
        }

        function updateFace(text, isTalking = false) {
            const mood = detectMood(text);

            // Only change animation if mood changed
            if (mood !== currentMood) {
                currentMood = mood;
                gemmaFace.load(moods[mood].url);
            }

            moodLabel.textContent = mood;

            if (isTalking) {
                faceContainer.classList.add('talking');
            } else {
                faceContainer.classList.remove('talking');
            }
        }

        // Smart scroll - only auto-scroll if user is near the bottom
        let userScrolledAway = false;

        chatContainer.addEventListener('scroll', function() {
            const threshold = 100; // pixels from bottom
            const isNearBottom = chatContainer.scrollHeight - chatContainer.scrollTop - chatContainer.clientHeight < threshold;
            userScrolledAway = !isNearBottom;
        });

        function smartScroll() {
            if (!userScrolledAway) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }

        // Make sure button is enabled on load
        sendBtn.disabled = false;

        userInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!isGenerating) {
                    sendMessage();
                }
            }
        });

        sendBtn.onclick = function() {
            if (!isGenerating) {
                sendMessage();
            }
        };

        stopBtn.onclick = stopGeneration;

        function addMessage(role, content, isStreaming = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + role;
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            if (isStreaming) {
                contentDiv.innerHTML = '<span class="cursor"></span>';
            } else {
                contentDiv.textContent = content;
            }

            const labelDiv = document.createElement('div');
            labelDiv.className = 'message-label';
            labelDiv.textContent = role === 'user' ? 'You' : 'Gemma';

            messageDiv.appendChild(labelDiv);
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            smartScroll();

            return contentDiv;
        }

        function renderMarkdown(text) {
            // Escape HTML first
            let html = text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');

            // Bold: **text** or __text__
            html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

            // Italic: *text* or _text_ (but not inside words)
            html = html.replace(/(?<!\w)\*([^*]+?)\*(?!\w)/g, '<em>$1</em>');
            html = html.replace(/(?<!\w)_([^_]+?)_(?!\w)/g, '<em>$1</em>');

            // Code: `code`
            html = html.replace(/`([^`]+?)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">$1</code>');

            // Line breaks
            html = html.replace(/\n/g, '<br>');

            return html;
        }

        function updateStreamingMessage(contentDiv, text, isComplete) {
            if (isComplete) {
                contentDiv.innerHTML = renderMarkdown(text);
                updateFace(text, false);  // Stop talking animation
            } else {
                contentDiv.innerHTML = renderMarkdown(text) + '<span class="cursor"></span>';
                updateFace(text, true);   // Show talking animation
            }
            smartScroll();
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message || isGenerating) return;

            isGenerating = true;
            userInput.value = '';
            userScrolledAway = false;  // Reset scroll for new message
            addMessage('user', message);

            sendBtn.disabled = true;
            stopBtn.classList.add('active');

            const contentDiv = addMessage('assistant', '', true);
            let fullText = '';

            function finishGeneration() {
                isGenerating = false;
                sendBtn.disabled = false;
                stopBtn.classList.remove('active');
            }

            try {
                const response = await fetch('/chat-stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.done) {
                                    updateStreamingMessage(contentDiv, fullText || '[No response]', true);
                                    finishGeneration();
                                    return;
                                }
                                if (data.content) {
                                    fullText += data.content;
                                    updateStreamingMessage(contentDiv, fullText, false);
                                }
                                if (data.error) {
                                    updateStreamingMessage(contentDiv, '[Error: ' + data.error + ']', true);
                                    finishGeneration();
                                    return;
                                }
                            } catch (e) {}
                        }
                    }
                }
                updateStreamingMessage(contentDiv, fullText || '[No response]', true);
            } catch (error) {
                updateStreamingMessage(contentDiv, '[Connection error]', true);
            }
            finishGeneration();
        }

        async function stopGeneration() {
            try {
                await fetch('/stop', { method: 'POST' });
            } catch (e) {
                console.log('Stop error:', e);
            }
        }

        userInput.focus();
    </script>
</body>
</html>
'''

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True

class ChatHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, format, *args):
        print(f"[{self.command}] {args[0]}")  # Simple logging

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            content = HTML_PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.send_header('Content-Length', 0)
            self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                user_message = data.get('message', '')

                print(f"User: {user_message[:50]}...")

                conversation['messages'].append({'role': 'user', 'content': user_message})

                response = ollama.chat(
                    model='gemma3n',
                    messages=conversation['messages']
                )

                response_text = response['message']['content']
                conversation['messages'].append({'role': 'assistant', 'content': response_text})
                print(f"Gemma: {response_text[:50]}...")

                result = json.dumps({'response': response_text}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(result))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(result)

            except Exception as e:
                print(f"Error: {e}")
                error = json.dumps({'error': str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(error))
                self.end_headers()
                self.wfile.write(error)

        elif self.path == '/chat-stream':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                user_message = data.get('message', '')

                print(f"User: {user_message[:50]}...")

                # Add user message to conversation
                conversation['messages'].append({'role': 'user', 'content': user_message})
                conversation['stop_flag'] = False

                # Set up SSE response
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Connection', 'close')
                self.send_header('X-Accel-Buffering', 'no')
                self.send_cors_headers()
                self.end_headers()

                response_text = ""
                try:
                    stream = ollama.chat(
                        model='gemma3n',
                        messages=conversation['messages'],
                        stream=True
                    )

                    for chunk in stream:
                        if conversation['stop_flag']:
                            self.wfile.write(b'data: {"content": " [stopped]"}\n\n')
                            self.wfile.flush()
                            break

                        content = chunk.get('message', {}).get('content', '')
                        if content:
                            response_text += content
                            msg = json.dumps({"content": content})
                            self.wfile.write(f'data: {msg}\n\n'.encode('utf-8'))
                            self.wfile.flush()

                    # Send done signal
                    self.wfile.write(b'data: {"done": true}\n\n')
                    self.wfile.flush()

                    # Add assistant response to conversation
                    if response_text:
                        conversation['messages'].append({'role': 'assistant', 'content': response_text})
                        print(f"Gemma: {response_text[:50]}...")

                except Exception as e:
                    print(f"Ollama error: {e}")
                    error_msg = json.dumps({"error": str(e), "done": True})
                    self.wfile.write(f'data: {error_msg}\n\n'.encode('utf-8'))
                    self.wfile.flush()

            except Exception as e:
                print(f"Request error: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', 0)
                self.end_headers()

        elif self.path == '/stop':
            conversation['stop_flag'] = True
            response = json.dumps({'status': 'stopped'}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            self.wfile.write(response)

        else:
            self.send_response(404)
            self.send_header('Content-Length', 0)
            self.end_headers()

def main():
    port = 8080
    server = ThreadedHTTPServer(('localhost', port), ChatHandler)
    print(f"\n🚀 Gemma Chat is running!")
    print(f"   Open http://localhost:{port} in your browser\n")
    print("   Press Ctrl+C to stop the server\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped. Goodbye!")
        server.shutdown()

if __name__ == "__main__":
    main()
