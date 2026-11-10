# Entre Theme

A modern, non-destructive theme for the Frappe/ERPNext Desk and Login pages. Built exclusively using CSS variables and Vanilla Javascript.

## Developer

Entretech (https://entretech.pt)

## Installation

```sh
bench get-app https://github.com/DercioBobo/entre_theme
bench --site [sitename] install-app entre_theme
bench build --app entre_theme
```

Upgrading an existing site:

```sh
bench --site [sitename] migrate
bench build --app entre_theme
```

Then open **Entre Theme Settings** and save once. Sites upgraded from older
versions keep their old saved accent colour; set it to `#ec932c` for the
default orange look.

## Features

- Light, frosted desk look built around a single accent colour, with Frappe's
  dark theme supported
- Custom login page
- Entre Theme Settings (tabs: Geral, Aparência, Áreas de Trabalho, Impressão,
  Avançado). Changes apply on save, with no rebuild:
  - accent colour, button text colour, page background (light theme), corner
    radius, font, animations
  - navbar style (frosted glass or solid)
  - workspaces: hide shortcut counts, sidebar divider, faint logo watermark
  - custom CSS
- Generated **"Entre Theme" Print Style** for print formats and PDFs, optionally
  set as the default in Print Settings
- **"Entre …" Print Formats** that all share one layout: Cotação, Encomenda,
  Factura / Nota de Crédito, Guia de Remessa, Recibo, plus the purchase side
  (Cotação de Fornecedor, Ordem de Compra, Factura de Fornecedor, Guia de
  Recepção). They can be made the default for each document.

## Print formats

- Layout: `templates/print/transaction.html` (documents with items) and
  `templates/print/payment_entry.html`, built from the shared partials in
  `templates/print/parts/` (header with party box and watermark, footer).
- Data: `print_utils.py` prepares everything (title, dates, party, rows,
  totals, payment status), exposed to Jinja as `entre_print_context(doc)`.
  The per-document differences are in its `DOCS` table.
- Records: `print_formats.py` creates/updates the formats on settings save
  and `bench migrate`, for the doctypes that exist on the site. Each record
  is a one-line include of its template plus the rendered print CSS, so the
  formats look right whatever Print Style is selected.
- They are rewritten on every save/migrate: **duplicate** one to customise
  it beyond the options in Entre Theme Settings > Impressão.
- Titles can be changed per document with Frappe's Print Heading.

## How it works

- **Desk:** `public/css/theme.css` styles the desk from `--et-*` CSS variables,
  and its on/off parts are classes on `<body>` (`et-navbar-glass`,
  `et-hide-counts`, `et-ws-watermark`, `et-sidebar-divider`, `et-no-anim`).
  The saved settings travel with the desk boot payload (`boot_session` hook)
  and are applied by `public/js/theme.js`. Saving the settings clears the
  cached boot, so all users get the change on their next page load.
- **Login:** `/login` is served by a custom page renderer
  (`overrides/login_renderer.py`) that writes the variables into the page on
  the server.
- **Print:** wkhtmltopdf can't read CSS variables, so
  `templates/print/print_style.css` is rendered with the values filled in
  (`print_style.py`) and stored as the "Entre Theme" Print Style. This happens
  each time the settings are saved and after every `bench migrate`.

### Notes

- Fonts other than Inter come from Google Fonts. PDFs that use a Google print
  font need the server to have internet access; choose **Arial** as the print
  font to avoid that.
- The print rules are global under `.print-format`, so custom print formats
  that set their own fonts must mark those rules `!important` to keep them.

## License

MIT