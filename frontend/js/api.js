/**
 * api.js — Centralised API communication layer
 */
const API_BASE = window.ENV?.API_BASE_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("access_token");
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${getToken()}`,
  };
}

/**
 * Generic JSON POST
 */
async function apiPost(path, body = {}, useAuth = true) {
  const headers = useAuth ? authHeaders() : { "Content-Type": "application/json" };
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw { status: res.status, detail: data.detail || "Unknown error" };
  return data;
}

/**
 * Multipart POST (for file uploads)
 */
async function apiPostForm(path, formData) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${getToken()}` },
    body: formData,
  });
  const data = await res.json();
  if (!res.ok) throw { status: res.status, detail: data.detail || "Unknown error" };
  return data;
}

/* ─── Auth ─────────────────────────────────────────────── */
async function loginUser(username, password) {
  return apiPost("/user/login", { username, enc_password: password }, false);
}

async function signupUser(username, password, firstname, lastname) {
  return apiPost(
    "/user/signup",
    { username, enc_password: password, firstname, lastname },
    false
  );
}

/* ─── Assistants ───────────────────────────────────────── */
async function chatCareerAssistant(userInput, userId, threadId) {
  return apiPost("/assistant/chat_career_assistant", {
    user_input: userInput,
    user_id: userId,
    thread_id: threadId,
  });
}

async function chatSkitAssistant(userInput, userId, threadId) {
  return apiPost("/assistant/chat_skit_assistant", {
    user_input: userInput,
    user_id: userId,
    thread_id: threadId,
  });
}

/* ─── Threads ──────────────────────────────────────────── */
async function listThreads(userId, chatType) {
  return apiPost("/threads/list", { user_id: userId, chat_type: chatType });
}

async function getThreadHistory(userId, threadId, chatType) {
  return apiPost("/threads/history", {
    user_id: userId,
    thread_id: threadId,
    chat_type: chatType,
  });
}

async function deleteThread(userId, threadId, chatType) {
  return apiPost("/threads/delete", {
    user_id: userId,
    thread_id: threadId,
    chat_type: chatType,
  });
}

/* ─── Resume ───────────────────────────────────────────── */
async function uploadResume(file, jobRole, experienceLevel, companyRequirements, userId, threadId) {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("job_role", jobRole);
  fd.append("experience_level", experienceLevel);
  if (companyRequirements) fd.append("company_requirements", companyRequirements);
  fd.append("user_id", userId);
  fd.append("thread_id", threadId);
  return apiPostForm("/resume/upload_resume", fd);
}
