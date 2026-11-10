import frappe
from frappe.model.document import Document

from entre_theme import print_style
from entre_theme.api import get_settings_values


class EntreThemeSettings(Document):
	def on_update(self):
		# The theme ships inside the cached desk boot (api.boot_session);
		# drop the cache so every user picks up the new values on next load.
		frappe.cache.delete_key("bootinfo")
		print_style.sync(get_settings_values(self))
