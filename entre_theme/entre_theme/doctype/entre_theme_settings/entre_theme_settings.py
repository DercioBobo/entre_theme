import frappe
from frappe.model.document import Document


class EntreThemeSettings(Document):
	def on_update(self):
		# The theme ships inside the cached desk boot (api.boot_session);
		# drop the cache so every user picks up the new values on next load.
		frappe.cache.delete_key("bootinfo")
