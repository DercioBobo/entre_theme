"""Data for the Entre print formats (templates/print/*.html).

Every Entre print format follows the same pattern: letter head, party box,
dates on the left and title + number on the right, watermark, table,
totals and a repeating footer. The per-document differences (title, party,
which dates to show, ...) live in DOCS below, and the values that vary per
company come from Entre Theme Settings. The templates only lay things out.

Exposed to Jinja as entre_print_context(doc) through the `jinja` hook.
"""

import frappe
from frappe.utils import cint, flt, fmt_money, formatdate, in_words, money_in_words, strip_html

from entre_theme.api import get_settings_values, get_watermark

# label, field, kind ("date" or None), when ("return" / "not_return" / None)
DOCS = {
	"Quotation": {
		"title": "Cotação",
		"party_type": "Customer",
		"date": "transaction_date",
		"meta": [("Validade", "valid_till", "date", None)],
	},
	"Sales Order": {
		"title": "Encomenda",
		"party_type": "Customer",
		"date": "transaction_date",
		"meta": [
			("Entrega", "delivery_date", "date", None),
			("Requisição", "po_no", None, None),
		],
	},
	"Sales Invoice": {
		"title": "Factura",
		"return_title": "Nota de Crédito",
		"party_type": "Customer",
		"date": "posting_date",
		"meta": [
			("Vencimento", "due_date", "date", "not_return"),
			("Requisição", "po_no", None, None),
			("Ref. factura", "return_against", None, "return"),
		],
		"payment_status": True,
	},
	"Delivery Note": {
		"title": "Guia de Remessa",
		"return_title": "Guia de Devolução",
		"party_type": "Customer",
		"date": "posting_date",
		"meta": [
			("Requisição", "po_no", None, None),
			("Ref. guia", "return_against", None, "return"),
		],
		"delivery": True,
	},
	"Supplier Quotation": {
		"title": "Cotação de Fornecedor",
		"party_type": "Supplier",
		"date": "transaction_date",
		"meta": [("Validade", "valid_till", "date", None)],
	},
	"Purchase Order": {
		"title": "Ordem de Compra",
		"party_type": "Supplier",
		"date": "transaction_date",
		"meta": [("Entrega", "schedule_date", "date", None)],
	},
	"Purchase Invoice": {
		"title": "Factura de Fornecedor",
		"return_title": "Nota de Crédito de Fornecedor",
		"party_type": "Supplier",
		"date": "posting_date",
		"meta": [
			("Factura nº", "bill_no", None, None),
			("Data factura", "bill_date", "date", None),
			("Vencimento", "due_date", "date", "not_return"),
			("Ref. factura", "return_against", None, "return"),
		],
		"payment_status": True,
	},
	"Purchase Receipt": {
		"title": "Guia de Recepção",
		"return_title": "Guia de Devolução a Fornecedor",
		"party_type": "Supplier",
		"date": "posting_date",
		"meta": [
			("Guia do fornecedor", "supplier_delivery_note", None, None),
			("Ref. guia", "return_against", None, "return"),
		],
		"delivery": True,
	},
	"Payment Entry": {
		"title": "Nota de Pagamento",
		"date": "posting_date",
		"meta": [
			("Modo", "mode_of_payment", None, None),
			("Referência", "reference_no", None, None),
		],
	},
}

PARTY_LABELS = {"Customer": "Cliente", "Supplier": "Fornecedor", "Employee": "Funcionário"}


# ── Formatting ────────────────────────────────────────────────────────────────

def money(value):
	return fmt_money(flt(value), currency="")


def currency_label(currency):
	return "MT" if currency == "MZN" else (currency or "")


def amount_in_words(value, currency):
	"""Amount in words, without the currency code or "só".
	MZN: "Dez Mil Meticais", "Um Metical e Cinquenta Centavos",
	"Dois Milhões de Meticais e Um Centavo"."""
	if currency != "MZN":
		return money_in_words(value, currency).replace(" só.", "").replace(" only.", "")

	v = flt(value, 2)
	whole = int(v)
	cents = cint(flt((v - whole) * 100, 0))
	parts = []
	if whole:
		de = " de" if whole % 1000000 == 0 else ""
		parts.append(in_words(whole) + de + (" metical" if whole == 1 else " meticais"))
	if cents:
		parts.append(in_words(cents) + (" centavo" if cents == 1 else " centavos"))
	out = " e ".join(parts) if parts else "zero meticais"
	return out.title().replace(" E ", " e ").replace(" De ", " de ")


# ── Building blocks ───────────────────────────────────────────────────────────

def _title(doc, conf):
	if doc.get("select_print_heading"):
		return doc.select_print_heading
	if doc.get("is_return") and conf.get("return_title"):
		return conf["return_title"]
	return conf["title"]


def _meta(doc, conf, date_format):
	def fmt(value, kind):
		return formatdate(value, date_format) if kind == "date" else value

	rows = [{"label": "Data", "value": fmt(doc.get(conf["date"]), "date")}]
	is_return = bool(doc.get("is_return"))
	for label, field, kind, when in conf["meta"]:
		if when == "return" and not is_return:
			continue
		if when == "not_return" and is_return:
			continue
		value = doc.get(field)
		if value:
			rows.append({"label": label, "value": fmt(value, kind)})
	return rows


def _party_doc(party_type, party):
	if party_type in ("Customer", "Supplier") and party and frappe.db.exists(party_type, party):
		return frappe.get_cached_doc(party_type, party)
	return None


def _party(doc, conf, with_contacts=False):
	if doc.doctype == "Payment Entry":
		party_type, party = doc.party_type, doc.party
		name = doc.party_name or doc.party
	elif doc.doctype == "Quotation":
		party_type, party = doc.quotation_to, doc.party_name
		name = doc.customer_name or doc.party_name
	elif conf["party_type"] == "Customer":
		party_type, party = "Customer", doc.customer
		name = doc.customer_name or doc.customer
	else:
		party_type, party = "Supplier", doc.supplier
		name = doc.supplier_name or doc.supplier

	p = _party_doc(party_type, party)
	info = {
		"label": PARTY_LABELS.get(party_type, "Cliente"),
		"name": name or "",
		"address": doc.get("address_display") or "",
		"nuit": doc.get("nuit") or doc.get("tax_id") or (p.get("tax_id") if p else ""),
		"email": "",
		"phone": "",
	}
	if with_contacts and p:
		info["email"] = p.get("email") or p.get("email_id") or ""
		info["phone"] = p.get("telemovel") or p.get("mobile_no") or ""
	return info


def _watermark(v):
	if not v["print_show_watermark"]:
		return ""
	return v["print_watermark"] or get_watermark(v) or ""


def _footer(doc, v, letter_head_footer):
	note = (v["print_footer_note"] or "").strip()
	show_note = note and (not letter_head_footer or v["print_footer_note_everywhere"])
	return {
		"letter_head": letter_head_footer,
		"note": f"{note} / {doc.company}" if show_note and doc.get("company") else (note if show_note else ""),
		"page_numbers": bool(v["print_show_page_numbers"]),
	}


def _items(doc, v):
	group = (v["print_title_item_group"] or "").strip()
	use_description = v["print_item_text"] != "Nome do Artigo"
	rows, n = [], 0
	for item in doc.get("items") or []:
		description = item.get("description") or ""
		has_description = bool(strip_html(description).strip())

		if group and item.get("item_group") == group:
			# Section title row: only when it has text
			if has_description:
				rows.append({"group": True, "text": description})
			continue

		n += 1
		rows.append({
			"group": False,
			"n": n,
			"text": description if (use_description and has_description) else (item.get("item_name") or item.get("item_code")),
			"qty": item.get_formatted("qty"),
			"uom": item.get("uom") or "",
			"rate": money(item.get("rate")),
			"amount": money(item.get("amount")),
		})
	return rows


def _grand_total(doc):
	if doc.get("rounded_total") and not doc.get("disable_rounded_total"):
		return flt(doc.rounded_total)
	return flt(doc.grand_total)


def _totals(doc, v):
	rows = [{"label": v["print_items_total_label"] or "Total", "value": money(doc.total)}]
	if doc.get("discount_amount"):
		rows.append({"label": "Descontos comerciais", "value": "-" + money(doc.discount_amount)})
	rows.append({"label": "Sub-total", "value": money(doc.net_total)})

	taxes = [t for t in doc.get("taxes") or [] if t.get("tax_amount") or t.get("rate")]
	if len(taxes) <= 1:
		rate = flt(taxes[0].rate) if taxes else 0
		label = "IVA" + (f" ({rate:g}%)" if rate else "")
		rows.append({"label": label, "value": money(doc.total_taxes_and_charges)})
	else:
		for t in taxes:
			amount = flt(t.get("tax_amount_after_discount_amount") or t.get("tax_amount"))
			if t.get("add_deduct_tax") == "Deduct":
				amount = -amount
			label = t.get("description") or t.get("account_head")
			if t.get("rate"):
				label += f" ({flt(t.rate):g}%)"
			rows.append({"label": label, "value": money(amount)})

	if doc.get("rounding_adjustment") and not doc.get("disable_rounded_total"):
		rows.append({"label": "Arredondamento", "value": money(doc.rounding_adjustment)})

	rows.append({
		"label": f"Total ({currency_label(doc.currency)})",
		"value": money(_grand_total(doc)),
		"grand": True,
	})
	return rows


def _payment_status(doc, conf, v):
	"""None, {"full": True} or {"paid": ..., "due": ...} for submitted invoices."""
	if not (conf.get("payment_status") and v["print_show_payment_status"]):
		return None
	if doc.docstatus != 1 or doc.get("is_return"):
		return None
	total = _grand_total(doc)
	outstanding = flt(doc.get("outstanding_amount"))
	paid = total - outstanding
	if paid > 0 and outstanding > 0:
		return {"paid": money(paid), "due": money(outstanding)}
	if outstanding <= 0 and total > 0:
		return {"full": True}
	return None


def _terms(doc, v):
	terms = doc.get("terms") or ""
	if not v["print_show_terms"] or not strip_html(terms).strip():
		return None
	return {"title": doc.get("tc_name") or "Termos e Condições", "body": terms}


# ── Entry point ───────────────────────────────────────────────────────────────

def entre_print_context(doc, letter_head_footer=None):
	"""Everything an Entre print format needs, ready to print."""
	v = get_settings_values()
	conf = DOCS.get(doc.doctype) or DOCS["Sales Invoice"]
	date_format = v["print_date_format"]

	ctx = frappe._dict({
		"title": _title(doc, conf),
		"meta": _meta(doc, conf, date_format),
		"watermark": _watermark(v),
		"footer": _footer(doc, v, letter_head_footer),
	})

	if doc.doctype == "Payment Entry":
		ctx.party = _party(doc, conf, with_contacts=True)
		ctx.update(_payment(doc, date_format))
		return ctx

	show_prices = not conf.get("delivery") or bool(v["print_delivery_prices"])
	ctx.party = _party(doc, conf)
	ctx.subject = doc.get("invoice_title") or ""
	ctx.rows = _items(doc, v)  # not "items": that is dict.items() in Jinja
	ctx.show_prices = show_prices
	ctx.show_uom = bool(v["print_show_uom"])
	ctx.totals = _totals(doc, v) if show_prices else []
	ctx.in_words = amount_in_words(_grand_total(doc), doc.currency) if show_prices and v["print_show_in_words"] else ""
	ctx.payment_status = _payment_status(doc, conf, v)
	ctx.terms = _terms(doc, v)
	return ctx


def _payment(doc, date_format):
	is_receive = doc.payment_type == "Receive"
	currency = (doc.paid_to_account_currency if is_receive else doc.paid_from_account_currency) or "MZN"
	extra = []
	if doc.get("unallocated_amount"):
		label = "Saldo a favor do cliente" if is_receive else "Saldo adiantado"
		extra.append({"label": label, "value": money(doc.unallocated_amount)})
	for d in doc.get("deductions") or []:
		extra.append({"label": d.description or d.account, "value": money(d.amount)})

	return {
		"is_receive": is_receive,
		"currency": currency_label(currency),
		"pay_date": formatdate(doc.reference_date or doc.posting_date, date_format),
		"amount": money(doc.paid_amount),
		"amount_words": amount_in_words(doc.paid_amount, currency),
		"references": [
			{
				"idx": row.idx,
				"name": row.reference_name,
				"due_date": formatdate(row.due_date, date_format) if row.due_date else "",
				"total": money(row.total_amount),
				"outstanding": money(row.outstanding_amount),
				"allocated": money(row.allocated_amount),
			}
			for row in doc.get("references") or []
		],
		"total_allocated": money(doc.total_allocated_amount),
		"extra": extra,
	}
