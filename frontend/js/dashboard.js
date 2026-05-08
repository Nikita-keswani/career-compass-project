/**
 * dashboard.js — Dashboard orchestration, persistent threads, chat, resume analytics
 */
document.addEventListener("DOMContentLoaded", () => {
  // ── Auth guard ─────────────────────────────────────────
  const token    = localStorage.getItem("access_token");
  const username = localStorage.getItem("username") || "User";
  if (!token) { window.location.href = "index.html"; return; }

  // ── DOM refs ───────────────────────────────────────────
  const pageTitle  = document.getElementById("page-title");
  const avatarEl   = document.getElementById("user-avatar");
  const usernameEl = document.getElementById("user-name");
  const logoutBtn  = document.getElementById("btn-logout");
  const navLinks   = document.querySelectorAll(".sidebar-nav a");
  const panels     = document.querySelectorAll(".panel");

  // Chat panels
  const careerMessages = document.getElementById("career-messages");
  const careerInput    = document.getElementById("career-input");
  const careerSendBtn  = document.getElementById("career-send");
  const careerEmpty    = document.getElementById("career-empty");

  const skitMessages   = document.getElementById("skit-messages");
  const skitInput      = document.getElementById("skit-input");
  const skitSendBtn    = document.getElementById("skit-send");
  const skitEmpty      = document.getElementById("skit-empty");

  // Thread UI
  const careerThreadsSection = document.getElementById("career-threads-section");
  const skitThreadsSection   = document.getElementById("skit-threads-section");
  const careerThreadList     = document.getElementById("career-thread-list");
  const skitThreadList       = document.getElementById("skit-thread-list");
  const careerNewThreadBtn   = document.getElementById("career-new-thread");
  const skitNewThreadBtn     = document.getElementById("skit-new-thread");

  // Resume panel
  const fileInput        = document.getElementById("resume-file");
  const fileNameDisplay  = document.getElementById("file-name");
  const resumeForm       = document.getElementById("resume-form");
  const resumeLoader     = document.getElementById("resume-loader");
  const resumeAnalytics  = document.getElementById("resume-analytics");

  // ── Init UI ────────────────────────────────────────────
  avatarEl.textContent = username.charAt(0).toUpperCase();
  usernameEl.textContent = username;

  // Configure marked for markdown rendering
  if (typeof marked !== "undefined") {
    marked.setOptions({ breaks: true, gfm: true });
  }

  // ═══════════════════════════════════════════════════════
  //  THREAD MANAGEMENT (persistent via backend)
  // ═══════════════════════════════════════════════════════

  // In-memory thread store: { id, name, messages: [{text, role}], loaded }
  const threadStore = {
    career: [],
    skit: [],
  };

  let activeCareerThreadIdx = -1;
  let activeSkitThreadIdx   = -1;
  let isLoadingThreads = false; // Guard against re-entrant calls

  function generateThreadId(type) {
    return `${type}-${username}-${Date.now()}`;
  }

  // Creates a new local thread (not persisted until a message is sent)
  function createLocalThread(type, id, name) {
    const threadId = id || generateThreadId(type);
    const threadName = name || `New Thread`;
    const thread = { id: threadId, name: threadName, messages: [], loaded: !id };
    threadStore[type].push(thread);
    return threadStore[type].length - 1;
  }

  // Load threads from backend on startup (called only once)
  async function loadThreadsFromBackend(type, chatType) {
    try {
      const data = await listThreads(username, chatType);
      const threads = data.threads || [];
      threadStore[type] = []; // Reset

      threads.forEach((t) => {
        threadStore[type].push({
          id: t.id,
          name: t.name,
          messages: [],
          loaded: false,
        });
      });

      if (threadStore[type].length > 0) {
        if (type === "career") activeCareerThreadIdx = 0;
        else activeSkitThreadIdx = 0;
      } else {
        const idx = createLocalThread(type);
        if (type === "career") activeCareerThreadIdx = idx;
        else activeSkitThreadIdx = idx;
      }

      renderThreadList(type);
    } catch (err) {
      console.warn(`Failed to load ${type} threads:`, err);
      const idx = createLocalThread(type);
      if (type === "career") activeCareerThreadIdx = idx;
      else activeSkitThreadIdx = idx;
      renderThreadList(type);
    }
  }

  // Load thread history lazily (only when user clicks a thread)
  async function loadThreadHistory(type, idx) {
    const thread = threadStore[type][idx];
    if (!thread || thread.loaded) return;

    const chatType = type === "career" ? "career_assistant" : "skit_assistant";
    try {
      const data = await getThreadHistory(username, thread.id, chatType);
      const history = data.history || [];
      thread.messages = [];
      history.forEach((entry) => {
      thread.messages.push({ text: entry.user_input, role: "user", timestamp: entry.timestamp || null });
        thread.messages.push({ text: entry.bot_response, role: "assistant", timestamp: entry.timestamp || null });
      });
    } catch (err) {
      console.warn(`Failed to load history for thread ${thread.id}:`, err);
    } finally {
      thread.loaded = true; // Always mark as loaded to avoid retrying
    }
  }

  function renderThreadList(type) {
    const list      = type === "career" ? careerThreadList : skitThreadList;
    const activeIdx = type === "career" ? activeCareerThreadIdx : activeSkitThreadIdx;

    list.innerHTML = "";
    // Build indices in reverse so newest threads appear on top
    const indices = threadStore[type].map((_, i) => i).reverse();
    indices.forEach((idx) => {
      const thread = threadStore[type][idx];
      const li = document.createElement("li");
      if (idx === activeIdx) li.classList.add("active");

      const nameSpan = document.createElement("span");
      nameSpan.classList.add("thread-name");
      nameSpan.textContent = thread.name;
      nameSpan.addEventListener("click", () => switchThread(type, idx));

      const delBtn = document.createElement("button");
      delBtn.classList.add("btn-delete-thread");
      delBtn.textContent = "✕";
      delBtn.title = "Delete thread";
      delBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        handleDeleteThread(type, idx);
      });

      li.appendChild(nameSpan);
      li.appendChild(delBtn);
      list.appendChild(li);
    });
  }

  async function handleDeleteThread(type, idx) {
    const thread = threadStore[type][idx];
    if (!confirm(`Delete thread "${thread.name}"? This cannot be undone.`)) return;

    const chatType = type === "career" ? "career_assistant" : "skit_assistant";
    try {
      await deleteThread(username, thread.id, chatType);
    } catch (err) {
      console.warn("Failed to delete thread from server:", err);
    }

    // Remove locally
    threadStore[type].splice(idx, 1);

    // Fix active index
    const activeIdx = type === "career" ? activeCareerThreadIdx : activeSkitThreadIdx;
    if (threadStore[type].length === 0) {
      // Create a fresh empty thread
      const newIdx = createLocalThread(type);
      if (type === "career") activeCareerThreadIdx = newIdx;
      else activeSkitThreadIdx = newIdx;
    } else if (idx === activeIdx) {
      // Deleted the active thread — switch to the first one
      const newIdx = 0;
      if (type === "career") activeCareerThreadIdx = newIdx;
      else activeSkitThreadIdx = newIdx;
    } else if (idx < activeIdx) {
      // Shift active index down
      if (type === "career") activeCareerThreadIdx--;
      else activeSkitThreadIdx--;
    }

    renderThreadList(type);
    const currentIdx = type === "career" ? activeCareerThreadIdx : activeSkitThreadIdx;
    const container  = type === "career" ? careerMessages : skitMessages;
    const emptyState = type === "career" ? careerEmpty : skitEmpty;
    renderChat(container, emptyState, threadStore[type][currentIdx]?.messages || []);
  }

  async function switchThread(type, idx) {
    // Prevent re-entrant switching
    if (isLoadingThreads) return;
    isLoadingThreads = true;

    try {
      if (type === "career") activeCareerThreadIdx = idx;
      else activeSkitThreadIdx = idx;

      // Lazy load history from backend if not loaded yet
      await loadThreadHistory(type, idx);

      const container  = type === "career" ? careerMessages : skitMessages;
      const emptyState = type === "career" ? careerEmpty : skitEmpty;
      renderChat(container, emptyState, threadStore[type][idx].messages);
      renderThreadList(type);
    } finally {
      isLoadingThreads = false;
    }
  }

  function renderChat(container, emptyState, messages) {
    container.innerHTML = "";
    if (messages.length === 0) {
      container.appendChild(emptyState);
      emptyState.classList.remove("hidden");
      return;
    }
    emptyState.classList.add("hidden");
    messages.forEach((msg) => {
      container.appendChild(createMessageEl(msg.text, msg.role, msg.timestamp));
    });
    container.scrollTop = container.scrollHeight;
  }

  // Initialize — load thread lists only (no history loading on startup)
  async function initThreads() {
    await loadThreadsFromBackend("career", "career_assistant");
    await loadThreadsFromBackend("skit", "skit_assistant");
  }
  initThreads();

  // New thread buttons
  careerNewThreadBtn.addEventListener("click", () => {
    activeCareerThreadIdx = createLocalThread("career");
    renderThreadList("career");
    renderChat(careerMessages, careerEmpty, []);
  });

  skitNewThreadBtn.addEventListener("click", () => {
    activeSkitThreadIdx = createLocalThread("skit");
    renderThreadList("skit");
    renderChat(skitMessages, skitEmpty, []);
  });

  // ── Navigation ─────────────────────────────────────────
  function showPanel(panelId, linkEl) {
    navLinks.forEach((l) => l.classList.remove("active"));
    if (linkEl) linkEl.classList.add("active");

    panels.forEach((p) => p.classList.remove("active"));
    document.getElementById(panelId).classList.add("active");

    pageTitle.textContent = linkEl ? linkEl.textContent.trim() : panelId;

    // Show/hide thread section based on panel
    careerThreadsSection.classList.toggle("hidden", panelId !== "panel-career");
    skitThreadsSection.classList.toggle("hidden", panelId !== "panel-skit");
  }

  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      showPanel(link.dataset.panel, link);
    });
  });

  // ── Logout ─────────────────────────────────────────────
  logoutBtn.addEventListener("click", () => {
    if (!confirm("Are you sure you want to logout?")) return;
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    window.location.href = "index.html";
  });

  // ═══════════════════════════════════════════════════════
  //  CHAT
  // ═══════════════════════════════════════════════════════

  function formatTimestamp(ts) {
    if (!ts) return "";
    const d = (ts instanceof Date) ? ts : new Date(ts);
    if (isNaN(d.getTime())) return "";
    return d.toLocaleString("en-US", {
      month: "short", day: "numeric",
      hour: "numeric", minute: "2-digit",
      hour12: true,
    });
  }

  function createMessageEl(text, role, timestamp) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message", role);

    const avatar = document.createElement("div");
    avatar.classList.add("msg-avatar");
    avatar.textContent = role === "user" ? "U" : "AI";

    const content = document.createElement("div");
    content.classList.add("msg-content");

    const bubble = document.createElement("div");
    bubble.classList.add("msg-bubble");

    if (role === "assistant" && typeof marked !== "undefined") {
      bubble.innerHTML = marked.parse(text);
    } else {
      bubble.textContent = text;
    }

    content.appendChild(bubble);

    const tsStr = formatTimestamp(timestamp);
    if (tsStr) {
      const tsEl = document.createElement("span");
      tsEl.classList.add("msg-timestamp");
      tsEl.textContent = tsStr;
      content.appendChild(tsEl);
    }

    wrapper.appendChild(avatar);
    wrapper.appendChild(content);
    return wrapper;
  }

  function createTypingIndicator() {
    const el = document.createElement("div");
    el.classList.add("message", "assistant");
    el.innerHTML = `
      <div class="msg-avatar">AI</div>
      <div class="typing-indicator"><span></span><span></span><span></span></div>`;
    return el;
  }

  async function handleChat({ type, messagesContainer, input, sendBtn, emptyState, apiFn }) {
    const text = input.value.trim();
    if (!text) return;

    const threadIdx = type === "career" ? activeCareerThreadIdx : activeSkitThreadIdx;
    const thread = threadStore[type][threadIdx];
    const threadId = thread.id;

    // Update thread name from first message
    if (thread.messages.length === 0) {
      thread.name = text.length > 30 ? text.substring(0, 30) + "…" : text;
      renderThreadList(type);
    }

    // Hide empty state
    if (emptyState) emptyState.classList.add("hidden");

    // Save & render user message
    const now = new Date();
    thread.messages.push({ text, role: "user", timestamp: now });
    messagesContainer.appendChild(createMessageEl(text, "user", now));
    input.value = "";
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Typing indicator
    const typing = createTypingIndicator();
    messagesContainer.appendChild(typing);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    sendBtn.disabled = true;

    try {
      const data = await apiFn(text, username, threadId);
      typing.remove();
      const respTime = new Date();
      thread.messages.push({ text: data.response, role: "assistant", timestamp: respTime });
      messagesContainer.appendChild(createMessageEl(data.response, "assistant", respTime));
    } catch (err) {
      typing.remove();
      const errMsg = `⚠ Error: ${err.detail || "Something went wrong."}`;
      const errTime = new Date();
      thread.messages.push({ text: errMsg, role: "assistant", timestamp: errTime });
      messagesContainer.appendChild(createMessageEl(errMsg, "assistant", errTime));
    } finally {
      sendBtn.disabled = false;
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
      input.focus();
    }
  }

  // Career Assistant
  careerSendBtn.addEventListener("click", () =>
    handleChat({
      type: "career",
      messagesContainer: careerMessages,
      input: careerInput,
      sendBtn: careerSendBtn,
      emptyState: careerEmpty,
      apiFn: chatCareerAssistant,
    })
  );
  careerInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); careerSendBtn.click(); }
  });

  // SKIT Assistant
  skitSendBtn.addEventListener("click", () =>
    handleChat({
      type: "skit",
      messagesContainer: skitMessages,
      input: skitInput,
      sendBtn: skitSendBtn,
      emptyState: skitEmpty,
      apiFn: chatSkitAssistant,
    })
  );
  skitInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); skitSendBtn.click(); }
  });

  // ═══════════════════════════════════════════════════════
  //  RESUME UPLOAD & ANALYTICS DASHBOARD
  // ═══════════════════════════════════════════════════════

  fileInput.addEventListener("change", () => {
    fileNameDisplay.textContent = fileInput.files.length ? fileInput.files[0].name : "";
  });

  // Use a click handler on the button instead of form submit to guarantee no page refresh
  const resumeSubmitBtn = resumeForm.querySelector("button[type=submit]");

  resumeForm.addEventListener("submit", (e) => {
    e.preventDefault();
    e.stopPropagation();
    handleResumeSubmit();
    return false;
  });

  async function handleResumeSubmit() {
    const file = fileInput.files[0];
    if (!file) { alert("Please select a resume PDF."); return; }

    const jobRole    = document.getElementById("job-role").value.trim();
    const expLevel   = document.getElementById("experience-level").value;
    const companyReq = document.getElementById("company-requirements").value.trim();

    if (!jobRole) { alert("Please enter a Job Role."); return; }

    resumeAnalytics.classList.add("hidden");
    resumeLoader.classList.remove("hidden");
    resumeSubmitBtn.disabled = true;

    const resumeThreadId = `resume-${username}-${Date.now()}`;

    try {
      const data = await uploadResume(file, jobRole, expLevel, companyReq || null, username, resumeThreadId);
      renderAnalytics(data.response);
    } catch (err) {
      console.error("Resume upload error:", err);
      // Show error in analytics area
      resumeAnalytics.innerHTML = `
        <div class="detail-card" style="margin-bottom:20px;">
          <h4>❌ Error</h4>
          <div style="font-size:.9rem;line-height:1.75;color:var(--red);">${err.detail || "Failed to process resume. Please try again."}</div>
        </div>`;
      resumeAnalytics.classList.remove("hidden");
    } finally {
      resumeLoader.classList.add("hidden");
      resumeSubmitBtn.disabled = false;
    }
  }

  // ── Analytics Rendering ────────────────────────────────
  function renderAnalytics(responseStr) {
    let result;
    try {
      // The backend returns JSON as a string — may have markdown fences
      let cleaned = responseStr;
      cleaned = cleaned.replace(/```json\s*/gi, "").replace(/```\s*/g, "").trim();
      result = JSON.parse(cleaned);
    } catch (e) {
      // If not JSON, show as plain text fallback
      resumeAnalytics.innerHTML = `
        <div class="detail-card" style="margin-bottom:20px;">
          <h4>📋 Analysis Result</h4>
          <div style="font-size:.9rem;line-height:1.75;color:var(--text-secondary);white-space:pre-wrap;">${responseStr}</div>
        </div>`;
      resumeAnalytics.classList.remove("hidden");
      return;
    }

    // Reset the analytics HTML to the template (in case of repeated submissions)
    resumeAnalytics.innerHTML = buildAnalyticsHTML();

    // ATS Ring
    const score = result.ats_score || 0;
    const circumference = 2 * Math.PI * 52; // r=52
    const offset = circumference - (score / 100) * circumference;
    const ring = document.getElementById("ats-ring");
    const scoreNum = document.getElementById("ats-score-num");

    let ringColor = "#f87171"; // red
    if (score >= 70) ringColor = "#34d399"; // green
    else if (score >= 40) ringColor = "#fbbf24"; // orange

    // Trigger animation after a frame
    requestAnimationFrame(() => {
      ring.style.strokeDashoffset = offset;
      ring.style.stroke = ringColor;
    });
    scoreNum.textContent = score;

    // Sub-scores
    setBar("skill-bar", "skill-val", result.skill_match || 0);
    setBar("project-bar", "project-val", result.project_match || 0);
    setBar("experience-bar", "experience-val", result.experience_match || 0);
    setBar("format-bar", "format-val", result.format_match || 0);

    // Lists
    fillList("list-strengths", result.strengths || []);
    fillList("list-weaknesses", result.weaknesses || []);
    fillList("list-lags", result.resume_lags || []);
    fillList("list-corrections", result.corrections_required || []);

    // Keywords
    const kwContainer = document.getElementById("missing-keywords");
    kwContainer.innerHTML = "";
    (result.missing_keywords || []).forEach((kw) => {
      const tag = document.createElement("span");
      tag.classList.add("tag");
      tag.textContent = kw;
      kwContainer.appendChild(tag);
    });

    resumeAnalytics.classList.remove("hidden");
  }

  function buildAnalyticsHTML() {
    return `
      <!-- Score Header -->
      <div class="analytics-header">
        <div class="ats-score-ring">
          <svg viewBox="0 0 120 120">
            <circle class="ring-bg" cx="60" cy="60" r="52" />
            <circle id="ats-ring" class="ring-fg" cx="60" cy="60" r="52" />
          </svg>
          <div class="ats-score-value">
            <span id="ats-score-num">0</span>
            <small>/100</small>
          </div>
        </div>
        <div class="ats-score-label">ATS Score</div>
      </div>

      <!-- Sub-scores -->
      <div class="sub-scores">
        <div class="score-bar-card">
          <div class="score-bar-label"><span>Skill Match</span><span id="skill-val">0%</span></div>
          <div class="score-bar-track"><div id="skill-bar" class="score-bar-fill accent"></div></div>
        </div>
        <div class="score-bar-card">
          <div class="score-bar-label"><span>Project Match</span><span id="project-val">0%</span></div>
          <div class="score-bar-track"><div id="project-bar" class="score-bar-fill green"></div></div>
        </div>
        <div class="score-bar-card">
          <div class="score-bar-label"><span>Experience Match</span><span id="experience-val">0%</span></div>
          <div class="score-bar-track"><div id="experience-bar" class="score-bar-fill orange"></div></div>
        </div>
        <div class="score-bar-card">
          <div class="score-bar-label"><span>Format &amp; ATS</span><span id="format-val">0%</span></div>
          <div class="score-bar-track"><div id="format-bar" class="score-bar-fill pink"></div></div>
        </div>
      </div>

      <!-- Detail Cards -->
      <div class="analytics-grid">
        <div class="detail-card strengths">
          <h4>💪 Strengths</h4>
          <ul id="list-strengths"></ul>
        </div>
        <div class="detail-card weaknesses">
          <h4>⚠️ Weaknesses</h4>
          <ul id="list-weaknesses"></ul>
        </div>
        <div class="detail-card lags">
          <h4>🔻 Resume Lags</h4>
          <ul id="list-lags"></ul>
        </div>
        <div class="detail-card corrections">
          <h4>🛠️ Corrections Required</h4>
          <ul id="list-corrections"></ul>
        </div>
      </div>

      <!-- Missing Keywords -->
      <div class="detail-card keywords-card">
        <h4>🔑 Missing Keywords</h4>
        <div id="missing-keywords" class="keyword-tags"></div>
      </div>`;
  }

  function setBar(barId, valId, value) {
    setTimeout(() => {
      document.getElementById(barId).style.width = `${value}%`;
      document.getElementById(valId).textContent = `${value}%`;
    }, 150);
  }

  function fillList(listId, items) {
    const ul = document.getElementById(listId);
    ul.innerHTML = "";
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      ul.appendChild(li);
    });
  }
});
