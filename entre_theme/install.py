import frappe

from entre_theme.api import DEFAULTS

SETTINGS = "Entre Theme Settings"


def after_install():
	"""Seed Entre Theme Settings with defaults on a fresh install."""
	try:
		doc = frappe.get_single(SETTINGS)
		if not doc.primary_color:
			doc.update(DEFAULTS)
			doc.save(ignore_permissions=True)  # on_update renders the print style and formats
			frappe.db.commit()
		else:
			after_migrate()
	except Exception:
		# DocType may not yet be available during the very first migrate.
		pass

	print("\n" + "=" * 60)
	print("  Entre Theme installed successfully!")
	print("  Run the following to link assets:")
	print("    bench build --app entre_theme")
	print("=" * 60 + "\n")


def seed_defaults():
	"""Write the default of every setting that was never saved (fields added
	by an upgrade), so the stored settings always hold a real value."""
	if not frappe.db.exists("DocType", SETTINGS):
		return
	stored = set(frappe.db.sql_list("select field from `tabSingles` where doctype = %s", SETTINGS))
	if not stored:
		return  # never saved: after_install / first save fills everything
	missing = {key: value for key, value in DEFAULTS.items() if key not in stored}
	if missing:
		frappe.db.set_single_value(SETTINGS, missing)
		frappe.clear_document_cache(SETTINGS, SETTINGS)


def after_migrate():
	"""Fill in new settings, then re-render the print style and print formats
	(their templates may have changed with the update)."""
	from entre_theme import print_formats, print_style

	seed_defaults()
	print_style.sync()
	print_formats.sync()


def before_uninstall():
	"""
	Site data (Entre Theme Settings) is intentionally NOT deleted
	so that settings are preserved if the app is reinstalled.
	"""
	print("\n" + "=" * 60)
	print("  Uninstalling Entre Theme...")
	print("  Note: Settings data has been preserved in the database.")
	print("  To remove it manually: bench --site <site> execute")
	print("    frappe.delete_doc('Entre Theme Settings', 'Entre Theme Settings')")
	print("=" * 60 + "\n")
