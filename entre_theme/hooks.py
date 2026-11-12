app_name = "entre_theme"
app_title = "Entre Theme"
app_publisher = "Entretech"
app_description = "A non-destructive ERPNext theme app"
app_email = "hello@entretech.pt"
app_license = "mit"

# ─────────────────────────────────────────────
# Desk Assets (included in every logged-in page)
# ─────────────────────────────────────────────
app_include_css = [
	"/assets/entre_theme/css/theme.css",
]
app_include_js = [
	"/assets/entre_theme/js/theme.js",
]

# Website, portal and error pages (rules gated by body classes, see website.py)
web_include_css = [
	"/assets/entre_theme/css/web.css",
]

# Loading screen (/app) and website pages: entre_theme.website
update_website_context = ["entre_theme.website.update_website_context"]

# Theme values ship with the desk boot payload (read by theme.js)
boot_session = "entre_theme.api.boot_session"

# ─────────────────────────────────────────────
# Custom Login Page Renderer
# (standalone page: links login.css itself and has its own inline JS)
# ─────────────────────────────────────────────
page_renderer = ["entre_theme.overrides.login_renderer.LoginPageRenderer"]

# ─────────────────────────────────────────────
# Install / Uninstall Hooks
# ─────────────────────────────────────────────
after_install = "entre_theme.install.after_install"
# Fill in new settings; re-render the print style and print formats
after_migrate = "entre_theme.install.after_migrate"
before_uninstall = "entre_theme.install.before_uninstall"

# ─────────────────────────────────────────────
# Jinja methods: entre_print_context(doc) for templates/print/*.html,
# entre_email_context() for the email template
# ─────────────────────────────────────────────
jinja = {
	"methods": [
		"entre_theme.print_utils.entre_print_context",
		# Branded emails: templates/emails/standard.html (see emails.py)
		"entre_theme.emails.entre_email_context",
		# Letter Head "Entre Theme": header and footer (see letter_head.py)
		"entre_theme.letter_head.entre_letter_head",
		"entre_theme.letter_head.entre_letter_head_footer",
	],
}
