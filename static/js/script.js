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

// Khởi tạo khi trang tải
document.addEventListener("DOMContentLoaded", function () {
    initializeTerminal(); // Khởi tạo terminal (chỉ chạy trên trang Home)
    initializeTopUpButton(); // Khởi tạo nút Top-Up (chạy trên mọi trang)
});