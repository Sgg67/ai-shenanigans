/* BLITZ NFL desk -- chat client.
   All model and user text is inserted with textContent (never innerHTML), so a
   reply can never inject markup into the page. */
(function () {
  "use strict";

  const welcome = document.getElementById("welcome");
  const transcript = document.getElementById("transcript");
  const thread = document.getElementById("thread");
  const form = document.getElementById("composer");
  const input = document.getElementById("input");
  const send = document.getElementById("send");
  const topbarTitle = document.getElementById("topbar-title");
  const topbarMeta = document.getElementById("topbar-meta");
  const historyGroup = document.getElementById("history-group");
  const historyList = document.getElementById("history");
  const coverageGroup = document.getElementById("coverage-group");

  let busy = false;
  const asked = [];

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function showTranscript() {
    if (transcript.hidden) {
      welcome.hidden = true;
      transcript.hidden = false;
      coverageGroup.hidden = true;
      historyGroup.hidden = false;
    }
  }

  function scrollToEnd() {
    transcript.scrollTop = transcript.scrollHeight;
  }

  function addUser(text) {
    const row = el("div", "row-user");
    row.appendChild(el("div", "bubble-user", text));
    thread.appendChild(row);
    scrollToEnd();
  }

  function botShell(label) {
    const row = el("div", "row-bot");
    const tag = el("div", "bot-tag");
    tag.appendChild(el("span", "bot-dot"));
    tag.appendChild(el("span", "bot-name", label));
    row.appendChild(tag);
    thread.appendChild(row);
    return row;
  }

  function addPending() {
    const row = botShell("Blitz is pulling the tape");
    const dots = el("div", "typing-dots");
    dots.appendChild(el("span"));
    dots.appendChild(el("span"));
    dots.appendChild(el("span"));
    row.appendChild(dots);
    scrollToEnd();
    return row;
  }

  function fillAnswer(row, data) {
    row.textContent = "";

    const tag = el("div", "bot-tag");
    tag.appendChild(el("span", "bot-dot"));
    tag.appendChild(el("span", "bot-name", "Blitz"));
    row.appendChild(tag);

    const body = el("div", "bot-body");
    if (data.kind === "refusal") body.classList.add("is-refusal");
    // Blank lines in the reply become separate paragraphs.
    String(data.answer || "")
      .split(/\n{2,}/)
      .map(function (part) { return part.trim(); })
      .filter(Boolean)
      .forEach(function (part) { body.appendChild(el("p", null, part)); });
    row.appendChild(body);

    if (Array.isArray(data.sources) && data.sources.length) {
      const wrap = el("div", "sources");
      wrap.appendChild(el("div", "side-label", "Sources"));
      const list = el("div", "sources-list");
      data.sources.forEach(function (src, i) {
        const srow = el("div", "source-row");
        srow.appendChild(el("span", "source-num", String(i + 1).padStart(2, "0")));
        const link = el("a", "source-link", src.title);
        link.href = src.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        srow.appendChild(link);
        list.appendChild(srow);
      });
      wrap.appendChild(list);
      row.appendChild(wrap);
    }
    scrollToEnd();
  }

  function fillError(row, message) {
    row.textContent = "";
    const tag = el("div", "bot-tag");
    tag.appendChild(el("span", "bot-dot"));
    tag.appendChild(el("span", "bot-name", "Connection error"));
    row.appendChild(tag);
    const body = el("div", "bot-body is-refusal");
    body.appendChild(el("p", null, message));
    row.appendChild(body);
    scrollToEnd();
  }

  function rememberQuestion(text) {
    asked.push(text);
    historyList.textContent = "";
    asked.forEach(function (q, i) {
      const item = el("button", "history-item", q);
      item.type = "button";
      if (i === asked.length - 1) item.classList.add("active");
      item.addEventListener("click", function () {
        input.value = q;
        input.focus();
      });
      historyList.appendChild(item);
    });
    topbarTitle.textContent = text;
  }

  function setBusy(state) {
    busy = state;
    send.disabled = state;
    input.disabled = state;
    // Only overwrite the meta slot while working -- once done, the caller sets it
    // to the source count (per the design) and it must survive.
    if (state) topbarMeta.textContent = "Working…";
  }

  async function ask(question) {
    if (busy || !question) return;
    showTranscript();
    addUser(question);
    rememberQuestion(question);
    setBusy(true);
    const pending = addPending();

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question })
      });
      if (!res.ok) throw new Error("Server responded " + res.status);
      const data = await res.json();
      fillAnswer(pending, data);
      topbarMeta.textContent = data.sources && data.sources.length
        ? data.sources.length + (data.sources.length === 1 ? " source" : " sources")
        : "Ready";
    } catch (err) {
      fillError(pending, "Couldn't reach the NFL desk. Is the server still running?");
      topbarMeta.textContent = "Offline";
    } finally {
      setBusy(false);
      input.focus();
    }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const q = input.value.trim();
    if (!q) return;
    input.value = "";
    ask(q);
  });

  document.getElementById("prompt-grid").addEventListener("click", function (e) {
    const card = e.target.closest(".prompt-card");
    if (card) ask(card.dataset.q);
  });

  document.getElementById("new-question").addEventListener("click", function () {
    thread.textContent = "";
    transcript.hidden = true;
    welcome.hidden = false;
    historyGroup.hidden = true;
    coverageGroup.hidden = false;
    historyList.textContent = "";
    asked.length = 0;
    topbarTitle.textContent = "Session — empty";
    topbarMeta.textContent = "Ready";
    input.value = "";
    input.focus();
  });

  input.focus();
})();
