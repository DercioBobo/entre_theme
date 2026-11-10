import frappe

from entre_theme.api import DEFAULTS


def after_install():
	"""Seed Entre Theme Settings with defaults on a fresh install."""
	try:
		doc = frappe.get_single("Entre Theme Settings")
		if not doc.primary_color:
			doc.update(DEFAULTS)
			doc.save(ignore_permissions=True)
			frappe.db.commit()
	except Exception:
		# DocType may not yet be available during the very first migrate.
		pass

	print("\n" + "=" * 60)
	print("  Entre Theme installed successfully!")
	print("  Run the following to link assets:")
	print("    bench build --app entre_theme")
	print("=" * 60 + "\n")


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
