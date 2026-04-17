(function () {
    const widget = document.querySelector(".saathi-widget");
    if (!widget) return;

    const toggle = widget.querySelector(".saathi-toggle");
    const panel = widget.querySelector(".saathi-panel");
    const closeButton = widget.querySelector(".saathi-close");
    const form = widget.querySelector(".saathi-form");
    const input = widget.querySelector(".saathi-input");
    const messages = widget.querySelector(".saathi-messages");
    const quickActionButtons = widget.querySelectorAll("[data-saathi-prompt]");
    const chatUrl = widget.dataset.chatUrl;

    function getCsrfToken() {
        const tokenMeta = document.querySelector('meta[name="csrf-token"]');
        return tokenMeta ? tokenMeta.getAttribute("content") : "";
    }

    function setOpen(open) {
        panel.hidden = !open;
        toggle.setAttribute("aria-expanded", String(open));
        if (open) {
            input.focus();
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
        let formatted = escapeHtml(text);
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
        formatted = formatted.replace(/\n/g, "<br>");
        return formatted;
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

        appendMessage(message, "user");
        input.value = "";

        const loading = document.createElement("article");
        loading.className = "saathi-message saathi-message-bot saathi-message-loading";
        loading.innerHTML = "<p>Thinking...</p>";
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

            if (!response.ok) {
                appendMessage(data.error || "Sorry, I could not respond right now.", "bot");
                return;
            }

            appendMessage(data.reply, "bot");
        } catch (error) {
            loading.remove();
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
