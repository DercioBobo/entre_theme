"""Notices in the desk ("Avisos" in Entre Theme Settings).

The notices that apply to the user (by role) ship with the theme in the desk
boot. The boot is cached per user and the settings save clears it, so start
and end times are sent as timestamps and checked by theme.js in the browser:
a notice appears and disappears on time without a reload.
"""

import hashlib
from zoneinfo import ZoneInfo

import frappe
from frappe.utils import get_datetime, get_system_timezone

NOTICE_TYPES = {"Informação": "info", "Aviso": "warning", "Importante": "alert", "Sucesso": "success"}
NOTICE_STYLES = {"Faixa": "bar", "Cartão": "card"}
SAFE_LINK = ("http://", "https://", "mailto:", "tel:", "/")


def parse_roles(text):
	return [r.strip() for r in (text or "").replace(",", "\n").splitlines() if r.strip()]


def safe_link(url):
	url = (url or "").strip()
	return url if url.startswith(SAFE_LINK) and not url.startswith("//") else ""


def _timestamp(value):
	"""Milliseconds since the epoch of a datetime in the system time zone."""
	if not value:
		return None
	dt = get_datetime(value)
	try:
		zone = ZoneInfo(get_system_timezone())
	except Exception:
		zone = None  # no time zone database: the server's local time
	return int(dt.replace(tzinfo=zone).timestamp() * 1000)


def _rows():
	try:
		return frappe.get_cached_doc("Entre Theme Settings").get("desk_notices") or []
	except Exception:
		return []


def get_desk_notices(v):
	"""The current user's notices, for theme.js; None when the feature is off.
	Never raises: a bad notice must not take the theme down with it."""
	if not v["desk_notices_on"]:
		return None
	try:
		return _desk_notices(v)
	except Exception:
		frappe.log_error(title="Entre Theme: desk notices")
		return None


def _desk_notices(v):
	roles = set(frappe.get_roles())
	now = _timestamp(frappe.utils.now_datetime())
	out = []
	for row in _rows():
		message = (row.get("message") or "").strip()
		if not row.get("enabled") or not message:
			continue
		allowed = parse_roles(row.get("roles"))
		if allowed and not roles.intersection(allowed):
			continue
		end = _timestamp(row.get("end_at"))
		if end and end <= now:
			continue
		link = safe_link(row.get("link_url"))
		label = (row.get("link_label") or "").strip()
		# Same text, type and link: same id, so a closed notice stays closed;
		# change any of them and it shows again.
		key = "\n".join((message, row.get("notice_type") or "", link, label))
		out.append({
			"id": hashlib.md5(key.encode("utf-8")).hexdigest()[:12],
			"message": message,
			"type": NOTICE_TYPES.get(row.get("notice_type"), "info"),
			"link": link,
			"link_label": label or (link and "Abrir") or "",
			"start": _timestamp(row.get("start_at")),
			"end": end,
		})
	return {
		"style": NOTICE_STYLES.get(v["desk_notice_style"], "bar"),
		"dismiss": bool(v["desk_notice_dismiss"]),
		"items": out,
	}


def validate_rows(rows):
	"""Settings validation: known roles, a safe link, end after start."""
	known = None
	for row in rows or []:
		names = parse_roles(row.get("roles"))
		if names:
			if known is None:
				known = set(frappe.get_all("Role", pluck="name"))
			unknown = [r for r in names if r not in known]
			if unknown:
				frappe.throw(
					frappe._("Aviso na linha {0}: função desconhecida: {1}").format(row.idx, ", ".join(unknown))
				)
		if (row.get("link_url") or "").strip() and not safe_link(row.get("link_url")):
			frappe.throw(
				frappe._("Aviso na linha {0}: a ligação tem de começar por https://, http://, mailto:, tel: ou /").format(row.idx)
			)
		if row.get("start_at") and row.get("end_at") and get_datetime(row.end_at) <= get_datetime(row.start_at):
			frappe.throw(frappe._("Aviso na linha {0}: o Fim tem de ser depois do Início").format(row.idx))
