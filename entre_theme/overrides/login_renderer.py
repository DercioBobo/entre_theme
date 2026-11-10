import frappe
from werkzeug.wrappers import Response

from entre_theme.api import get_css_vars, get_font_url, get_settings_values


class LoginPageRenderer:
	"""
	Custom page renderer for Frappe v15 that intercepts the /login route
	and serves a fully themed login page while preserving all standard
	Frappe login context (SSO providers, redirect URLs, etc.).

	Frappe v15 page_renderer protocol:
	  - __init__(self, path, doctype=None)
	  - can_render(self) -> bool
	  - render(self) -> werkzeug.wrappers.Response
	"""

	def __init__(self, path, doctype=None):
		self.path = path
		self.doctype = doctype

	def can_render(self):
		"""Return True only for the /login path."""
		clean_path = self.path.split("?")[0].strip("/")
		return clean_path == "login"

	def render(self):
		context = frappe._dict()
		try:
			from frappe.www.login import get_context as frappe_login_context
			frappe_login_context(context)
		except Exception:
			# Frappe's login context helper unavailable or changed signature.
			context.update({
				"provider_logins": [],
				"social_login": False,
				"show_language_picker": False,
				"dev_server": frappe.conf.get("developer_mode", 0),
			})

		values = get_settings_values()
		logo_url = values["logo_url"]
		if not logo_url:
			try:
				logo_url = frappe.db.get_single_value("Website Settings", "app_logo") or ""
			except Exception:
				logo_url = ""

		context.update({
			"css_vars": get_css_vars(values),
			"primary_color": values["primary_color"],
			"font_url": get_font_url(values["font_family"]),
			"custom_css": values["custom_css"],
			"logo_url": logo_url,
			"login_bg_url": values["login_bg_url"],
			"company_tagline": values["company_tagline"],
		})

		html = frappe.render_template("entre_theme/templates/pages/login.html", context)

		# A raw Werkzeug Response is the correct return type for the v15
		# page_renderer protocol (respond_as_web_page has side effects).
		return Response(html, status=200, content_type="text/html; charset=utf-8")
