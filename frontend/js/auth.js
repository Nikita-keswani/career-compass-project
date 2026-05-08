/**
 * auth.js — Login / Sign-up page logic
 */
document.addEventListener("DOMContentLoaded", () => {
  // Redirect to dashboard if already authenticated
  if (localStorage.getItem("access_token")) {
    window.location.href = "dashboard.html";
    return;
  }

  const loginTab  = document.getElementById("tab-login");
  const signupTab = document.getElementById("tab-signup");
  const loginForm  = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");
  const errorBox   = document.getElementById("auth-error");

  // ── Tab switching ──────────────────────────────────────
  loginTab.addEventListener("click", () => {
    loginTab.classList.add("active");
    signupTab.classList.remove("active");
    loginForm.classList.remove("hidden");
    signupForm.classList.add("hidden");
    hideError();
  });

  signupTab.addEventListener("click", () => {
    signupTab.classList.add("active");
    loginTab.classList.remove("active");
    signupForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
    hideError();
  });

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
  }
  function hideError() {
    errorBox.classList.add("hidden");
  }

  // ── Login ──────────────────────────────────────────────
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    const btn = loginForm.querySelector("button[type=submit]");
    btn.disabled = true;
    btn.textContent = "Signing in…";

    try {
      const username = document.getElementById("login-username").value.trim();
      const password = document.getElementById("login-password").value;
      const data = await loginUser(username, password);
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("username", username);
      window.location.href = "dashboard.html";
    } catch (err) {
      showError(err.detail || "Login failed. Please try again.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Sign In";
    }
  });

  // ── Sign-up ────────────────────────────────────────────
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    const btn = signupForm.querySelector("button[type=submit]");
    btn.disabled = true;
    btn.textContent = "Creating account…";

    try {
      const username  = document.getElementById("signup-username").value.trim();
      const password  = document.getElementById("signup-password").value;
      const firstname = document.getElementById("signup-firstname").value.trim();
      const lastname  = document.getElementById("signup-lastname").value.trim();

      if (!username || !password || !firstname || !lastname) {
        throw { detail: "All fields are required." };
      }

      const data = await signupUser(username, password, firstname, lastname);
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("username", username);
      alert("✅ Account created successfully! Welcome, " + firstname + "!");
      window.location.href = "dashboard.html";
    } catch (err) {
      showError(err.detail || "Signup failed. Please try again.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Create Account";
    }
  });
});
