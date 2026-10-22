(function () {
  "use strict";

  const storageKey = "alumni-theme";
  const root = document.documentElement;

  function setTheme(theme) {
    root.classList.toggle("theme-light", theme === "light");
    root.dataset.theme = theme;
    localStorage.setItem(storageKey, theme);
    const button = document.querySelector("[data-theme-toggle]");
    if (button) {
      button.setAttribute("aria-pressed", String(theme === "light"));
      button.setAttribute("aria-label", theme === "light" ? "Activer le thème sombre" : "Activer le thème clair");
      button.innerHTML = theme === "light" ? "☾ <span>Mode sombre</span>" : "☀ <span>Mode clair</span>";
    }
  }

  function createThemeToggle() {
    if (document.querySelector("[data-theme-toggle]")) return;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "theme-toggle";
    button.dataset.themeToggle = "true";
    button.addEventListener("click", function () {
      setTheme(root.classList.contains("theme-light") ? "dark" : "light");
    });
    document.body.appendChild(button);
  }

  function enableStepSwitcher() {
    document.querySelectorAll(".form-step").forEach(function (step) {
      step.setAttribute("tabindex", "0");
      step.setAttribute("role", "button");
      const activate = function () {
        document.querySelectorAll(".form-step").forEach((item) => item.classList.remove("is-active"));
        step.classList.add("is-active");
      };
      step.addEventListener("click", activate);
      step.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") { event.preventDefault(); activate(); }
      });
    });
  }

  function applyEigsiIdentity() {
    const emblem = '<svg class="eigsi-emblem" viewBox="0 0 72 48" aria-hidden="true"><path d="M4 35C19 35 22 12 38 12c8 0 12 5 13 10-7-5-12-5-17 2-7 10-15 13-30 11Z" fill="url(#eigsi-runtime-a)"/><path d="M14 43c14-1 17-17 29-17 8 0 12 4 15 8-9-4-13-2-19 4-6 6-14 7-25 5Z" fill="url(#eigsi-runtime-b)"/><path d="M25 7c10-2 18 1 23 8-8-2-13 1-17 8-4 7-9 10-17 10 8-5 10-11 11-17 0-4 0-6 0-9Z" fill="#4CAF50"/></svg>';
    const defs = '<svg width="0" height="0" aria-hidden="true"><defs><linearGradient id="eigsi-runtime-a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4CAF50"/><stop offset="1" stop-color="#0088CC"/></linearGradient><linearGradient id="eigsi-runtime-b" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#0088CC"/><stop offset="1" stop-color="#00529B"/></linearGradient></defs></svg>';
    document.body.insertAdjacentHTML("afterbegin", defs);
    document.querySelectorAll(".brand-mark").forEach(function (mark) {
      mark.textContent = "";
      mark.classList.add("brand-emblem-only");
      mark.insertAdjacentHTML("afterbegin", emblem);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    createThemeToggle();
    setTheme(localStorage.getItem(storageKey) || "dark");
    enableStepSwitcher();
    applyEigsiIdentity();
  });
})();
