/**
 * Entre Theme — desk runtime.
 *
 * Applies the theme from Entre Theme Settings: colours, radius and font as
 * CSS custom properties on <html>, on/off parts as et-* classes on <body>.
 * The payload arrives with the desk boot (api.boot_session), so no extra
 * request or asset rebuild is needed. All styling lives in the static
 * stylesheet (css/theme.css), which reads these variables and classes.
 */
(function () {
	"use strict";

	function setStyleTag(id, css) {
		var tag = document.getElementById(id);
		if (!css) {
			if (tag) tag.remove();
			return;
		}
		if (!tag) {
			tag = document.createElement("style");
			tag.id = id;
			document.head.appendChild(tag);
		}
		tag.textContent = css;
	}

	function loadFont(payload) {
		// Inter ships with Frappe's desk; load others on demand.
		var link = document.getElementById("entre-font");
		var url = payload.font_family !== "Inter" ? payload.font_url : "";
		if (!url) {
			if (link) link.remove();
			return;
		}
		if (!link) {
			link = document.createElement("link");
			link.id = "entre-font";
			link.rel = "stylesheet";
			document.head.appendChild(link);
		}
		if (link.href !== url) link.href = url;
	}

	var BODY_CLASSES = [
		"et-navbar-glass", "et-hide-counts", "et-sidebar-divider", "et-ws-watermark", "et-no-anim",
		"et-logo-center", "et-logo-sidebar", "et-logo-sized",
		"et-theme-navbar", "et-theme-sidebar", "et-theme-workspace", "et-theme-lists", "et-theme-tabs", "et-theme-fields",
		"et-btn-accent", "et-page-cards", "et-tint-blue", "et-fit-lists", "et-hide-list-activity",
		"et-section-bars", "et-doc-monogram", "et-timeline", "et-form-sidebar",
		"et-width-wide", "et-width-full", "et-density-compact", "et-density-comfortable"
	];

	// ── Logo in the sidebar ───────────────────────────────────────
	// Frappe builds a sidebar per page, asynchronously, so a copy of the
	// navbar logo is (re)inserted into the current page's sidebar whenever
	// the DOM settles. The navbar logo hides only while that copy is
	// visible (not on small screens, collapsed sidebars or pages without one).
	var logoObserver = null;
	var logoQueued = false;

	function currentSidebar() {
		var page = window.frappe && frappe.container && frappe.container.page;
		var scope = page && page.nodeType === 1 ? page : document;
		return scope.querySelector(".layout-side-section");
	}

	function syncSidebarLogo() {
		logoQueued = false;
		var body = document.body;
		var on = body.classList.contains("et-logo-sidebar");
		var navImg = document.querySelector(".navbar-home img");
		var side = on && navImg ? currentSidebar() : null;
		var visible = false;

		if (side) {
			var link = side.querySelector(":scope > .et-sidebar-logo");
			if (!link) {
				link = document.createElement("a");
				link.className = "et-sidebar-logo";
				link.href = "/app";
				link.appendChild(document.createElement("img"));
				side.insertBefore(link, side.firstChild);
			}
			var img = link.firstChild;
			if (img.getAttribute("src") !== navImg.getAttribute("src")) {
				img.setAttribute("src", navImg.getAttribute("src"));
				img.setAttribute("alt", navImg.getAttribute("alt") || "");
			}
			visible = side.offsetWidth > 0 && side.offsetHeight > 0;
		}
		body.classList.toggle("et-logo-moved", visible);
	}

	function queueLogoSync() {
		if (logoQueued) return;
		logoQueued = true;
		window.requestAnimationFrame(syncSidebarLogo);
	}

	function setupSidebarLogo(on) {
		if (!on) {
			if (logoObserver) {
				logoObserver.disconnect();
				logoObserver = null;
			}
			document.querySelectorAll(".et-sidebar-logo").forEach(function (el) { el.remove(); });
			if (document.body) document.body.classList.remove("et-logo-moved");
			return;
		}
		if (!logoObserver) {
			logoObserver = new MutationObserver(queueLogoSync);
			logoObserver.observe(document.body, {
				childList: true,
				subtree: true,
				attributes: true,
				attributeFilter: ["class", "style"]
			});
			window.addEventListener("resize", queueLogoSync);
		}
		queueLogoSync();
	}

	function setBodyClasses(classes) {
		var body = document.body;
		if (!body) {
			document.addEventListener("DOMContentLoaded", function () {
				setBodyClasses(classes);
			});
			return;
		}
		BODY_CLASSES.forEach(function (name) {
			body.classList.toggle(name, (classes || []).indexOf(name) !== -1);
		});
		setupSidebarLogo(body.classList.contains("et-logo-sidebar"));
	}

	// ── Logo & favicon ────────────────────────────────────────────
	// theme.js runs after frappe.boot is set but before the desk draws the
	// navbar, so patching boot.app_logo_url is enough on page load; the
	// <img> update covers a live refresh after saving the settings.
	var frappeLogo; // Frappe's own logo, restored when the setting is cleared

	function applyLogo(url) {
		if (!window.frappe || !frappe.boot) return;
		if (frappeLogo === undefined) frappeLogo = frappe.boot.app_logo_url || "";
		var src = url || frappeLogo;
		if (!src) return;
		frappe.boot.app_logo_url = src;
		document.querySelectorAll(".navbar-home img").forEach(function (img) {
			if (img.getAttribute("src") !== src) img.setAttribute("src", src);
		});
	}

	function applyFavicon(url) {
		if (!url) return; // the server-side favicon (Website Settings) stays
		document.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]').forEach(function (link) {
			if (link.getAttribute("href") !== url) link.setAttribute("href", url);
		});
	}

	// ── Dark mode ─────────────────────────────────────────────────
	// Frappe sets data-theme="dark" on <html> (also when "Automático"
	// resolves to dark). The theme then layers the dark colours over the
	// light ones, or, with "Frappe Escuro Original", steps aside entirely.
	var lastPayload = null;
	var appliedVars = [];
	var themeObserver = null;

	function isDark() {
		return document.documentElement.getAttribute("data-theme") === "dark";
	}

	function watchTheme() {
		if (themeObserver) return;
		themeObserver = new MutationObserver(function () {
			if (lastPayload) apply(lastPayload);
		});
		themeObserver.observe(document.documentElement, {
			attributes: true,
			attributeFilter: ["data-theme"]
		});
	}

	function apply(payload) {
		if (!payload || !payload.vars) return;
		lastPayload = payload;
		watchTheme();
		var root = document.documentElement;
		var off = isDark() && payload.dark_off;
		var vars = {};
		if (!off) {
			Object.keys(payload.vars).forEach(function (name) { vars[name] = payload.vars[name]; });
			if (isDark() && payload.vars_dark) {
				Object.keys(payload.vars_dark).forEach(function (name) { vars[name] = payload.vars_dark[name]; });
			}
		}
		// Drop variables from an earlier apply that no longer have a value
		appliedVars.forEach(function (name) {
			if (!vars[name]) root.style.removeProperty(name);
		});
		appliedVars = [];
		Object.keys(vars).forEach(function (name) {
			// "" = not set (e.g. an area colour that follows the global one)
			if (vars[name]) {
				root.style.setProperty(name, vars[name]);
				appliedVars.push(name);
			} else {
				root.style.removeProperty(name);
			}
		});
		// Branding (logo, favicon) stays in every mode
		applyLogo(payload.app_logo);
		applyFavicon(payload.favicon);
		setBodyClasses(off ? [] : payload.body_classes);
		loadFont(off ? {} : payload);
		setStyleTag("entre-custom-css", payload.custom_css);
	}

	function refresh() {
		return frappe.call({ method: "entre_theme.api.get_theme_vars" }).then(function (r) {
			apply(r.message);
		});
	}

	window.entre_theme = { apply: apply, refresh: refresh };

	if (window.frappe && frappe.boot && frappe.boot.entre_theme) {
		apply(frappe.boot.entre_theme);
	} else {
		// Boot not populated yet (or older session) — apply once the desk is ready.
		$(document).on("app_ready", function () {
			if (frappe.boot && frappe.boot.entre_theme) apply(frappe.boot.entre_theme);
			else refresh();
		});
	}
})();
