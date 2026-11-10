import frappe
from frappe.model.document import Document

from entre_theme import print_formats, print_style
from entre_theme.api import get_settings_values, sync_favicon


class EntreThemeSettings(Document):
	def on_update(self):
		# The theme ships inside the cached desk boot (api.boot_session);
		# drop the cache so every user picks up the new values on next load.
		frappe.cache.delete_key("bootinfo")
		values = get_settings_values(self)
		sync_favicon(values)
		print_style.sync(values)
		print_formats.sync(values)
