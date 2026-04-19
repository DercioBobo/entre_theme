import frappe
from frappe.utils import get_html_format


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
		"""
		:param path: The requested URL path (e.g. 'login' or '/login')
		:param doctype: Unused for page renderers; included for protocol compliance.
		"""
		self.path = path
		self.doctype = doctype

	def can_render(self):
		"""Return True only for the /login path."""
		clean_path = self.path.split("?")[0].strip("/")
		return clean_path == "login"

	def render(self):
		"""
		Build the login page context, inject theme vars, render our custom
		template, and return a proper Werkzeug Response.
		"""
		# Build base Frappe login context safely
		context = frappe._dict()
		try:
			from frappe.www.login import get_context as frappe_login_context
			frappe_login_context(context)
		except Exception:
			# If Frappe's login context helper is unavailable or changes signature,
			# fall back to a minimal safe context
			context.update({
				"provider_logins": [],
				"social_login": False,
				"show_language_picker": False,
				"dev_server": frappe.conf.get("developer_mode", 0),
			})

		# Inject theme vars from settings
		try:
			settings = frappe.get_single("Entre Theme Settings")
			context.update({
				"primary_color": settings.primary_color or "#2B5CE6",
				"navbar_bg": settings.navbar_bg or "#1a1a2e",
				"sidebar_bg": settings.sidebar_bg or "#16213e",
				"font_family": settings.font_family or "Inter",
				"enable_animations": settings.enable_animations if settings.enable_animations is not None else 1,
				"custom_css": settings.custom_css or "",
				"logo_url": settings.logo_url or frappe.db.get_single_value("Website Settings", "app_logo") or "",
				"login_bg_url": settings.login_bg_url or "",
				"company_tagline": settings.company_tagline or "",
			})
		except Exception:
			# Graceful fallback during initial install / migration
			context.update({
				"primary_color": "#2B5CE6",
				"navbar_bg": "#1a1a2e",
				"sidebar_bg": "#16213e",
				"font_family": "Inter",
				"enable_animations": 1,
				"custom_css": "",
				"logo_url": "",
				"login_bg_url": "",
				"company_tagline": "",
			})

		# Render our Jinja template to an HTML string
		html = frappe.render_template(
			"entre_theme/templates/pages/login.html",
			context
		)

		# Return a proper Werkzeug Response (required by Frappe v15 renderer protocol)
		return frappe.respond_as_web_page(
			title="Login",
			html=html,
			http_status_code=200,
		)
