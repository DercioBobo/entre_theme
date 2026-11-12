"""The "Entre Theme" Letter Head, built from Entre Theme Settings.

The record holds only two Jinja calls, entre_letter_head(doc) and
entre_letter_head_footer(doc) (jinja methods, see hooks.py). Frappe renders a
Letter Head's header and footer as Jinja with {"doc": doc.as_dict()}
(frappe.www.printview.get_rendered_template), so every print format, the
app's and Frappe's own, gets the header of the document's company with the
current settings. Saving the settings never has to rewrite it.

Styles are inline: Frappe's standard print formats don't load the Entre
print style, and wkhtmltopdf renders the PDF header on its own.
"""

import html

import frappe
from frappe.utils import cint
from markupsafe import Markup

from entre_theme.api import area_color, get_settings_values

LETTER_HEAD = "Entre Theme"
HEADER_CALL = "{{ entre_letter_head(doc) }}"
FOOTER_CALL = "{{ entre_letter_head_footer(doc) }}"

FOOTER_BANKS = {"Contas Bancárias", "Contas Bancárias e Texto"}
FOOTER_TEXT = {"Texto", "Contas Bancárias e Texto"}


# ── Data ──────────────────────────────────────────────────────────────────────

def _values():
	v = get_settings_values()
	preview = frappe.flags.get("entre_letter_head_preview")
	if preview:
		v.update(preview)
	return v


def _company_name(doc):
	company = (doc or {}).get("company") if doc else None
	if company and frappe.db.exists("Company", company):
		return company
	try:
		company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")
	except Exception:
		company = None
	if company and frappe.db.exists("Company", company):
		return company
	return frappe.db.get_value("Company", {}, "name") if frappe.db.exists("DocType", "Company") else None


def _company(name):
	if not name:
		return frappe._dict()
	return frappe.get_cached_doc("Company", name)


def _address(company):
	"""The company's address: its primary one first."""
	if not company or not frappe.db.exists("DocType", "Address"):
		return []
	rows = frappe.get_all(
		"Address",
		filters=[
			["Dynamic Link", "link_doctype", "=", "Company"],
			["Dynamic Link", "link_name", "=", company],
			["Address", "disabled", "=", 0],
		],
		fields=["address_line1", "address_line2", "city", "country", "phone", "email_id"],
		# Qualified: the Dynamic Link join also has a "modified" column
		order_by="`tabAddress`.is_primary_address desc, `tabAddress`.modified desc",
		limit=1,
	)
	return rows[0] if rows else frappe._dict()


def _banks(company):
	if not company or not frappe.db.exists("DocType", "Bank Account"):
		return []
	filters = {"company": company, "is_company_account": 1}
	if frappe.get_meta("Bank Account").has_field("disabled"):
		filters["disabled"] = 0
	return frappe.get_all(
		"Bank Account",
		filters=filters,
		fields=["bank", "account_name", "bank_account_no", "iban", "branch_code"],
		order_by="is_default desc, creation asc",
		limit=3,
	)


def _lines(text):
	return [line.strip() for line in (text or "").splitlines() if line.strip()]


def get_details(v, company_name):
	"""The lines of the header: name, address, tax id, contacts, extra text."""
	company = _company(company_name)
	address = _address(company_name) if v["lh_show_address"] else {}
	out = {
		"name": (company.get("company_name") or company_name or "") if v["lh_show_company_name"] else "",
		"lines": [],
		"contacts": [],
	}
	if address:
		street = ", ".join(x for x in (address.get("address_line1"), address.get("address_line2")) if x)
		place = ", ".join(x for x in (address.get("city"), address.get("country")) if x)
		out["lines"] += [x for x in (street, place) if x]
	if v["lh_show_tax_id"] and company.get("tax_id"):
		out["lines"].append(f"{v['lh_tax_label'] or 'NUIT'}: {company.tax_id}")
	if v["lh_show_contacts"]:
		phone = company.get("phone_no") or (address or {}).get("phone")
		email = company.get("email") or (address or {}).get("email_id")
		out["contacts"] = [x for x in (f"Tel: {phone}" if phone else "", f"Email: {email}" if email else "",
			company.get("website") or "") if x]
	out["extra"] = _lines(v["lh_extra_text"])
	return out


# ── HTML ──────────────────────────────────────────────────────────────────────

def _e(value):
	return html.escape(str(value or ""))


def render_header(v, company_name):
	accent = area_color(v, "print_accent", "primary_color")
	logo = v["lh_logo"] or v["logo_url"]
	height = max(24, min(cint(v["lh_logo_height"]) or 64, 160))
	d = get_details(v, company_name)
	side = v["lh_layout"] == "Logótipo ao Lado dos Dados"

	text = ""
	if d["name"]:
		text += f'<div class="lh-name" style="font-size:11pt;font-weight:700;color:#111111;margin-bottom:2px">{_e(d["name"])}</div>'
	line_style = "font-size:8.5pt;line-height:1.5;color:#374151"
	for line in d["lines"]:
		text += f'<div class="lh-line" style="{line_style}">{_e(line)}</div>'
	if d["contacts"]:
		# Each contact stays whole when the line wraps
		joined = " · ".join(f'<span style="white-space:nowrap">{_e(c)}</span>' for c in d["contacts"])
		text += f'<div class="lh-line" style="{line_style}">{joined}</div>'
	for line in d["extra"]:
		text += f'<div class="lh-line" style="{line_style}">{_e(line)}</div>'
	img = (
		f'<img class="lh-logo" src="{_e(logo)}" alt="" style="display:block;height:{height}px;width:auto;'
		f'max-width:100%;{"" if side else "margin-bottom:10px;"}">'
		if logo else ""
	)

	if side and img and text:
		body = (
			'<table style="border-collapse:collapse;width:auto"><tr>'
			f'<td style="padding:0 16px 0 0;vertical-align:middle;border:0">{img}</td>'
			f'<td style="padding:0;vertical-align:middle;border:0">{text}</td>'
			"</tr></table>"
		)
	else:
		body = img + text

	line = f'<div style="margin-top:12px;height:3px;width:56px;background:{_e(accent)}"></div>' if v["lh_accent_line"] else ""
	return f'<div class="lh entre-lh" style="padding-top:16px;max-width:50%">{body}{line}</div>'


def _bank_cell(bank, accent):
	iban = bank.get("iban") or ""
	iban_label = "IBAN" if iban[:2].isalpha() else "NIB"
	rows = [
		f'<p class="bank-name" style="margin:0 0 3px;font-size:9pt;font-weight:700;color:#111111">{_e(bank.get("bank") or bank.get("account_name"))}</p>'
	]
	for label, value in (("Conta", bank.get("bank_account_no")), (iban_label, iban), ("Balcão", bank.get("branch_code"))):
		if value:
			rows.append(f'<p style="margin:0"><span class="k" style="color:#4b5563">{label}:</span> {_e(value)}</p>')
	return (
		f'<td style="vertical-align:top;padding:7px 10px;font-size:8pt;color:#111827;'
		f'border:1px solid #e5e7eb;border-top:2px solid {_e(accent)}">{"".join(rows)}</td>'
	)


def render_footer(v, company_name):
	accent = area_color(v, "print_accent", "primary_color")
	parts = []
	if v["lh_footer"] in FOOTER_BANKS:
		banks = _banks(company_name)
		if banks:
			title = _e(v["lh_bank_title"])
			cells = "".join(_bank_cell(b, accent) for b in banks)
			parts.append(
				'<div class="bank-block" style="margin-top:24px;page-break-inside:avoid">'
				+ (f'<div class="bank-title" style="font-weight:700;color:#111111;margin-bottom:6px;font-size:9pt">{title}</div>' if title else "")
				+ f'<table class="bank-table" style="width:100%;border-collapse:collapse"><tr>{cells}</tr></table></div>'
			)
	if v["lh_footer"] in FOOTER_TEXT:
		lines = _lines(v["lh_footer_text"])
		if lines:
			parts.append(
				'<div style="margin-top:10px;font-size:8pt;line-height:1.5;color:#4b5563;text-align:center">'
				+ "<br>".join(_e(line) for line in lines) + "</div>"
			)
	return "".join(parts)


# ── Jinja methods (called from the Letter Head record) ───────────────────────

def entre_letter_head(doc=None):
	try:
		v = _values()
		return Markup(render_header(v, _company_name(doc)))
	except Exception:
		frappe.log_error(title="Entre Theme: letter head")
		return ""


def entre_letter_head_footer(doc=None):
	try:
		v = _values()
		return Markup(render_footer(v, _company_name(doc)))
	except Exception:
		frappe.log_error(title="Entre Theme: letter head footer")
		return ""


# ── The record ────────────────────────────────────────────────────────────────

def _unset_default(name):
	"""Frappe makes a letter head the default when none is: undo that unless asked."""
	if frappe.db.get_value("Letter Head", name, "is_default"):
		frappe.db.set_value("Letter Head", name, "is_default", 0)
		if frappe.defaults.get_global_default("letter_head") == name:
			frappe.defaults.clear_default("letter_head")
			frappe.defaults.clear_default("default_letter_head_content")
		frappe.clear_cache()


def sync(values=None):
	"""Create / update the "Entre Theme" Letter Head when "Criar Cabeçalho" is
	on. Off: the record is left as it is (never deleted: it may be in use)."""
	if not frappe.db.exists("DocType", "Letter Head"):
		return
	v = values or get_settings_values()
	if not v["lh_manage"]:
		if frappe.db.exists("Letter Head", LETTER_HEAD):
			_unset_default(LETTER_HEAD)
		return

	want_default = bool(v["lh_default"])
	if frappe.db.exists("Letter Head", LETTER_HEAD):
		doc = frappe.get_doc("Letter Head", LETTER_HEAD)
	else:
		doc = frappe.new_doc("Letter Head")
		doc.letter_head_name = LETTER_HEAD
		# before_insert forces source = "Image"; with no image validate only
		# shows a message, so insert quietly and switch to HTML below
		doc.flags.ignore_permissions = True
		muted = frappe.flags.mute_messages
		frappe.flags.mute_messages = True
		try:
			doc.insert()
		finally:
			frappe.flags.mute_messages = muted

	fields = {
		"source": "HTML",
		"footer_source": "HTML",
		"content": HEADER_CALL,
		"footer": FOOTER_CALL,
		"disabled": 0,
	}
	if want_default:
		fields["is_default"] = 1
	if any(doc.get(k) != val for k, val in fields.items()):
		doc.update(fields)
		doc.flags.ignore_permissions = True
		doc.save()

	if not want_default:
		_unset_default(LETTER_HEAD)


@frappe.whitelist()
def preview_letter_head(values=None, company=None):
	"""The settings form's "Pré-visualizar Cabeçalho", with unsaved values."""
	import json

	frappe.only_for("System Manager")
	overrides = json.loads(values) if isinstance(values, str) else (values or {})
	overrides = {k: val for k, val in overrides.items() if k in get_settings_values()}
	frappe.flags.entre_letter_head_preview = overrides
	try:
		v = _values()
		name = company if company and frappe.db.exists("Company", company) else _company_name(None)
		return {
			"company": name or "",
			"header": render_header(v, name),
			"footer": render_footer(v, name),
		}
	finally:
		frappe.flags.entre_letter_head_preview = None
