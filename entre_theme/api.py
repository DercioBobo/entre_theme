import frappe

# Single source of truth for defaults. Used by the desk (boot + API),
# the login renderer, the print style and the install hook.
DEFAULTS = {
	# Aparência
	"primary_color": "#ec932c",
	"primary_text_color": "#ffffff",
	"page_bg": "#f5f6f8",
	"border_radius": "12px",
	"font_family": "Inter",
	"enable_animations": 1,
	"navbar_style": "Vidro",
	# Área de trabalho
	"hide_shortcut_counts": 1,
	"sidebar_divider": 1,
	"show_workspace_watermark": 1,
	# Impressão
	"manage_print_style": 1,
	"set_default_print_style": 0,
	"print_accent": "",
	"print_dark_color": "#111111",
	"print_font_family": "Nunito Sans",
	"print_font_size": 9,
	"print_watermark_opacity": 0.06,
}

# Fields with no default: empty means "not set".
OPTIONAL = ("custom_css", "print_custom_css", "logo_url", "login_bg_url", "company_tagline", "workspace_watermark")

CHECKS = {
	"enable_animations",
	"hide_shortcut_counts",
	"sidebar_divider",
	"show_workspace_watermark",
	"manage_print_style",
	"set_default_print_style",
}

TRANSITION = "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"

# Google-hosted fonts offered in the settings Select. Inter ships with Frappe's
# desk, but the standalone login page still needs to load it.
GOOGLE_FONTS = {"Inter", "Roboto", "Outfit", "Open Sans", "Lato", "Nunito Sans"}


def get_settings_values(settings=None):
	"""Return the raw settings merged over DEFAULTS (never raises).
	Pass the settings document when it's at hand (e.g. in on_update, where
	the cached copy may still be the old one)."""
	values = dict(DEFAULTS)
	values.update({key: "" for key in OPTIONAL})
	if settings is None:
		try:
			settings = frappe.get_cached_doc("Entre Theme Settings")
		except Exception:
			# DocType may not exist yet during install / migrate.
			return values

	for key in values:
		value = settings.get(key)
		if key in CHECKS:
			if value is not None:
				values[key] = 1 if value else 0
		elif value:
			values[key] = value
	return values


def get_watermark(v):
	return v["workspace_watermark"] or v["logo_url"]


def get_desk_vars(v):
	"""CSS custom properties read by public/css/theme.css."""
	watermark = get_watermark(v)
	return {
		"--et-accent": v["primary_color"],
		"--et-accent-text": v["primary_text_color"],
		"--et-page-bg-light": v["page_bg"],
		"--et-radius": v["border_radius"],
		"--et-font": f"'{v['font_family']}', system-ui, -apple-system, sans-serif",
		"--et-ws-watermark-img": f'url("{watermark}")' if watermark else "none",
	}


def get_body_classes(v):
	"""On/off parts of the desk theme, as classes on <body>."""
	classes = {
		"et-navbar-glass": v["navbar_style"] == "Vidro",
		"et-hide-counts": v["hide_shortcut_counts"],
		"et-sidebar-divider": v["sidebar_divider"],
		"et-ws-watermark": v["show_workspace_watermark"] and bool(get_watermark(v)),
		"et-no-anim": not v["enable_animations"],
	}
	return [name for name, on in classes.items() if on]


def get_css_vars(values=None):
	"""Variables used by the standalone login page (public/css/login.css)."""
	v = values or get_settings_values()
	accent = v["primary_color"]
	return {
		"--font-family": f"'{v['font_family']}', system-ui, -apple-system, sans-serif",
		"--page-bg": v["page_bg"],
		"--border-radius": v["border_radius"],
		"--transition": TRANSITION if v["enable_animations"] else "none",
		"--card-bg": "#ffffff",
		"--card-border": "rgba(15, 23, 42, 0.07)",
		"--card-shadow": "0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px -8px rgba(15, 23, 42, 0.12)",
		"--input-bg": "#f1f3f6",
		"--input-border": "transparent",
		"--input-focus-ring": accent,
		"--primary-color": accent,
		"--primary-hover": f"color-mix(in srgb, {accent} 85%, black)",
		"--primary-text": v["primary_text_color"],
		"--button-shadow": f"0 8px 20px -10px color-mix(in srgb, {accent} 60%, transparent)",
	}


def get_font_url(font_family):
	if font_family not in GOOGLE_FONTS:
		return ""
	family = font_family.replace(" ", "+")
	return f"https://fonts.googleapis.com/css2?family={family}:wght@400;500;600;700&display=swap"


def get_theme_payload():
	values = get_settings_values()
	return {
		"vars": get_desk_vars(values),
		"body_classes": get_body_classes(values),
		"font_family": values["font_family"],
		"font_url": get_font_url(values["font_family"]),
		"custom_css": values["custom_css"],
	}


@frappe.whitelist()
def get_theme_vars():
	"""Theme payload for the desk. Used by theme.js to refresh after saving settings."""
	return get_theme_payload()


def boot_session(bootinfo):
	"""boot_session hook: ship the theme with the desk boot so it applies with no extra request."""
	bootinfo.entre_theme = get_theme_payload()
