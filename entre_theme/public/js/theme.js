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

	// ── Notices ("Avisos no Sistema") ─────────────────────────────
	// The server sends this user's notices (roles already checked) with
	// start/end as timestamps; they are shown and hidden on time here, so
	// a notice that starts or ends while the desk is open needs no reload.
	// Closed notices are remembered per user, in this browser.
	var noticeData = null;
	var noticeTimer = null;

	function dismissKey() {
		var user = (window.frappe && frappe.session && frappe.session.user) || "";
		return "entre-notices-closed:" + user;
	}

	function closedNotices() {
		try {
			return JSON.parse(localStorage.getItem(dismissKey()) || "[]");
		} catch (e) {
			return [];
		}
	}

	function closeNotice(id) {
		var closed = closedNotices();
		if (closed.indexOf(id) === -1) closed.push(id);
		try {
			// Only ids of notices that still exist: the list never grows forever
			var live = ((noticeData && noticeData.items) || []).map(function (n) { return n.id; });
			localStorage.setItem(dismissKey(), JSON.stringify(closed.filter(function (c) {
				return live.indexOf(c) !== -1;
			})));
		} catch (e) { /* private mode: closes for this page only */ }
		renderNotices();
	}

	function noticeIcon(type) {
		var paths = {
			info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
			warning: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
			alert: '<circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>',
			success: '<circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6"/>'
		};
		return '<svg class="et-notice-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
			'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
			(paths[type] || paths.info) + "</svg>";
	}

	function buildNotice(n, canClose) {
		var el = document.createElement("div");
		el.className = "et-desk-notice et-desk-notice--" + n.type;
		el.setAttribute("role", n.type === "alert" || n.type === "warning" ? "alert" : "status");
		el.innerHTML = noticeIcon(n.type);
		var text = document.createElement("div");
		text.className = "et-desk-notice-text";
		text.textContent = n.message; // plain text: never HTML
		if (n.link) {
			var a = document.createElement("a");
			a.className = "et-desk-notice-link";
			a.href = n.link;
			a.textContent = n.link_label;
			if (/^https?:/.test(n.link)) {
				a.target = "_blank";
				a.rel = "noopener";
			}
			text.appendChild(document.createTextNode(" "));
			text.appendChild(a);
		}
		el.appendChild(text);
		if (canClose) {
			var btn = document.createElement("button");
			btn.type = "button";
			btn.className = "et-desk-notice-close";
			btn.setAttribute("aria-label", window.__ ? __("Fechar") : "Fechar");
			btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
				'stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>';
			btn.addEventListener("click", function () { closeNotice(n.id); });
			el.appendChild(btn);
		}
		return el;
	}

	function renderNotices() {
		var box = document.getElementById("et-desk-notices");
		var data = noticeData;
		var now = Date.now();
		var closed = data && data.dismiss ? closedNotices() : [];
		var items = ((data && data.items) || []).filter(function (n) {
			return (!n.start || n.start <= now) && (!n.end || n.end > now) && closed.indexOf(n.id) === -1;
		});
		if (!items.length) {
			if (box) box.remove();
			return;
		}
		var body = document.getElementById("body");
		if (!box) {
			box = document.createElement("div");
			box.id = "et-desk-notices";
		}
		box.className = "et-desk-notices et-desk-notices--" + data.style;
		// Bar: in the page flow, between the navbar and the page. Card: fixed corner.
		if (data.style === "bar" && body && body.parentNode) {
			if (box.nextSibling !== body) body.parentNode.insertBefore(box, body);
		} else if (box.parentNode !== document.body) {
			document.body.appendChild(box);
		}
		box.innerHTML = "";
		var list = box;
		if (data.style === "bar") {
			list = document.createElement("div");
			list.className = "container";
			box.appendChild(list);
		}
		items.forEach(function (n) { list.appendChild(buildNotice(n, data.dismiss)); });
	}

	function setupNotices(data) {
		noticeData = data && data.items && data.items.length ? data : null;
		if (noticeTimer) {
			clearInterval(noticeTimer);
			noticeTimer = null;
		}
		if (!document.body) {
			document.addEventListener("DOMContentLoaded", function () { setupNotices(data); });
			return;
		}
		renderNotices();
		// Start / end times: check every minute
		if (noticeData) noticeTimer = setInterval(renderNotices, 60000);
	}

	function apply(payload) {
		if (!payload || !payload.vars) return;
		setupNotices(payload.notices);
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
