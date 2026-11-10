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

	var BODY_CLASSES = ["et-navbar-glass", "et-hide-counts", "et-sidebar-divider", "et-ws-watermark", "et-no-anim"];

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
	}

	function apply(payload) {
		if (!payload || !payload.vars) return;
		var root = document.documentElement;
		Object.keys(payload.vars).forEach(function (name) {
			root.style.setProperty(name, payload.vars[name]);
		});
		setBodyClasses(payload.body_classes);
		loadFont(payload);
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
