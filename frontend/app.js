/* ═══════════════════════════════════════════════════
   Jhooth Pakdo — Frontend Application
   ═══════════════════════════════════════════════════ */

const API = window.location.origin;
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

// ─── State ───
let conversationHistory = [];
let isProcessing = false;

// ─── Particles ───
(function initParticles() {
  const canvas = $("#particles-canvas");
  const ctx = canvas.getContext("2d");
  let particles = [];
  const resize = () => { canvas.width = innerWidth; canvas.height = innerHeight; };
  resize();
  window.addEventListener("resize", resize);

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.size = Math.random() * 2 + 0.5;
      this.speedX = (Math.random() - 0.5) * 0.3;
      this.speedY = (Math.random() - 0.5) * 0.3;
      this.opacity = Math.random() * 0.5 + 0.1;
      const colors = ["255,107,53", "255,255,255", "26,140,91"];
      this.color = colors[Math.floor(Math.random() * colors.length)];
    }
    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) this.reset();
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${this.color},${this.opacity})`;
      ctx.fill();
    }
  }

  for (let i = 0; i < 80; i++) particles.push(new Particle());
  (function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach((p) => { p.update(); p.draw(); });
    requestAnimationFrame(animate);
  })();
})();

// ─── Navigation ───
$$(".nav-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    $$(".nav-tab").forEach((t) => t.classList.remove("active"));
    $$(".view").forEach((v) => v.classList.remove("active"));
    tab.classList.add("active");
    $(`#view-${tab.dataset.view}`).classList.add("active");
  });
});

// ─── Auto-resize textarea ───
const textarea = $("#claim-input");
textarea.addEventListener("input", () => {
  textarea.style.height = "auto";
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
  $("#char-count").textContent = `${textarea.value.length} / 2000`;
});
textarea.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

// ─── Quick chips ───
$$(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    textarea.value = chip.dataset.claim;
    textarea.dispatchEvent(new Event("input"));
    sendMessage();
  });
});

// ─── Send button ───
$("#send-btn").addEventListener("click", sendMessage);

// ─── Chat Engine ───
async function sendMessage() {
  const claim = textarea.value.trim();
  if (!claim || isProcessing) return;
  isProcessing = true;
  $("#send-btn").disabled = true;

  // Hide hero on first message
  const hero = $("#hero-section");
  if (hero) hero.style.display = "none";

  // Add user message
  appendMessage("user", claim);
  conversationHistory.push({ role: "user", content: claim });
  textarea.value = "";
  textarea.style.height = "auto";
  $("#char-count").textContent = "0 / 2000";

  // Show typing indicator
  const typingId = showTyping();

  try {
    const res = await fetch(`${API}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claim, history: conversationHistory.slice(0, -1) }),
    });

    removeTyping(typingId);

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unknown error" }));
      appendMessage("bot", `❌ **Error:** ${err.detail || "Something went wrong."}`);
    } else {
      const data = await res.json();
      appendMessage("bot", data.analysis);
      conversationHistory.push({ role: "assistant", content: data.analysis });
    }
  } catch (e) {
    removeTyping(typingId);
    appendMessage("bot", "❌ **Connection error.** Please check your network and try again.");
  }

  isProcessing = false;
  $("#send-btn").disabled = false;
}

function appendMessage(role, content) {
  const container = $("#chat-messages");
  const div = document.createElement("div");
  div.className = `msg ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.textContent = role === "user" ? "👤" : "🛡️";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.innerHTML = role === "bot" ? marked.parse(content) : escapeHtml(content);

  div.appendChild(avatar);
  div.appendChild(bubble);
  container.appendChild(div);
  div.scrollIntoView({ behavior: "smooth", block: "end" });
}

function showTyping() {
  const id = "typing-" + Date.now();
  const container = $("#chat-messages");
  const div = document.createElement("div");
  div.className = "msg bot";
  div.id = id;
  div.innerHTML = `
    <div class="msg-avatar">🛡️</div>
    <div class="msg-bubble">
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>`;
  container.appendChild(div);
  div.scrollIntoView({ behavior: "smooth", block: "end" });
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function escapeHtml(text) {
  const d = document.createElement("div");
  d.textContent = text;
  return d.innerHTML;
}

// ─── Timeline Engine ───
$("#timeline-btn").addEventListener("click", generateTimeline);
$("#timeline-topic").addEventListener("keydown", (e) => {
  if (e.key === "Enter") generateTimeline();
});

async function generateTimeline() {
  const topic = $("#timeline-topic").value.trim();
  if (!topic) return;

  const content = $("#timeline-content");
  const btn = $("#timeline-btn");
  btn.disabled = true;
  btn.textContent = "Generating…";
  content.innerHTML = `<div class="spinner-overlay"><div class="spinner"></div></div>`;

  try {
    const res = await fetch(`${API}/api/timeline`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });

    if (!res.ok) throw new Error("API error");
    const data = await res.json();
    renderTimeline(data);
  } catch (e) {
    content.innerHTML = `<div class="tl-summary"><p>❌ Failed to generate timeline. Please try again.</p></div>`;
  }

  btn.disabled = false;
  btn.textContent = "Generate Timeline";
}

function renderTimeline(data) {
  const content = $("#timeline-content");
  if (data.error) {
    content.innerHTML = `<div class="tl-summary"><p>⚠️ ${data.error}</p></div>`;
    return;
  }

  let html = `
    <div class="tl-summary">
      <h3>${escapeHtml(data.topic || "Timeline")}</h3>
      <p>${escapeHtml(data.summary || "")}</p>
      <div class="tl-summary-stats">
        <span class="tl-stat">📝 Total Steps: <strong>${(data.events || []).length}</strong></span>
      </div>
    </div>`;

  (data.events || []).forEach((ev) => {
    html += `
      <div class="tl-event" data-type="${ev.type || "event"}">
        <span class="tl-type-badge ${ev.type || "event"}">${ev.type || "event"}</span>
        <div class="tl-date">${escapeHtml(ev.date || "Unknown date")}</div>
        <div class="tl-title">${escapeHtml(ev.title || "")}</div>
        <div class="tl-desc">${escapeHtml(ev.description || "")}</div>
      </div>`;
  });

  content.innerHTML = html;
}
