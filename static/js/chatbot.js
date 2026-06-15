/* ────────────────────────────────────────────────────────────
   Student Rent App — AI Chatbot (rule-based simulation)
   ──────────────────────────────────────────────────────────── */

const KB = [
  {
    patterns: ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"],
    response: "Hey there! 👋 I'm RentBot, your student rental assistant. Ask me anything about finding rentals, posting requests, or how the platform works!"
  },
  {
    patterns: ["how", "post", "submit", "create", "add", "listing", "request"],
    response: "To post a rental request:\n1️⃣ Go to the Home page\n2️⃣ Fill in your Name, Phone, Location, Time, Purpose & Cost\n3️⃣ Hit Submit — your request goes live instantly on the Dashboard!"
  },
  {
    patterns: ["accept", "approve", "book", "booking"],
    response: "To accept a request:\n• Open the Dashboard\n• Click ✅ Accept on a listing you're interested in\n• You'll be taken to the Confirmation screen where you can upload a booking screenshot."
  },
  {
    patterns: ["reject", "decline", "deny", "remove"],
    response: "You can reject any rental request from the Dashboard by clicking ❌ Reject. The listing will be marked as rejected and removed from the active feed."
  },
  {
    patterns: ["confirm", "confirmation", "screenshot", "upload", "proof"],
    response: "After accepting a request, you'll see a Confirmation screen. Upload a screenshot (JPG/PNG) as booking proof — this helps both parties verify the agreement."
  },
  {
    patterns: ["cost", "price", "fee", "how much", "rent", "expensive", "cheap", "affordable"],
    response: "Costs are set by the student posting the request. Prices typically range by:\n💰 Duration (hourly, daily, weekly)\n📍 Location (on-campus vs off-campus)\n🏠 Type (room, car, gear, etc.)\n\nFilter the Dashboard to find requests within your budget!"
  },
  {
    patterns: ["location", "area", "where", "nearby", "campus", "hostel", "dorm"],
    response: "Rental locations are posted by students and usually include dorms, off-campus housing, and nearby areas. The location is listed on each request card in the Dashboard — look for the 📍 icon."
  },
  {
    patterns: ["phone", "contact", "number", "call", "reach"],
    response: "Each rental request shows the poster's phone number (digits only, 7–15 characters). Once a request is accepted, use that number to coordinate directly with the other student."
  },
  {
    patterns: ["purpose", "why", "reason", "use", "type", "kind", "what for"],
    response: "The 'Purpose' field describes what the rental is for — e.g. study space, temporary room, car/vehicle, equipment, etc. This helps others understand what you need or what you're offering."
  },
  {
    patterns: ["time", "duration", "how long", "when", "period", "start", "end"],
    response: "The 'Time' field on a request specifies when the rental is available or needed. This could be a specific date range, time of day, or duration (e.g. '3 days', 'weekends only')."
  },
  {
    patterns: ["safe", "trust", "secure", "scam", "verified"],
    response: "Safety tips:\n🔒 Always confirm bookings with a screenshot\n🤝 Meet in public places for initial handovers\n📞 Verify the phone number before transacting\n🆔 Stick to student-verified requests where possible"
  },
  {
    patterns: ["dashboard", "feed", "browse", "view", "list", "all"],
    response: "The Dashboard shows all active rental requests in a clean card feed. You can see the student's name, location, purpose, time, and cost at a glance — then Accept or Reject with one click."
  },
  {
    patterns: ["delete", "cancel", "withdraw", "take down"],
    response: "Currently, requests can be rejected from the Dashboard which removes them from the active feed. Full delete functionality can be added by an admin via the Firebase Console."
  },
  {
    patterns: ["firebase", "database", "data", "stored", "backend"],
    response: "All rental requests are stored in Firebase Realtime Database — a cloud NoSQL database by Google. Data syncs in real-time, so the Dashboard always shows the latest requests."
  },
  {
    patterns: ["help", "support", "problem", "issue", "error", "not working"],
    response: "I'm sorry you're having trouble! Here's what to check:\n• Make sure all required fields are filled\n• Phone must be digits only (7–15 chars)\n• Check your internet connection\n\nFor setup issues, refer to the README.md file included with the project."
  },
  {
    patterns: ["thank", "thanks", "appreciate", "great", "awesome", "perfect"],
    response: "You're welcome! 😊 Happy to help. Let me know if you have any other questions about the Student Rent App!"
  },
  {
    patterns: ["bye", "goodbye", "see you", "later", "exit"],
    response: "Bye! 👋 Come back whenever you need help finding or posting rentals. Good luck!"
  }
];

const DEFAULT_RESPONSE = "I'm not sure about that one! Try asking about:\n• How to post a request\n• Browsing the dashboard\n• Accepting or rejecting listings\n• Costs, locations, or booking confirmation";

function getBotResponse(input) {
  const lower = input.toLowerCase().trim();
  for (const entry of KB) {
    if (entry.patterns.some(p => lower.includes(p))) {
      return entry.response;
    }
  }
  return DEFAULT_RESPONSE;
}

/* ── DOM ── */
const toggle   = document.getElementById("chat-toggle");
const box      = document.getElementById("chat-box");
const messages = document.getElementById("chat-messages");
const inputEl  = document.getElementById("chat-input");
const sendBtn  = document.getElementById("chat-send");

let isOpen = false;

toggle.addEventListener("click", () => {
  isOpen = !isOpen;
  box.style.display = isOpen ? "flex" : "none";
  toggle.innerHTML = isOpen
    ? `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="white" viewBox="0 0 24 24"><path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>`
    : `<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="white" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>`;
  if (isOpen) {
    inputEl.focus();
    scrollToBottom();
  }
});

function scrollToBottom() {
  messages.scrollTop = messages.scrollHeight;
}

function appendMessage(text, role) {
  const div = document.createElement("div");
  div.className = role === "bot" ? "msg-bot" : "msg-user";
  div.style.whiteSpace = "pre-line";
  div.textContent = text;
  messages.appendChild(div);
  scrollToBottom();
}

function showTyping() {
  const div = document.createElement("div");
  div.className = "msg-bot typing-indicator";
  div.id = "typing";
  div.innerHTML = "<span></span><span></span><span></span>";
  messages.appendChild(div);
  scrollToBottom();
  return div;
}

function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;

  appendMessage(text, "user");
  inputEl.value = "";

  const typing = showTyping();
  const delay = 600 + Math.random() * 500;

  setTimeout(() => {
    typing.remove();
    appendMessage(getBotResponse(text), "bot");
  }, delay);
}

sendBtn.addEventListener("click", sendMessage);
inputEl.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

/* Initial greeting */
setTimeout(() => {
  appendMessage("Hi! I'm RentBot 🤖 — your student rental assistant. How can I help you today?", "bot");
}, 500);
