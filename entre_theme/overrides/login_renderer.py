import frappe
from frappe import _
from werkzeug.wrappers import Response

from entre_theme.api import get_css_vars, get_font_url, get_login_theme, get_settings_values

NOTICE_TYPES = {"Informação": "info", "Aviso": "warning", "Importante": "alert"}
SAFE_LINK = ("http://", "https://", "mailto:", "tel:", "/")


def get_login_notice(v):
	"""The notice above the form, or None (empty, or past "Mostrar até")."""
	text = (v["login_notice"] or "").strip()
	if not text:
		return None
	if v["login_notice_until"]:
		try:
			if frappe.utils.now_datetime() > frappe.utils.get_datetime(v["login_notice_until"]):
				return None
		except Exception:
			pass
	return {"text": text, "type": NOTICE_TYPES.get(v["login_notice_type"], "info")}


def get_footer_links(v):
	""""Texto | endereço" per line; lines without a safe address are skipped."""
	links = []
	for line in (v["login_footer_links"] or "").splitlines():
		label, sep, url = line.partition("|")
		label, url = label.strip(), url.strip()
		if sep and label and url.lower().startswith(SAFE_LINK) and not url.startswith("//"):
			links.append({"label": label, "url": url})
	return links


def get_company_name():
	"""The name shown in the brand panel and as the monogram when there's no logo."""
	for getter in (
		lambda: frappe.db.get_single_value("Website Settings", "app_name"),
		lambda: frappe.defaults.get_global_default("company"),
	):
		try:
			name = getter()
		except Exception:
			name = None
		if name and name != "Frappe":
			return name
	return ""


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
		"""Only /login, and only while "Usar a Página de Login do Tema" is on;
		otherwise Frappe serves its own login page."""
		clean_path = self.path.split("?")[0].strip("/")
		if clean_path != "login":
			return False
		return bool(get_settings_values()["custom_login"])

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

		favicon = values["favicon"]
		if not favicon:
			try:
				favicon = frappe.db.get_single_value("Website Settings", "favicon") or ""
			except Exception:
				favicon = ""

		company_name = get_company_name()
		css_vars = get_css_vars(values)
		login_style, style_vars, style_classes = get_login_theme(values)
		css_vars.update(style_vars)
		context.update({
			"css_vars": css_vars,
			# The login accent (its own colour, or the global one): background gradient
			"primary_color": css_vars["--primary-color"],
			"favicon": favicon or "/assets/frappe/images/favicon.ico",
			"login_style": login_style,
			"login_classes": " ".join(style_classes),
			"company_name": company_name,
			"login_headline": values["login_headline"],
			"login_subtext": values["login_subtext"],
			"type_text": values["login_type_text"] or company_name or "Entre",
			# Moldura uses the welcome text as the form title
			"title_text": values["login_headline"] if login_style == "frame" else _("Iniciar sessão"),
			"font_url": get_font_url(values["font_family"]),
			"custom_css": values["custom_css"],
			"logo_url": logo_url,
			"login_bg_url": values["login_bg_url"],
			"company_tagline": values["company_tagline"],
			"login_notice": get_login_notice(values),
			"footer_links": get_footer_links(values),
			"copyright": (
				f"© {frappe.utils.now_datetime().year} {company_name}".strip()
				if values["login_copyright"] else ""
			),
		})

		html = frappe.render_template("entre_theme/templates/pages/login.html", context)

		# A raw Werkzeug Response is the correct return type for the v15
		# page_renderer protocol (respond_as_web_page has side effects).
		return Response(html, status=200, content_type="text/html; charset=utf-8")
