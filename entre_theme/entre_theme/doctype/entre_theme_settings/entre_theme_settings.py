import frappe
from frappe.model.document import Document

from entre_theme import letter_head, notices, print_formats, print_style, website
from entre_theme.api import get_settings_values, sync_favicon


class EntreThemeSettings(Document):
	def validate(self):
		notices.validate_rows(self.get("desk_notices"))

	def on_update(self):
		# The theme ships inside the cached desk boot (api.boot_session);
		# drop the cache so every user picks up the new values on next load.
		frappe.cache.delete_key("bootinfo")
		values = get_settings_values(self)
		sync_favicon(values)
		print_style.sync(values)
		print_formats.sync(values)
		website.sync_splash(values)
		letter_head.sync(values)
