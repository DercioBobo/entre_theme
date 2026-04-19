/**
 * login.js — Entre Theme
 *
 * Loaded via web_include_js on ALL Frappe web pages. Guard immediately so
 * none of the logic below runs outside the custom login page.
 *
 * The guard checks for `.et-login-wrapper`, which is the root element unique
 * to our login.html template. If it's not present, we bail instantly.
 */
if (!document.querySelector(".et-login-wrapper")) {
	// Not our login page — do nothing.
	// This is intentional: Frappe's web_include_js has no per-route filtering.
} else {
	window.addEventListener("DOMContentLoaded", function () {
		// ── Password visibility toggle ─────────────────────────────────────────
		var toggleBtn = document.getElementById("et-toggle-pwd");
		var pwdInput  = document.getElementById("login_password");
		var eyeOpen   = document.getElementById("et-eye-open");
		var eyeClosed = document.getElementById("et-eye-closed");

		if (toggleBtn && pwdInput) {
			toggleBtn.addEventListener("click", function () {
				var isHidden = pwdInput.getAttribute("type") === "password";
				pwdInput.setAttribute("type", isHidden ? "text" : "password");
				eyeOpen.style.display   = isHidden ? "none" : "";
				eyeClosed.style.display = isHidden ? ""     : "none";
			});
		}

		// ── Input focus classes (for potential animated-label extensions) ──────
		var inputs = document.querySelectorAll(".et-input");
		inputs.forEach(function (input) {
			input.addEventListener("focus", function () {
				var group = input.closest(".et-field-group");
				if (group) group.classList.add("et-focused");
			});
			input.addEventListener("blur", function () {
				var group = input.closest(".et-field-group");
				if (group && !input.value) group.classList.remove("et-focused");
			});
		});
	});
}
