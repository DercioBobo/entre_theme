"""The "Entre …" Print Formats, created and kept up to date by the app.

Each record is a one-line include of a template in templates/print/, so the
layout lives in the app (one pattern for every document) and the options
live in Entre Theme Settings. Each format also carries the rendered print
CSS, so it looks right whatever Print Style is selected in Print Settings.

To customise one beyond the settings, duplicate it: these records are
rewritten on every settings save and `bench migrate`.
"""

import frappe

from entre_theme import print_style
from entre_theme.api import get_settings_values

MODULE = "Entre Theme"

# doctype: (print format name, template)
FORMATS = {
	"Quotation": ("Entre Cotação", "transaction.html"),
	"Sales Order": ("Entre Encomenda", "transaction.html"),
	"Sales Invoice": ("Entre Factura", "transaction.html"),
	"Delivery Note": ("Entre Guia de Remessa", "transaction.html"),
	"Supplier Quotation": ("Entre Cotação de Fornecedor", "transaction.html"),
	"Purchase Order": ("Entre Ordem de Compra", "transaction.html"),
	"Purchase Invoice": ("Entre Factura de Fornecedor", "transaction.html"),
	"Purchase Receipt": ("Entre Guia de Recepção", "transaction.html"),
	"Payment Entry": ("Entre Recibo", "payment_entry.html"),
}


def _html(template):
	return (
		"{#- Managed by Entre Theme: rewritten on settings save and migrate.\n"
		"    Duplicate this format to customise it. -#}\n"
		f'{{% include "entre_theme/templates/print/{template}" %}}\n'
	)


def sync(values=None):
	if not frappe.db.exists("DocType", "Print Format"):
		return
	v = values or get_settings_values()
	if not v["manage_print_formats"]:
		return

	css = print_style.render(v)
	for doctype, (name, template) in FORMATS.items():
		if not frappe.db.exists("DocType", doctype):
			continue  # e.g. ERPNext not installed

		fields = {
			"doc_type": doctype,
			"module": MODULE,
			"standard": "No",
			"custom_format": 1,
			"print_format_type": "Jinja",
			"print_format_builder": 0,
			"html": _html(template),
			"css": css,
			"disabled": 0,
		}

		if frappe.db.exists("Print Format", name):
			doc = frappe.get_doc("Print Format", name)
			if any(doc.get(k) != val for k, val in fields.items()):
				doc.update(fields)
				doc.flags.ignore_permissions = True
				doc.save()
		else:
			doc = frappe.new_doc("Print Format")
			doc.update(fields)
			doc.name = name
			doc.set("__newname", name)
			doc.flags.ignore_permissions = True
			doc.insert()

		_set_default(doctype, name, bool(v["set_default_print_formats"]))


def _set_default(doctype, name, on):
	current = frappe.db.get_value(
		"Property Setter",
		{"doc_type": doctype, "property": "default_print_format", "doctype_or_field": "DocType"},
		["name", "value"],
		as_dict=True,
	)
	if on:
		if not current or current.value != name:
			frappe.make_property_setter(
				{
					"doctype": doctype,
					"doctype_or_field": "DocType",
					"property": "default_print_format",
					"value": name,
					"property_type": "Data",
				},
				validate_fields_for_doctype=False,
			)
	elif current and current.value == name:
		# Only undo our own default, never one the user picked.
		frappe.delete_doc("Property Setter", current.name, ignore_permissions=True)
		frappe.clear_cache(doctype=doctype)
