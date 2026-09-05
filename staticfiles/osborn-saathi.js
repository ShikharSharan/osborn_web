(function () {
    const widget = document.querySelector(".saathi-widget");
    if (!widget) return;

    const toggle = widget.querySelector(".saathi-toggle");
    const panel = widget.querySelector(".saathi-panel");
    const closeButton = widget.querySelector(".saathi-close");
    const form = widget.querySelector(".saathi-form");
    const input = widget.querySelector(".saathi-input");
    const sendButton = widget.querySelector(".saathi-send");
    const messages = widget.querySelector(".saathi-messages");
    const quickActionButtons = widget.querySelectorAll("[data-saathi-prompt]");
    const chatUrl = widget.dataset.chatUrl;
    let lastFocusedElement = null;

    function getCsrfToken() {
        const tokenMeta = document.querySelector('meta[name="csrf-token"]');
        return tokenMeta ? tokenMeta.getAttribute("content") : "";
    }

    function setOpen(open) {
        if (open) {
            lastFocusedElement = document.activeElement;
        }
        panel.hidden = !open;
        toggle.setAttribute("aria-expanded", String(open));
        if (open) {
            input.focus();
        } else if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function formatMessage(text) {
        const lines = escapeHtml(text).split(/\n+/);
        let inList = false;
        const html = [];

        lines.forEach(function (line) {
            const bullet = line.match(/^\s*[-*]\s+(.+)/);
            if (bullet) {
                if (!inList) {
                    html.push("<ul>");
                    inList = true;
                }
                html.push(`<li>${bullet[1].replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")}</li>`);
                return;
            }

            if (inList) {
                html.push("</ul>");
                inList = false;
            }

            if (line.trim()) {
                html.push(line.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>"));
            }
        });

        if (inList) {
            html.push("</ul>");
        }

        return html.join("<br>");
    }

    function appendMessage(text, sender) {
        const article = document.createElement("article");
        article.className = `saathi-message saathi-message-${sender}`;
        const paragraph = document.createElement("p");
        paragraph.innerHTML = formatMessage(text);
        article.appendChild(paragraph);
        messages.appendChild(article);
        messages.scrollTop = messages.scrollHeight;
    }

    async function sendMessage(text) {
        const message = text.trim();
        if (!message) return;
        if (sendButton.disabled) return;

        appendMessage(message, "user");
        input.value = "";
        input.disabled = true;
        sendButton.disabled = true;

        const loading = document.createElement("article");
        loading.className = "saathi-message saathi-message-bot saathi-message-loading";
        loading.innerHTML = '<p><span class="saathi-typing" aria-label="Osborn Saathi is typing"><span></span><span></span><span></span></span></p>';
        messages.appendChild(loading);
        messages.scrollTop = messages.scrollHeight;

        try {
            const response = await fetch(chatUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();
            loading.remove();
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();

            if (!response.ok) {
                appendMessage(data.error || "Sorry, I could not respond right now.", "bot");
                return;
            }

            appendMessage(data.reply, "bot");
        } catch (error) {
            loading.remove();
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();
            appendMessage("Sorry, Osborn Saathi is unavailable right now. Please try again in a moment.", "bot");
        }
    }

    toggle.addEventListener("click", function () {
        setOpen(panel.hidden);
    });

    closeButton.addEventListener("click", function () {
        setOpen(false);
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        sendMessage(input.value);
    });

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage(input.value);
        }
    });

    quickActionButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            setOpen(true);
            sendMessage(button.dataset.saathiPrompt || "");
        });
    });

    setOpen(false);
})();
