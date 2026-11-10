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
# Print formats: entre_print_context(doc) for templates/print/*.html
# ─────────────────────────────────────────────
jinja = {
	"methods": ["entre_theme.print_utils.entre_print_context"],
}
