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

## Features

- Custom Login Page
- Re-themed desk navbar and sidebar
- Admin settings page (Entre Theme Settings) — changes apply on save, no rebuild needed
- Mobile responsive

## How it works

- Defaults live in `public/css/theme.css` as CSS custom properties.
- Saved settings are sent with the desk boot payload (`boot_session` hook) and
  applied by `public/js/theme.js` as inline variables on `<html>`.
- The login page (`/login`) is served by a custom page renderer that inlines the
  same variables server-side.
- Fonts other than Inter are loaded from Google Fonts.

## License

MIT