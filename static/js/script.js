// Hàm xử lý terminal (chỉ chạy trên trang Home)
function initializeTerminal() {
    const terminalOutput = document.getElementById("terminal-output");
    if (!terminalOutput) return; // Thoát nếu không có terminal (trên các trang khác)

    // Dữ liệu để hiển thị
    const data = [
        { key: "skills", value: "" },
        { key: "job", value: "Intern AI Engineer at Opus Solution" },
        { key: "hobbies", value: "exploring AI, open-source, reading, audiobook story, and learning new things" },
        { key: "project", value: "real-time image processing, speech recognition, and chatbot" },
    ];

    // Thêm skills từ skillsData nếu tồn tại
    if (typeof skillsData !== "undefined" && skillsData) {
        let allItems = [];
        skillsData.forEach(element => {
            const items = element.items.map(item => ({ name: item.name }));
            allItems = allItems.concat(items);
        });

        const selectedItems = allItems.slice(0, 10).map(item => `${item.name}`);
        if (allItems.length > 5) {
            selectedItems.push("...");
        }
        data[0].value = selectedItems.join(", ");
    }

    // Chuyển dữ liệu thành các dòng để gõ
    const lines = data.map(item => ({
        prompt: ">$",
        content: ` ${item.key}: ${item.value}`
    }));

    let currentLineIndex = 0;
    let currentCharIndex = 0;
    let isTypingPrompt = true;

    function typeWriter() {
        if (currentLineIndex < lines.length) {
            const currentLine = lines[currentLineIndex];
            if (isTypingPrompt) {
                if (currentCharIndex < currentLine.prompt.length) {
                    if (currentCharIndex === 0) {
                        const newLine = document.createElement("p");
                        newLine.className = "output-line";
                        const promptSpan = document.createElement("span");
                        promptSpan.className = "prompt-symbol";
                        newLine.appendChild(promptSpan);
                        terminalOutput.appendChild(newLine);
                    }
                    const lastLine = terminalOutput.lastChild;
                    const promptSpan = lastLine.querySelector(".prompt-symbol");
                    promptSpan.textContent += currentLine.prompt.charAt(currentCharIndex);
                    currentCharIndex++;
                    setTimeout(typeWriter, 50);
                } else {
                    isTypingPrompt = false;
                    currentCharIndex = 0;
                    setTimeout(typeWriter, 50);
                }
            } else {
                if (currentCharIndex < currentLine.content.length) {
                    const lastLine = terminalOutput.lastChild;
                    if (currentCharIndex === 0) {
                        const contentSpan = document.createElement("span");
                        contentSpan.className = "content-text";
                        lastLine.appendChild(contentSpan);
                    }
                    const contentSpan = lastLine.querySelector(".content-text");
                    contentSpan.textContent += currentLine.content.charAt(currentCharIndex);
                    currentCharIndex++;
                    setTimeout(typeWriter, 50);
                } else {
                    currentLineIndex++;
                    currentCharIndex = 0;
                    isTypingPrompt = true;
                    setTimeout(typeWriter, 500);
                }
            }
        }
    }

    if (lines.length > 0) {
        typeWriter();
    }
}

// Hàm xử lý nút Top-Up (chạy trên mọi trang)
function initializeTopUpButton() {
    const topUpBtn = document.getElementById("top-up-btn");
    if (!topUpBtn) return; // Thoát nếu không có nút Top-Up

    window.addEventListener("scroll", function () {
        if (window.scrollY > 100) {
            topUpBtn.style.display = "block";
        } else {
            topUpBtn.style.display = "none";
        }
    });
}

// Hàm cuộn lên đầu trang
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

// ========== CHATBOT FUNCTIONALITY ==========
class PortfolioChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.isTyping = false;
        this.init();
    }

    init() {
        this.createChatbotHTML();
        this.bindEvents();
        this.addWelcomeMessage();
    }

    createChatbotHTML() {
        const chatbotHTML = `
            <div class="chatbot-container">
                <button class="chatbot-toggle" id="chatbot-toggle">
                    💬
                </button>
                <div class="chatbot-window" id="chatbot-window">
                    <div class="chatbot-header">
                        <span>Portfolio Assistant</span>
                    </div>
                    <div class="chatbot-messages" id="chatbot-messages"></div>
                    <div class="chatbot-input">
                        <input type="text" id="chatbot-input" placeholder="Ask me about Guu's portfolio..." maxlength="500">
                        <button id="chatbot-send">Send</button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }

    bindEvents() {
        const toggle = document.getElementById('chatbot-toggle');
        const sendBtn = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');

        toggle.addEventListener('click', () => this.toggleChatbot());
        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Close chatbot when clicking outside
        document.addEventListener('click', (e) => {
            const chatbotContainer = document.querySelector('.chatbot-container');
            if (!chatbotContainer.contains(e.target) && this.isOpen) {
                this.toggleChatbot();
            }
        });
    }

    toggleChatbot() {
        const window = document.getElementById('chatbot-window');
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            window.classList.add('active');
            document.getElementById('chatbot-input').focus();
        } else {
            window.classList.remove('active');
        }
    }

    addWelcomeMessage() {
        const welcomeMessage = {
            type: 'bot',
            text: "Hello! I'm Guu's portfolio assistant. I can help you learn about his projects, skills, and experience. What would you like to know?",
            suggestions: ['Tell me about projects', 'What skills do you have?', 'Show me your timeline', 'How can I contact you?']
        };
        this.addMessage(welcomeMessage);
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;

        // Add user message
        this.addMessage({
            type: 'user',
            text: message
        });

        input.value = '';
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            this.hideTypingIndicator();

            if (response.ok) {
                this.addMessage({
                    type: 'bot',
                    text: data.response.text,
                    data: data.response.data,
                    suggestions: data.response.suggestions
                });
            } else {
                this.addMessage({
                    type: 'bot',
                    text: 'Sorry, I encountered an error. Please try again.',
                    suggestions: ['Tell me about projects', 'What are your skills?']
                });
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage({
                type: 'bot',
                text: 'Sorry, I\'m having trouble connecting. Please try again later.',
                suggestions: ['Tell me about projects', 'What are your skills?']
            });
        }
    }

    addMessage(message) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.type}`;

        let messageHTML = `<div class="message-content">${this.formatText(message.text)}</div>`;

        // Add data if present
        if (message.data && message.data.length > 0) {
            messageHTML += '<div class="message-data">';
            message.data.forEach(item => {
                messageHTML += `<div style="margin-bottom: 10px;">${this.formatText(item)}</div>`;
            });
            messageHTML += '</div>';
        }

        // Add suggestions if present
        if (message.suggestions && message.suggestions.length > 0) {
            messageHTML += '<div class="suggestions">';
            message.suggestions.forEach(suggestion => {
                messageHTML += `<span class="suggestion-chip" onclick="chatbot.sendSuggestion('${suggestion}')">${suggestion}</span>`;
            });
            messageHTML += '</div>';
        }

        messageDiv.innerHTML = messageHTML;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    sendSuggestion(suggestion) {
        const input = document.getElementById('chatbot-input');
        input.value = suggestion;
        this.sendMessage();
    }

    formatText(text) {
        // Convert markdown-style formatting to HTML
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
            .replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        this.isTyping = true;
        const indicator = document.createElement('div');
        indicator.className = 'message bot';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span>Assistant is typing</span>
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;
        
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.appendChild(indicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
}

// Initialize chatbot
let chatbot;

// Khởi tạo khi trang tải
document.addEventListener("DOMContentLoaded", function () {
    initializeTerminal(); // Khởi tạo terminal (chỉ chạy trên trang Home)
    initializeTopUpButton(); // Khởi tạo nút Top-Up (chạy trên mọi trang)
    chatbot = new PortfolioChatbot(); // Khởi tạo chatbot
});