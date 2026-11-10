"""Branded emails ("Emails" in Entre Theme Settings).

Frappe renders every outgoing email through "templates/emails/standard.html"
(frappe.email.email_body.get_formatted_html). Frappe's template loader
searches the most recently installed app first, so this app ships a file at
that same path (templates/emails/standard.html). It calls
entre_email_context() (a jinja method, see hooks.py) and, while "Emails com
a Marca" is off, simply includes Frappe's own template unchanged.
"""

import html
import json

import frappe

from entre_theme.api import accent_text, font_stack, get_navbar_logo, get_settings_values

EMAIL_STYLES = {"Cartão": "card", "Simples": "plain"}


def _radius(value):
	"""The theme radius, capped: big radii look odd in email clients."""
	try:
		px = int(str(value).replace("px", "").strip())
	except ValueError:
		px = 12
	return f"{max(0, min(px, 14))}px"


def entre_email_context(brand_logo=None):
	"""Look of the branded email for the template; {"enabled": 0} when off."""
	v = get_settings_values()
	preview = frappe.flags.get("entre_email_preview")
	if preview:
		v.update(preview)
	if not v["email_theme"]:
		return {"enabled": 0}

	accent = v["email_accent"] or v["primary_color"]
	logo = ""
	if v["email_show_logo"]:
		logo = v["email_logo"] or brand_logo or v["logo_url"] or get_navbar_logo(v)
	return {
		"enabled": 1,
		"style": EMAIL_STYLES.get(v["email_style"], "card"),
		"logo": logo,
		"accent": accent,
		"accent_text": accent_text(v, accent),
		"bg": v["email_bg"] or v["page_bg"],
		"surface": v["surface_color"],
		"text": v["text_color"],
		"border": v["border_color"],
		"font": font_stack(v["font_family"]).replace('"', "'"),
		"radius": _radius(v["border_radius"]),
		# Plain text from the settings: escaped, line breaks kept
		"footer_html": "<br>".join(html.escape(line) for line in (v["email_footer_text"] or "").strip().splitlines()),
	}


SAMPLE_MESSAGE = """
<p>Caro cliente,</p>
<p>Segue em anexo a <b>Factura ACC-SINV-2026-00042</b>, no valor de <b>12 450,00 MZN</b>,
com vencimento a 30 de Novembro.</p>
<p>Qualquer dúvida, estamos ao dispor.</p>
<p>Com os melhores cumprimentos,<br>Departamento Financeiro</p>
"""


@frappe.whitelist()
def preview_email(values=None):
	"""The settings form's "Pré-visualizar Email": a sample email rendered
	with the form's current (possibly unsaved) values."""
	frappe.only_for("System Manager")
	overrides = json.loads(values) if isinstance(values, str) else (values or {})
	overrides = {k: v for k, v in overrides.items() if k in get_settings_values()}
	overrides["email_theme"] = 1

	from frappe.email.email_body import get_formatted_html

	frappe.flags.entre_email_preview = overrides
	try:
		return get_formatted_html(
			"Factura ACC-SINV-2026-00042",
			SAMPLE_MESSAGE,
			footer='<div style="font-size:12px;color:#8d99a6">Enviado a partir do EntreCloud ERP</div>',
			with_container=True,
		)
	except Exception:
		# No outgoing email account, etc.: render the template directly
		return frappe.get_template("templates/emails/standard.html").render({
			"content": SAMPLE_MESSAGE,
			"subject": "Factura ACC-SINV-2026-00042",
			"with_container": True,
			"footer": "",
		})
	finally:
		frappe.flags.entre_email_preview = None
