"""The "Entre Theme" Print Style, generated from Entre Theme Settings.

wkhtmltopdf (Frappe's PDF engine) doesn't understand CSS variables, so the
print CSS can't read the settings at runtime like the desk does. Instead
templates/print/print_style.css is rendered with the values written in and
stored in a regular Print Style record, which Print Settings can select.
"""

import os

import frappe
from jinja2 import Environment

from entre_theme.api import get_settings_values

PRINT_STYLE = "Entre Theme"
TEMPLATE = os.path.join(os.path.dirname(__file__), "templates", "print", "print_style.css")

# Print fonts. Google fonts are imported; the rest are system fonts.
PRINT_GOOGLE_FONTS = {"Nunito Sans", "Inter", "Roboto", "Open Sans", "Lato"}
BASE_FONT_SIZE = 9  # the size the template was designed at


def render(values=None):
	v = values or get_settings_values()
	font = v["print_font_family"]
	scale = (v["print_font_size"] or BASE_FONT_SIZE) / BASE_FONT_SIZE

	def fs(px):
		return f"{round(px * scale, 2):g}px"

	font_url = ""
	if font in PRINT_GOOGLE_FONTS:
		font_url = (
			"https://fonts.googleapis.com/css2?family="
			+ font.replace(" ", "+")
			+ ":wght@400;600;700&display=swap"
		)

	with open(TEMPLATE, encoding="utf-8") as f:
		# Own environment: CSS must not be HTML-escaped.
		template = Environment(autoescape=False, keep_trailing_newline=True).from_string(f.read())

	return template.render(
		accent=v["print_accent"] or v["primary_color"],
		dark=v["print_dark_color"],
		font_stack=f"'{font}', Arial, sans-serif" if font != "Arial" else "Arial, sans-serif",
		font_url=font_url,
		fs=fs,
		watermark_opacity=v["print_watermark_opacity"],
		custom_css=v["print_custom_css"],
	)


def sync(values=None):
	"""Create / update the Print Style; make it the default if asked to.
	Runs on settings save and after migrate (template may have changed)."""
	if not frappe.db.exists("DocType", "Print Style"):
		return
	v = values or get_settings_values()
	if not v["manage_print_style"]:
		return

	css = render(v)
	if frappe.db.exists("Print Style", PRINT_STYLE):
		doc = frappe.get_doc("Print Style", PRINT_STYLE)
		if doc.css == css and not doc.disabled:
			css = None
		else:
			doc.css = css
			doc.disabled = 0
	else:
		doc = frappe.new_doc("Print Style")
		doc.print_style_name = PRINT_STYLE
		doc.css = css
	if css is not None:
		doc.flags.ignore_permissions = True
		doc.save()

	if v["set_default_print_style"]:
		frappe.db.set_single_value("Print Settings", "print_style", PRINT_STYLE)
