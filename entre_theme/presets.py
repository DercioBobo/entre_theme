"""Ready-made looks for Entre Theme Settings ("Predefinições").

A preset only sets look-and-feel fields: colours, fonts, shapes, which
parts of the desk are themed and the login style. Logos, images, texts
and print/print-format options are never touched.

Applying one fills the form (settings JS); nothing changes until the user
saves, so a preset can be reviewed and fine-tuned first.
"""

import frappe

from entre_theme.api import AREA_COLORS, DARK_COLORS, DEFAULTS

# Every per-area / per-style colour back to "follow the global colour"
_CLEAR_COLORS = {field: "" for field in AREA_COLORS if not field.startswith("print_")}
_CLEAR_COLORS.update({field: "" for field in DARK_COLORS})
_CLEAR_COLORS.update({
	"login_overlay_color": "",
	"login_panel_text": "",
	"login_vivid_second": "",
	"login_night_glow_color": "",
	"login_frame_bg": "",
	"login_duo_shape_1": "",
	"login_duo_shape_2": "",
	"login_aurora_color_1": "",
	"login_aurora_color_2": "",
	"login_type_bg": "",
	"login_type_color": "",
})

# All parts themed (the Entre look), as in DEFAULTS
_ALL_ON = {
	key: DEFAULTS[key]
	for key in (
		"theme_navbar", "theme_sidebar", "theme_workspace", "theme_lists", "theme_tabs", "theme_fields",
		"primary_buttons", "page_cards", "tint_blue_indicators", "fit_lists",
		"form_section_bars", "form_monogram", "form_timeline", "form_sidebar_tidy",
		"hide_shortcut_counts", "sidebar_divider", "show_workspace_watermark", "custom_login",
	)
}


def _look(**values):
	look = dict(_CLEAR_COLORS)
	look.update(_ALL_ON)
	look.update({
		"auto_text_on_accent": 1,
		"dark_color": "#111111",
		"surface_color": "#ffffff",
		"text_color": "#0f172a",
		"page_width": "Normal",
		"density": "Normal",
		"navbar_logo_position": "Padrão",
		"logo_size": "Padrão",
		"enable_animations": 1,
		"dark_theme": DEFAULTS["dark_theme"],
	})
	look.update(values)
	return look


PRESETS = {
	"Entre Laranja (original)": _look(
		primary_color="#ec932c",
		page_bg="#f5f6f8",
		border_color="#edeef1",
		font_family="Inter",
		border_radius="12px",
		navbar_style="Vidro",
		login_style="Clássico",
	),
	"Corporativo Azul": _look(
		primary_color="#2563eb",
		page_bg="#f3f5f9",
		border_color="#e6e9ef",
		text_color="#0b1220",
		dark_color="#0f172a",
		font_family="Inter",
		border_radius="8px",
		navbar_style="Sólida",
		login_style="Dividido",
		login_decoration="Pontos",
	),
	"Verde Natureza": _look(
		primary_color="#1f9d72",
		page_bg="#f2f6f4",
		border_color="#e3ebe7",
		text_color="#10231c",
		dark_color="#123328",
		font_family="Nunito Sans",
		border_radius="16px",
		navbar_style="Vidro",
		login_style="Moldura",
	),
	"Vibrante": _look(
		primary_color="#e11d48",
		page_bg="#f7f5f6",
		border_color="#efe8eb",
		font_family="Outfit",
		border_radius="16px",
		navbar_style="Vidro",
		login_style="Vívido",
		login_field_shape="Pílula",
		login_button_shape="Pílula",
	),
	"Noite Elegante": _look(
		primary_color="#8b5cf6",
		page_bg="#f5f4f9",
		border_color="#ebe8f3",
		text_color="#15121f",
		dark_color="#1e1633",
		font_family="Outfit",
		border_radius="12px",
		navbar_style="Vidro",
		login_style="Aurora",
		login_aurora_tone="Escuro",
		login_field_icons=1,
	),
	"Minimal Monocromático": _look(
		primary_color="#18181b",
		page_bg="#fafafa",
		border_color="#ececec",
		text_color="#09090b",
		dark_color="#09090b",
		font_family="Inter",
		border_radius="6px",
		navbar_style="Sólida",
		login_style="Minimalista",
		tint_blue_indicators=0,
		form_section_bars=0,
		show_workspace_watermark=0,
	),
	"Executivo Dourado": _look(
		primary_color="#b8862b",
		page_bg="#f6f4ef",
		border_color="#ece6da",
		text_color="#1c1a16",
		dark_color="#1c1a16",
		font_family="Lato",
		border_radius="10px",
		navbar_style="Sólida",
		login_style="Imersivo",
	),
	# Everything off: the desk and login exactly as Frappe draws them
	"Frappe Original (sem tema)": {
		**_CLEAR_COLORS,
		"theme_navbar": 0,
		"theme_sidebar": 0,
		"theme_workspace": 0,
		"theme_lists": 0,
		"theme_tabs": 0,
		"theme_fields": 0,
		"primary_buttons": "Escuro (Frappe)",
		"page_cards": 0,
		"tint_blue_indicators": 0,
		"fit_lists": 0,
		"hide_list_activity": 0,
		"form_section_bars": 0,
		"form_monogram": 0,
		"form_timeline": 0,
		"form_sidebar_tidy": 0,
		"hide_shortcut_counts": 0,
		"sidebar_divider": 0,
		"show_workspace_watermark": 0,
		"custom_login": 0,
		"font_family": "Padrão do Frappe",
		"navbar_logo_position": "Padrão",
		"logo_size": "Padrão",
		"page_width": "Normal",
		"density": "Normal",
	},
}


@frappe.whitelist()
def get_preset(name):
	"""Field values for one preset (the settings form fills them in)."""
	frappe.only_for("System Manager")
	if name not in PRESETS:
		frappe.throw(frappe._("Predefinição desconhecida: {0}").format(name))
	return PRESETS[name]
