document.addEventListener("DOMContentLoaded", () => {
  const askButton = document.getElementById("ask-button");
  const input = document.getElementById("question-input");

  askButton.addEventListener("click", async () => {
    const question = input.value.trim();
    if (!question) return;

    renderMessage("You", question);

    try {
      const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      if (data.answer) {
        const answer = JSON.stringify(data.answer, null, 2);
        renderMessage("Bot", answer, data.sql);
        addToHistory({ question, answer: data.answer, sql: data.sql });
      } else {
        renderMessage("Bot", "❌ " + data.error);
      }
    } catch (error) {
      renderMessage("Bot", "❌ Fetch error");
    }

    input.value = "";
  });

  loadHistory();
});

function renderMessage(sender, text, sql = "") {
  const chatWindow = document.getElementById("chat-window");
  const box = document.createElement("div");
  box.className = "chat-entry";

  const deleteBtn = `<button onclick="deleteMessage(this)">🗑️</button>`;
  const copyBtn = `<button onclick="copyToClipboard('${escapeQuotes(text)}')">📋</button>`;
  const speakBtn = `<button onclick="speak('${escapeQuotes(text)}')">🔊</button>`;
  const sqlBlock = sql ? `<pre class="sql-block"><strong>SQL Query:</strong>\n${sql}</pre>` : "";

  box.innerHTML = `<strong>${sender}:</strong> ${speakBtn} ${copyBtn} ${deleteBtn}<pre>${text}</pre>${sqlBlock}`;
  chatWindow.appendChild(box);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function escapeQuotes(str) {
  return str?.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text);
}

function speak(text) {
  const utter = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.speak(utter);
}

function deleteMessage(btn) {
  const message = btn.closest(".chat-entry");
  message.remove();
}

function addToHistory(entry) {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "[]");

  // ✅ Avoid duplicates
  const exists = history.some(item => item.question.trim().toLowerCase() === entry.question.trim().toLowerCase());
  if (!exists) {
    history.push(entry);
    localStorage.setItem("chatHistory", JSON.stringify(history));
    loadHistory();
  }
}

function loadHistory() {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "[]");
  const ul = document.getElementById("chat-history");
  ul.innerHTML = "";

  history.forEach((h, index) => {
    const li = document.createElement("li");
    li.className = "history-item";

    const span = document.createElement("span");
    span.textContent = h.question;
    span.onclick = () => {
      document.getElementById("chat-window").innerHTML = "";
      renderMessage("You", h.question);
      renderMessage("Bot", JSON.stringify(h.answer, null, 2), h.sql);
    };

    const delBtn = document.createElement("button");
    delBtn.textContent = "🗑️";
    delBtn.onclick = (e) => {
      e.stopPropagation();
      history.splice(index, 1);
      localStorage.setItem("chatHistory", JSON.stringify(history));
      loadHistory();
    };

    li.appendChild(span);
    li.appendChild(delBtn);
    ul.appendChild(li);
  });
}

function clearHistory() {
  localStorage.removeItem("chatHistory");
  loadHistory();
  document.getElementById("chat-window").innerHTML = "";
}

function newChat() {
  document.getElementById("chat-window").innerHTML = "";
}

