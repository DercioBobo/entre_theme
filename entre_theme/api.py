import frappe

# Single source of truth for defaults. Used by the desk (boot + API),
# the login renderer and the install hook.
DEFAULTS = {
	"font_family": "Inter",
	"enable_animations": 1,
	"page_bg": "#f3f4f6",
	"border_radius": "8px",
	"card_bg": "#ffffff",
	"card_border": "#e5e7eb",
	"card_shadow": "0px 4px 6px rgba(0,0,0,0.05)",
	"input_bg": "#f9fafb",
	"input_border": "#d1d5db",
	"input_focus_ring": "#2B5CE6",
	"primary_color": "#2B5CE6",
	"primary_color_hover": "#1e40af",
	"primary_text_color": "#ffffff",
	"button_shadow": 0,
	"navbar_bg": "#1a1a2e",
	"sidebar_bg": "#16213e",
	"sidebar_active_bg": "#1f2937",
	"sidebar_text": "#9ca3af",
	"sidebar_text_active": "#ffffff",
}

TRANSITION = "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
BUTTON_SHADOW = "0px 4px 14px rgba(0,0,0,0.2)"

# Google-hosted fonts offered in the settings Select. Inter ships with Frappe's
# desk, but the standalone login page still needs to load it.
GOOGLE_FONTS = {"Inter", "Roboto", "Outfit", "Open Sans", "Lato"}


def get_settings_values():
	"""Return the raw settings merged over DEFAULTS (never raises)."""
	values = dict(DEFAULTS)
	values.update({"custom_css": "", "logo_url": "", "login_bg_url": "", "company_tagline": ""})
	try:
		settings = frappe.get_single("Entre Theme Settings")
	except Exception:
		# DocType may not exist yet during install / migrate.
		return values

	for key in values:
		value = settings.get(key)
		if key in ("enable_animations", "button_shadow"):
			if value is not None:
				values[key] = 1 if value else 0
		elif value:
			values[key] = value
	return values


def get_css_vars(values=None):
	"""Map settings to the exact CSS custom properties used by the stylesheets."""
	v = values or get_settings_values()
	return {
		"--font-family": f"'{v['font_family']}', system-ui, -apple-system, sans-serif",
		"--page-bg": v["page_bg"],
		"--border-radius": v["border_radius"],
		"--transition": TRANSITION if v["enable_animations"] else "none",
		"--card-bg": v["card_bg"],
		"--card-border": v["card_border"],
		"--card-shadow": v["card_shadow"],
		"--input-bg": v["input_bg"],
		"--input-border": v["input_border"],
		"--input-focus-ring": v["input_focus_ring"],
		"--primary-color": v["primary_color"],
		"--primary-hover": v["primary_color_hover"],
		"--primary-text": v["primary_text_color"],
		"--button-shadow": BUTTON_SHADOW if v["button_shadow"] else "none",
		"--navbar-bg": v["navbar_bg"],
		"--sidebar-bg": v["sidebar_bg"],
		"--sidebar-active-bg": v["sidebar_active_bg"],
		"--sidebar-text": v["sidebar_text"],
		"--sidebar-text-active": v["sidebar_text_active"],
	}


def get_font_url(font_family):
	if font_family not in GOOGLE_FONTS:
		return ""
	family = font_family.replace(" ", "+")
	return f"https://fonts.googleapis.com/css2?family={family}:wght@400;500;600;700&display=swap"


def get_theme_payload():
	values = get_settings_values()
	return {
		"vars": get_css_vars(values),
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
