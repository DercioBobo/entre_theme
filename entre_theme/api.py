import frappe

# Single source of truth for defaults. Used by the desk (boot + API),
# the login renderer, the print style and the install hook.
DEFAULTS = {
	# Cores globais (each area can override them, see AREA_COLORS)
	"primary_color": "#ec932c",
	"primary_text_color": "#ffffff",
	"auto_text_on_accent": 1,
	"dark_color": "#111111",
	"page_bg": "#f5f6f8",
	"surface_color": "#ffffff",
	"text_color": "#0f172a",
	"border_color": "#edeef1",
	# Página de login (options per style: see get_login_theme)
	"custom_login": 1,
	"login_style": "Clássico",
	"login_overlay": 1,
	"login_overlay_opacity": 80,
	"login_panel_side": "Esquerda",
	"login_panel_width": "Médio",
	"login_decoration": "Anel",
	"login_panel_logo": 1,
	"login_logo_plate": 1,
	"login_panel_tagline": 1,
	"login_vivid_angle": "Diagonal",
	"login_glass_blur": "Médio",
	"login_glass_opacity": 58,
	"login_minimal_align": "Esquerda",
	"login_minimal_line": 1,
	"login_night_bg": "#0d0f13",
	"login_night_glow": 1,
	"login_headline": "Bem-vindo de volta",
	"login_subtext": "Entre com os seus dados para continuar a trabalhar.",
	"login_focus_logo_size": "Grande",
	"login_frame_illustration": 1,
	"login_duo_shapes": 1,
	"login_aurora_tone": "Escuro",
	"login_aurora_speed": "Lento",
	"login_type_style": "Contorno",
	"login_field_icons": 0,
	"login_field_shape": "Padrão",
	"login_button_shape": "Padrão",
	"login_notice_type": "Informação",
	"login_copyright": 0,
	# Modo escuro
	"dark_theme": "Tema com Cores Escuras",
	# Ecrã de carregamento
	"splash_screen": 1,
	"splash_logo_size": "Médio",
	"splash_indicator": "Barra",
	# Emails
	"email_theme": 0,
	"email_style": "Cartão",
	"email_show_logo": 1,
	# Site, portal e páginas de erro
	"web_theme": "Páginas de Erro e Mensagens",
	"web_error_logo": 1,
	"web_hide_chrome": 0,
	# Aparência
	"border_radius": "12px",
	"font_family": "Inter",
	"page_width": "Normal",
	"density": "Normal",
	"enable_animations": 1,
	"navbar_style": "Vidro",
	"navbar_logo_position": "Padrão",
	"logo_size": "Padrão",
	# Partes com o tema (off = exactly Frappe's look)
	"theme_navbar": 1,
	"theme_sidebar": 1,
	"theme_workspace": 1,
	"theme_lists": 1,
	"theme_tabs": 1,
	"theme_fields": 1,
	# Listas e formulários
	"primary_buttons": "Cor Principal",
	"page_cards": 1,
	"tint_blue_indicators": 1,
	"fit_lists": 1,
	"hide_list_activity": 0,
	# Formulários
	"form_section_bars": 1,
	"form_monogram": 1,
	"form_timeline": 1,
	"form_sidebar_tidy": 1,
	# Área de trabalho
	"hide_shortcut_counts": 1,
	"sidebar_divider": 1,
	"show_workspace_watermark": 1,
	# Impressão
	"manage_print_style": 1,
	"set_default_print_style": 0,
	"print_font_family": "Nunito Sans",
	"print_font_size": 9,
	"print_watermark_opacity": 0.06,
	# Formatos de impressão
	"manage_print_formats": 1,
	"set_default_print_formats": 0,
	"print_date_format": "dd-mm-yyyy",
	"print_item_text": "Descrição",
	"print_title_item_group": "Titulo",
	"print_show_uom": 1,
	"print_items_total_label": "Equipamentos/Serviços",
	"print_show_payment_status": 1,
	"print_show_in_words": 0,
	"print_show_terms": 1,
	"print_delivery_prices": 1,
	"print_show_watermark": 1,
	"print_show_page_numbers": 1,
	"print_footer_note": "Processado por computador / EntreCloud ERP",
	"print_footer_note_everywhere": 0,
}

# Per-area colours: empty means "use the global colour" (see resolve_colors).
AREA_COLORS = (
	"navbar_accent", "navbar_bg", "navbar_text",
	"sidebar_accent", "sidebar_text",
	"workspace_accent", "workspace_card_bg",
	"login_accent", "login_card_bg",
	"print_accent", "print_dark_color",
)

# Dark-mode colours: empty means the built-in dark shade (see theme.css).
DARK_COLORS = (
	"dark_primary_color", "dark_page_bg", "dark_surface_color",
	"dark_text_color", "dark_border_color", "dark_navbar_bg",
)

# Fields with no default: empty means "not set".
OPTIONAL = (
	"custom_css", "print_custom_css", "logo_url", "navbar_logo", "favicon", "login_bg_url",
	"company_tagline", "workspace_watermark", "print_watermark",
	# Login style colours that default to something derived (accent, auto)
	"login_overlay_color", "login_panel_text", "login_vivid_second", "login_night_glow_color",
	"login_frame_bg", "login_duo_shape_1", "login_duo_shape_2", "login_aurora_color_1",
	"login_aurora_color_2", "login_type_text", "login_type_bg", "login_type_color",
	"login_notice", "login_notice_until", "login_footer_links",
	"splash_logo", "splash_text", "splash_bg",
	"email_logo", "email_accent", "email_bg", "email_footer_text",
) + AREA_COLORS + DARK_COLORS

CHECKS = {
	"auto_text_on_accent",
	"form_section_bars",
	"form_monogram",
	"form_timeline",
	"form_sidebar_tidy",
	"custom_login",
	"theme_navbar",
	"theme_sidebar",
	"theme_workspace",
	"theme_lists",
	"theme_tabs",
	"theme_fields",
	"page_cards",
	"tint_blue_indicators",
	"fit_lists",
	"hide_list_activity",
	"enable_animations",
	"hide_shortcut_counts",
	"sidebar_divider",
	"show_workspace_watermark",
	"manage_print_style",
	"set_default_print_style",
	"manage_print_formats",
	"set_default_print_formats",
	"print_show_uom",
	"print_show_payment_status",
	"print_show_in_words",
	"print_show_terms",
	"print_delivery_prices",
	"print_show_watermark",
	"print_show_page_numbers",
	"print_footer_note_everywhere",
	"login_overlay",
	"login_panel_logo",
	"login_logo_plate",
	"login_panel_tagline",
	"login_minimal_line",
	"login_night_glow",
	"login_frame_illustration",
	"login_duo_shapes",
	"login_field_icons",
	"login_copyright",
	"splash_screen",
	"email_theme",
	"email_show_logo",
	"web_error_logo",
	"web_hide_chrome",
}

# Text fields with a default where empty is a real choice ("off"). Their
# defaults are written into the settings by install.seed_defaults, so an
# empty value here means the user cleared it.
ALLOW_EMPTY = {"print_title_item_group", "print_footer_note", "print_items_total_label", "login_subtext"}

TRANSITION = "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"

# Logo heights in px: (navbar, sidebar). "Padrão" leaves the navbar logo at
# Frappe's own size; the sidebar logo then uses the middle size.
LOGO_SIZES = {"Pequeno": (24, 32), "Médio": (32, 44), "Grande": (40, 56)}

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
		elif key in ALLOW_EMPTY:
			values[key] = value or ""
		elif value:
			values[key] = value
	return values


def get_watermark(v):
	return v["workspace_watermark"] or v["logo_url"]


FRAPPE_FONT = "Padrão do Frappe"
SYSTEM_STACK = "system-ui, -apple-system, 'Segoe UI', sans-serif"


def font_stack(font_family):
	if font_family == FRAPPE_FONT:
		return SYSTEM_STACK
	return f"'{font_family}', {SYSTEM_STACK}"


def get_navbar_logo(v):
	"""Empty: keep Frappe's own (Navbar Settings)."""
	return v["navbar_logo"] or v["logo_url"]


def sync_favicon(v):
	"""Write the favicon into Website Settings, which Frappe uses for the
	desk, the website and its own pages. Empty: Website Settings is left alone."""
	if not v["favicon"]:
		return
	try:
		if not frappe.get_meta("Website Settings").has_field("favicon"):
			return
		if frappe.db.get_single_value("Website Settings", "favicon") != v["favicon"]:
			frappe.db.set_single_value("Website Settings", "favicon", v["favicon"])
			frappe.clear_cache()
	except Exception:
		frappe.log_error(title="Entre Theme: could not set the favicon")


def _rgb(color):
	"""(r, g, b) 0-255 from #rgb / #rrggbb, or None."""
	c = (color or "").strip().lstrip("#")
	if len(c) == 3:
		c = "".join(ch * 2 for ch in c)
	if len(c) != 6:
		return None
	try:
		return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
	except ValueError:
		return None


def _luminance(rgb):
	def channel(value):
		value /= 255
		return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

	r, g, b = (channel(x) for x in rgb)
	return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color_a, color_b):
	"""WCAG contrast ratio (1 to 21), or None for colours it can't read."""
	a, b = _rgb(color_a), _rgb(color_b)
	if not a or not b:
		return None
	high, low = sorted((_luminance(a), _luminance(b)), reverse=True)
	return (high + 0.05) / (low + 0.05)


def text_on(color):
	"""White or near-black for text on the colour. White wins whenever it
	reaches 3:1 (WCAG for bold / large text, which button labels are), so
	brand colours keep white text unless they're light enough to need dark."""
	on_white = contrast_ratio(color, "#ffffff")
	if on_white is None:
		return "#ffffff"
	if on_white >= 3:
		return "#ffffff"
	return "#ffffff" if on_white >= contrast_ratio(color, "#111111") else "#111111"


def accent_text(v, accent):
	"""Text on the accent: automatic (black or white) or the chosen colour."""
	if v["auto_text_on_accent"]:
		return text_on(accent)
	return v["primary_text_color"]


def area_color(v, area_field, global_field):
	"""An area's own colour, or the global one when the area has none."""
	return v[area_field] or v[global_field]


def get_desk_vars(v):
	"""CSS custom properties read by public/css/theme.css.

	Area colours are passed as-is ("" when unset): theme.css falls back to
	the global colour, and theme.js removes a variable whose value is "".
	Backgrounds and text end in -light: Frappe's dark theme ignores them."""
	watermark = get_watermark(v)
	navbar_logo_h, sidebar_logo_h = LOGO_SIZES.get(v["logo_size"], (None, LOGO_SIZES["Médio"][1]))
	return {
		"--et-logo-h": f"{navbar_logo_h}px" if navbar_logo_h else "auto",
		"--et-sidebar-logo-h": f"{sidebar_logo_h}px",
		# Global
		"--et-primary": v["primary_color"],
		"--et-accent-text": accent_text(v, v["primary_color"]),
		"--et-page-bg-light": v["page_bg"],
		"--et-surface-light": v["surface_color"],
		"--et-text-light": v["text_color"],
		"--et-border-light": v["border_color"],
		# Areas
		"--et-navbar-accent": v["navbar_accent"],
		"--et-navbar-bg-light": v["navbar_bg"],
		"--et-navbar-text-light": v["navbar_text"],
		"--et-sidebar-accent": v["sidebar_accent"],
		"--et-sidebar-text-light": v["sidebar_text"],
		"--et-ws-accent": v["workspace_accent"],
		"--et-ws-card-bg-light": v["workspace_card_bg"],
		# Shape & type
		"--et-radius": v["border_radius"],
		"--et-font": "" if v["font_family"] == FRAPPE_FONT else font_stack(v["font_family"]),
		"--et-ws-watermark-img": f'url("{watermark}")' if watermark else "none",
	}


def get_dark_vars(v):
	"""Variables applied by theme.js only while Frappe's dark theme is on.
	Unset colours are "" (theme.css then uses its built-in dark shades)."""
	accent = v["dark_primary_color"] or v["primary_color"]
	return {
		"--et-primary": accent,
		"--et-accent-text": accent_text(v, accent),
		"--et-page-bg-dark": v["dark_page_bg"],
		"--et-surface-dark": v["dark_surface_color"],
		"--et-text-dark": v["dark_text_color"],
		"--et-border-dark": v["dark_border_color"],
		"--et-navbar-bg-dark": v["dark_navbar_bg"],
	}


def get_body_classes(v):
	"""On/off parts of the desk theme, as classes on <body>."""
	classes = {
		"et-navbar-glass": v["navbar_style"] == "Vidro",
		"et-logo-center": v["navbar_logo_position"] == "Centro",
		"et-logo-sidebar": v["navbar_logo_position"] == "Barra Lateral",
		"et-logo-sized": v["logo_size"] in LOGO_SIZES,
		"et-hide-counts": v["hide_shortcut_counts"],
		"et-sidebar-divider": v["sidebar_divider"],
		"et-ws-watermark": v["theme_workspace"] and v["show_workspace_watermark"] and bool(get_watermark(v)),
		"et-no-anim": not v["enable_animations"],
		"et-width-wide": v["page_width"] == "Larga",
		"et-width-full": v["page_width"] == "Total",
		"et-density-compact": v["density"] == "Compacta",
		"et-density-comfortable": v["density"] == "Confortável",
		"et-theme-navbar": v["theme_navbar"],
		"et-theme-sidebar": v["theme_sidebar"],
		"et-theme-workspace": v["theme_workspace"],
		"et-theme-lists": v["theme_lists"],
		"et-theme-tabs": v["theme_tabs"],
		"et-theme-fields": v["theme_fields"],
		"et-btn-accent": v["primary_buttons"] == "Cor Principal",
		"et-page-cards": v["page_cards"],
		"et-tint-blue": v["tint_blue_indicators"],
		"et-fit-lists": v["fit_lists"],
		"et-hide-list-activity": v["hide_list_activity"],
		"et-section-bars": v["form_section_bars"],
		"et-doc-monogram": v["form_monogram"],
		"et-timeline": v["form_timeline"],
		"et-form-sidebar": v["form_sidebar_tidy"],
	}
	return [name for name, on in classes.items() if on]


def get_css_vars(values=None):
	"""Variables used by the standalone login page (public/css/login.css)."""
	v = values or get_settings_values()
	accent = area_color(v, "login_accent", "primary_color")
	return {
		"--font-family": font_stack(v["font_family"]),
		"--page-bg": v["page_bg"],
		"--border-radius": v["border_radius"],
		"--transition": TRANSITION if v["enable_animations"] else "none",
		"--card-bg": area_color(v, "login_card_bg", "surface_color"),
		"--card-border": v["border_color"],
		"--card-shadow": "0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px -8px rgba(15, 23, 42, 0.12)",
		"--input-bg": "#f1f3f6",
		"--input-border": "transparent",
		"--input-focus-ring": accent,
		"--primary-color": accent,
		"--primary-hover": f"color-mix(in srgb, {accent} 85%, black)",
		"--primary-text": accent_text(v, accent),
		"--button-shadow": f"0 8px 20px -10px color-mix(in srgb, {accent} 60%, transparent)",
	}


# "Estilo da Página de Login" → body class et-login--<slug> (public/css/login.css)
LOGIN_STYLES = {
	"Clássico": "classic",
	"Dividido": "split",
	"Painel Lateral": "side",
	"Vívido": "vivid",
	"Vidro": "glass",
	"Minimalista": "minimal",
	"Noite": "night",
	"Imersivo": "immersive",
	"Foco": "focus",
	"Moldura": "frame",
	"Cartão Duplo": "duo",
	"Aurora": "aurora",
	"Tipográfico": "type",
}
GLASS_BLUR = {"Leve": "12px", "Médio": "24px", "Forte": "40px"}
FOCUS_LOGO = {"Médio": "56px", "Grande": "80px", "Enorme": "112px"}
AURORA_SPEED = {"Lento": "36s", "Normal": "22s", "Rápido": "12s"}


def _percent(value, default):
	try:
		return max(0, min(100, int(value)))
	except (TypeError, ValueError):
		return default


def get_login_theme(v):
	"""The selected login style and its options, as (slug, css vars, body classes).

	Colour options left empty fall back in CSS (to the login accent or an
	automatic shade), so they are only emitted when set."""
	style = LOGIN_STYLES.get(v["login_style"], "classic")
	css = {
		"--overlay-opacity": f"{_percent(v['login_overlay_opacity'], 80) / 100:g}",
		"--glass-blur": GLASS_BLUR.get(v["login_glass_blur"], "24px"),
		"--glass-alpha": f"{_percent(v['login_glass_opacity'], 58)}%",
		"--night-bg": v["login_night_bg"],
		"--focus-logo-h": FOCUS_LOGO.get(v["login_focus_logo_size"], "80px"),
		"--aurora-speed": AURORA_SPEED.get(v["login_aurora_speed"], "36s"),
	}
	for var, field in (
		("--overlay-color", "login_overlay_color"),
		("--panel-text-custom", "login_panel_text"),
		("--vivid-second-custom", "login_vivid_second"),
		("--glow-color", "login_night_glow_color"),
		("--frame-bg-custom", "login_frame_bg"),
		("--shape-1-custom", "login_duo_shape_1"),
		("--shape-2-custom", "login_duo_shape_2"),
		("--aurora-1-custom", "login_aurora_color_1"),
		("--aurora-2-custom", "login_aurora_color_2"),
		("--type-bg-custom", "login_type_bg"),
		("--type-color-custom", "login_type_color"),
	):
		if v[field]:
			css[var] = v[field]

	flags = {
		"et-overlay": v["login_overlay"],
		"et-panel-right": v["login_panel_side"] == "Direita",
		"et-panel-narrow": v["login_panel_width"] == "Estreito",
		"et-panel-wide": v["login_panel_width"] == "Largo",
		"et-deco-dots": v["login_decoration"] == "Pontos",
		"et-deco-none": v["login_decoration"] == "Nenhuma",
		"et-no-panel-logo": not v["login_panel_logo"],
		"et-no-logo-plate": not v["login_logo_plate"],
		"et-no-panel-tagline": not v["login_panel_tagline"],
		"et-vivid-vertical": v["login_vivid_angle"] == "Vertical",
		"et-vivid-horizontal": v["login_vivid_angle"] == "Horizontal",
		"et-minimal-center": v["login_minimal_align"] == "Centro",
		"et-no-topline": not v["login_minimal_line"],
		"et-no-glow": not v["login_night_glow"],
		"et-no-illustration": not v["login_frame_illustration"],
		"et-no-shapes": not v["login_duo_shapes"],
		"et-aurora-light": v["login_aurora_tone"] == "Claro",
		"et-aurora-still": v["login_aurora_speed"] == "Parado",
		"et-type-filled": v["login_type_style"] == "Preenchido",
		"et-icons": v["login_field_icons"],
		"et-field-pill": v["login_field_shape"] == "Pílula",
		"et-btn-pill": v["login_button_shape"] == "Pílula",
	}
	return style, css, [name for name, on in flags.items() if on]


def get_font_url(font_family):
	if font_family not in GOOGLE_FONTS:
		return ""
	family = font_family.replace(" ", "+")
	return f"https://fonts.googleapis.com/css2?family={family}:wght@400;500;600;700&display=swap"


def get_theme_payload():
	values = get_settings_values()
	return {
		"vars": get_desk_vars(values),
		"vars_dark": get_dark_vars(values),
		# "Frappe Escuro Original": no theme at all while the dark theme is on
		"dark_off": values["dark_theme"] == "Frappe Escuro Original",
		"body_classes": get_body_classes(values),
		"font_family": values["font_family"],
		"font_url": get_font_url(values["font_family"]),
		"custom_css": values["custom_css"],
		"app_logo": get_navbar_logo(values),
		"favicon": values["favicon"],
	}


@frappe.whitelist()
def get_theme_vars():
	"""Theme payload for the desk. Used by theme.js to refresh after saving settings."""
	return get_theme_payload()


def boot_session(bootinfo):
	"""boot_session hook: ship the theme with the desk boot so it applies with no extra request."""
	bootinfo.entre_theme = get_theme_payload()
