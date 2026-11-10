"""Pages outside the desk's own boot: the loading screen and the website.

Both come through Frappe's `update_website_context` hook, which runs for
every page rendered from a template, `/app` included (after its own
get_context), so it can add to what Frappe already put in the context.

Loading screen ("Ecrã de Carregamento")
	app.html shows `.splash` (one <img>) until the desk boots, then removes
	it. The page head only links `include_css`, so the branded look is a
	small stylesheet written per site to /files and added to that list.

Website ("Site, Portal e Páginas de Erro")
	A <style> with the theme colours is appended to `head_html` and classes
	to `body_class`; public/css/web.css (web_include_css) reads them.
"""

import hashlib
import os

import frappe

from entre_theme.api import (
	FRAPPE_FONT,
	accent_text,
	font_stack,
	get_font_url,
	get_navbar_logo,
	get_settings_values,
)

SPLASH_FILE = "entre-theme-splash.css"
SPLASH_CACHE_KEY = "entre_theme_splash_version"
SPLASH_LOGO = {"Pequeno": 64, "Médio": 96, "Grande": 140}

WEB_OFF = "Desligado"
WEB_ALL = "Todo o Site e Portal"


def _css_string(text):
	"""A safe CSS string literal for `content:`."""
	text = " ".join((text or "").split())
	return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("<", "\\3c ") + '"'


def _css_url(url):
	return 'url("' + (url or "").replace("\\", "\\\\").replace('"', "%22") + '")'


# ── Loading screen ─────────────────────────────────────────────────


def splash_logo(v):
	return v["splash_logo"] or get_navbar_logo(v)


def build_splash_css(v):
	accent = v["primary_color"]
	bg = v["splash_bg"] or v["page_bg"]
	text = v["text_color"]
	dark_on = v["dark_theme"] != "Frappe Escuro Original"
	dark_bg = (v["dark_page_bg"] or "#161616") if dark_on else "#171717"
	dark_text = (v["dark_text_color"] or "#f3f4f6") if dark_on else "#f3f4f6"
	dark_accent = (v["dark_primary_color"] or accent) if dark_on else accent
	size = SPLASH_LOGO.get(v["splash_logo_size"], 96)
	font = font_stack(v["font_family"]) if v["font_family"] != FRAPPE_FONT else "inherit"
	indicator = v["splash_indicator"]

	css = [
		"/* Entre Theme: loading screen (written by entre_theme.website) */",
		".splash{position:fixed!important;inset:0;top:0!important;left:0!important;"
		"transform:none!important;-webkit-transform:none!important;z-index:2000;"
		"display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;"
		f"background:{bg};color:{text};font-family:{font};--et-splash-accent:{accent};}}",
		f".splash img{{order:1;width:auto!important;height:auto!important;max-width:min(70vw,{size * 3}px)!important;"
		f"max-height:{size}px!important;object-fit:contain;animation:et-splash-in .5s ease both;}}",
		"@keyframes et-splash-in{from{opacity:0;transform:translateY(6px) scale(.98)}to{opacity:1;transform:none}}",
	]
	if v["splash_text"]:
		css.append(
			f".splash::before{{content:{_css_string(v['splash_text'])};order:2;font-size:13px;"
			"letter-spacing:.01em;opacity:.65;}"
		)
	if indicator == "Barra":
		css += [
			".splash::after{content:\"\";order:3;width:140px;height:3px;border-radius:3px;"
			"background:linear-gradient(var(--et-splash-accent),var(--et-splash-accent)) no-repeat,"
			"color-mix(in srgb,var(--et-splash-accent) 16%,transparent);"
			"background-size:40% 100%,100% 100%;animation:et-splash-bar 1.2s ease-in-out infinite;}",
			"@keyframes et-splash-bar{from{background-position:-70% 0,0 0}to{background-position:170% 0,0 0}}",
		]
	elif indicator == "Círculo":
		css += [
			".splash::after{content:\"\";order:3;width:26px;height:26px;border-radius:50%;"
			"border:3px solid color-mix(in srgb,var(--et-splash-accent) 18%,transparent);"
			"border-top-color:var(--et-splash-accent);animation:et-splash-spin .8s linear infinite;}",
			"@keyframes et-splash-spin{to{transform:rotate(360deg)}}",
		]
	elif indicator == "Pulsar":
		css += [
			".splash img{animation:et-splash-in .5s ease both,et-splash-pulse 1.6s ease-in-out .5s infinite;}",
			"@keyframes et-splash-pulse{50%{opacity:.55;transform:scale(.96)}}",
		]
	dark = (
		f".splash{{background:{dark_bg};color:{dark_text};--et-splash-accent:{dark_accent};}}"
	)
	css += [
		# app.html renders data-theme from the user's choice: light, dark or automatic
		f'html[data-theme="dark"] {dark}',
		f'@media (prefers-color-scheme: dark){{html[data-theme="automatic"] {dark}}}',
		"@media (prefers-reduced-motion: reduce){.splash img,.splash::after{animation:none!important;}}",
	]
	return "\n".join(css) + "\n"


def _splash_path():
	return frappe.get_site_path("public", "files", SPLASH_FILE)


def sync_splash(v=None):
	"""Write the loading-screen stylesheet when it changed; return its version
	("" when the branded loading screen is off)."""
	v = v or get_settings_values()
	if not v["splash_screen"]:
		return ""
	css = build_splash_css(v)
	version = hashlib.md5(css.encode()).hexdigest()[:10]
	path = _splash_path()
	if frappe.cache.get_value(SPLASH_CACHE_KEY) != version or not os.path.exists(path):
		try:
			os.makedirs(os.path.dirname(path), exist_ok=True)
			with open(path, "w", encoding="utf-8") as f:
				f.write(css)
			frappe.cache.set_value(SPLASH_CACHE_KEY, version)
		except OSError:
			frappe.log_error(title="Entre Theme: could not write the loading screen stylesheet")
			return ""
	return version


def _update_desk(context, v):
	if not v["splash_screen"]:
		return  # Frappe's own loading screen
	version = sync_splash(v)
	if not version:
		return
	logo = splash_logo(v)
	if logo:
		context["splash_image"] = logo
	context["include_css"] = list(context.get("include_css") or []) + [f"/files/{SPLASH_FILE}?v={version}"]


# ── Website, portal and error pages ────────────────────────────────


def get_web_vars(v):
	logo = v["logo_url"] or get_navbar_logo(v)
	accent = v["primary_color"]
	return {
		"--et-primary": accent,
		"--et-accent-text": accent_text(v, accent),
		"--et-radius": v["border_radius"],
		"--et-page-bg": v["page_bg"],
		"--et-surface": v["surface_color"],
		"--et-text": v["text_color"],
		"--et-border": v["border_color"],
		"--et-font": "" if v["font_family"] == FRAPPE_FONT else font_stack(v["font_family"]),
		"--et-web-logo": _css_url(logo) if logo else "none",
	}


def get_web_classes(v):
	logo = v["logo_url"] or get_navbar_logo(v)
	classes = {
		"et-web": True,
		"et-web-all": v["web_theme"] == WEB_ALL,
		"et-web-error-logo": v["web_error_logo"] and bool(logo),
		"et-web-hide-chrome": v["web_hide_chrome"],
	}
	return [name for name, on in classes.items() if on]


def _update_web(context, v):
	if v["web_theme"] == WEB_OFF:
		return
	variables = "".join(f"{k}:{val};" for k, val in get_web_vars(v).items() if val)
	head = [f'<style id="entre-web-vars">:root{{{variables}}}</style>']
	font_url = get_font_url(v["font_family"]) if v["web_theme"] == WEB_ALL else ""
	if font_url:
		head.append(f'<link rel="stylesheet" href="{font_url}">')
	context["head_html"] = (context.get("head_html") or "") + "\n".join(head)
	context["body_class"] = " ".join(filter(None, [context.get("body_class") or ""] + get_web_classes(v)))


def _is_login(context):
	path = (context.get("path") or "").strip("/")
	try:
		path = path or frappe.local.request.path.strip("/")
	except Exception:
		pass
	return path == "login"


def update_website_context(context):
	"""update_website_context hook (every template page, /app included)."""
	try:
		v = get_settings_values()
		if "desk_theme" in context and "include_css" in context:
			_update_desk(context, v)  # /app: www/app.html (only app.py sets desk_theme)
		elif not _is_login(context):
			# Frappe's own login page (when the theme's is off) stays as it is
			_update_web(context, v)
	except Exception:
		# Never break a page over the theme
		frappe.log_error(title="Entre Theme: website context")
