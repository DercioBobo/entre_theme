// Entre Theme Settings: presets, export / import, live colour preview,
// contrast warnings. Nothing here saves: the user reviews and saves.

const DOCTYPE = 'Entre Theme Settings';

// Fields that change the preview
const PREVIEW_FIELDS = [
	'primary_color', 'auto_text_on_accent', 'primary_text_color', 'page_bg', 'surface_color',
	'text_color', 'border_color', 'border_radius', 'font_family', 'primary_buttons',
	'navbar_accent', 'navbar_bg', 'navbar_text', 'sidebar_accent', 'sidebar_text',
	'workspace_accent', 'workspace_card_bg', 'login_accent', 'login_card_bg',
];

// Layout fields: never exported / imported
const LAYOUT_TYPES = ['Section Break', 'Column Break', 'Tab Break', 'HTML', 'Button', 'Heading'];
const NOT_EXPORTED = ['theme_preset'];

// ── Colour helpers (same rules as api.py) ─────────────────────────
function rgb(color) {
	let c = (color || '').trim().replace('#', '');
	if (c.length === 3) c = c.split('').map((ch) => ch + ch).join('');
	if (!/^[0-9a-f]{6}$/i.test(c)) return null;
	return [0, 2, 4].map((i) => parseInt(c.substr(i, 2), 16));
}

function luminance(values) {
	const [r, g, b] = values.map((v) => {
		v /= 255;
		return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
	});
	return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(a, b) {
	const ra = rgb(a), rb = rgb(b);
	if (!ra || !rb) return null;
	const [hi, lo] = [luminance(ra), luminance(rb)].sort((x, y) => y - x);
	return (hi + 0.05) / (lo + 0.05);
}

function textOn(color) {
	const onWhite = contrast(color, '#ffffff');
	if (onWhite === null || onWhite >= 3) return '#ffffff';
	return onWhite >= contrast(color, '#111111') ? '#ffffff' : '#111111';
}

function accentText(doc, accent) {
	return doc.auto_text_on_accent ? textOn(accent) : (doc.primary_text_color || '#ffffff');
}

// ── Live preview ───────────────────────────────────────────────────
function renderPreview(frm) {
	const field = frm.fields_dict.colors_preview;
	if (!field) return;
	const d = frm.doc;
	const accent = d.primary_color || '#ec932c';
	const surface = d.surface_color || '#ffffff';
	const text = d.text_color || '#0f172a';
	const border = d.border_color || '#edeef1';
	const page = d.page_bg || '#f5f6f8';
	const radius = d.border_radius || '12px';
	const font = !d.font_family || d.font_family === 'Padrão do Frappe'
		? 'system-ui, sans-serif' : `'${d.font_family}', system-ui, sans-serif`;
	const navAccent = d.navbar_accent || accent;
	const navBg = d.navbar_bg || surface;
	const navText = d.navbar_text || text;
	const sideAccent = d.sidebar_accent || accent;
	const sideText = d.sidebar_text || text;
	const wsAccent = d.workspace_accent || accent;
	const wsCard = d.workspace_card_bg || surface;
	const loginAccent = d.login_accent || accent;
	const loginCard = d.login_card_bg || surface;
	const darkButtons = d.primary_buttons === 'Escuro (Frappe)';
	const btnBg = darkButtons ? '#171717' : accent;
	const btnText = darkButtons ? '#ffffff' : accentText(d, accent);
	const mix = (c, pct, base) => `color-mix(in srgb, ${c} ${pct}%, ${base || 'transparent'})`;
	const ink = (c) => `color-mix(in oklch, ${c} 62%, black)`;

	field.$wrapper.html(`
		<div style="display:flex;gap:16px;flex-wrap:wrap;font-family:${font};font-size:12px;color:${text}">
			<div style="flex:2 1 360px;border:1px solid ${border};border-radius:12px;overflow:hidden;background:${page}">
				<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;background:${navBg};
					border-top:2px solid ${navAccent};border-bottom:1px solid ${border};color:${navText}">
					<span style="width:18px;height:18px;border-radius:5px;background:${navAccent}"></span>
					<span style="opacity:.8">Vendas › Clientes</span>
					<span style="margin-left:auto;background:${mix(navText, 6, navBg)};border-radius:8px;padding:3px 10px;opacity:.75">Pesquisar…</span>
				</div>
				<div style="display:flex;gap:12px;padding:12px">
					<div style="width:110px;color:${sideText}">
						<div style="padding:5px 8px;border-radius:8px;background:${mix(sideAccent, 12)};font-weight:600;
							box-shadow:inset 3px 0 0 ${sideAccent}">Início</div>
						<div style="padding:5px 8px;opacity:.75">Vendas</div>
						<div style="padding:5px 8px;opacity:.75">Stock</div>
					</div>
					<div style="flex:1;display:flex;flex-direction:column;gap:10px">
						<div style="background:${wsCard};border:1px solid ${border};border-radius:${radius};padding:10px 12px">
							<div style="font-weight:600;margin-bottom:8px;display:flex;align-items:center;gap:8px">
								<span style="width:3px;height:12px;border-radius:2px;background:${wsAccent}"></span>Contabilidade
							</div>
							<div style="display:flex;align-items:center;gap:8px">
								<span style="width:22px;height:22px;border-radius:7px;background:${mix(wsAccent, 14)};
									color:${ink(wsAccent)};display:inline-flex;align-items:center;justify-content:center">
									<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"
										stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg></span>
								Factura de Venda
							</div>
						</div>
						<div style="display:flex;align-items:center;gap:8px">
							<span style="background:${btnBg};color:${btnText};border-radius:8px;padding:5px 12px;font-weight:600">Guardar</span>
							<span style="background:${surface};border:1px solid ${border};border-radius:8px;padding:5px 12px">Cancelar</span>
							<span style="background:${mix(accent, 12)};color:${ink(accent)};border-radius:999px;padding:2px 9px;font-weight:500">Activo</span>
						</div>
					</div>
				</div>
			</div>
			<div style="flex:1 1 200px;border:1px solid ${border};border-radius:12px;display:flex;align-items:center;justify-content:center;
				padding:18px;background:linear-gradient(135deg, ${mix(loginAccent, 10, 'white')}, ${mix(loginAccent, 20, 'white')})">
				<div style="width:100%;max-width:200px;background:${loginCard};border-radius:${radius};padding:14px;
					box-shadow:0 10px 30px -12px rgba(15,23,42,.25)">
					<div style="width:28px;height:28px;border-radius:8px;background:${loginAccent};color:${accentText(d, loginAccent)};
						display:flex;align-items:center;justify-content:center;font-weight:700;margin:0 auto 10px">E</div>
					<div style="height:22px;border-radius:6px;background:${mix(text, 6, loginCard)};margin-bottom:6px"></div>
					<div style="height:22px;border-radius:6px;background:${mix(text, 6, loginCard)};margin-bottom:8px"></div>
					<div style="text-align:right;color:${ink(loginAccent)};margin-bottom:8px">Esqueceu a palavra-passe?</div>
					<div style="background:${loginAccent};color:${accentText(d, loginAccent)};border-radius:8px;padding:6px;
						text-align:center;font-weight:600">Entrar</div>
				</div>
			</div>
		</div>`);
}

// ── Contrast warnings ──────────────────────────────────────────────
function checkContrast(frm) {
	const d = frm.doc;
	const warnings = [];
	if (!d.auto_text_on_accent) {
		const c = contrast(d.primary_color, d.primary_text_color);
		if (c !== null && c < 3) {
			warnings.push(__('O texto sobre a Cor Principal é difícil de ler (contraste {0}:1). Ligue "Automático" ou escolha outra cor.', [c.toFixed(1)]));
		}
	}
	const body = contrast(d.text_color, d.surface_color);
	if (body !== null && body < 4.5) {
		warnings.push(__('O Texto sobre os Cartões é difícil de ler (contraste {0}:1).', [body.toFixed(1)]));
	}
	if (warnings.length) {
		frm.set_intro(warnings.join('<br>'), 'orange');
	} else {
		frm.set_intro('');
	}
}

// ── Export / import ────────────────────────────────────────────────
function themeValues(frm) {
	const values = {};
	frm.meta.fields.forEach((df) => {
		if (LAYOUT_TYPES.includes(df.fieldtype) || NOT_EXPORTED.includes(df.fieldname)) return;
		values[df.fieldname] = frm.doc[df.fieldname];
	});
	return values;
}

function exportTheme(frm) {
	const data = { entre_theme: 1, exported_on: frappe.datetime.now_datetime(), values: themeValues(frm) };
	const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
	const link = document.createElement('a');
	link.href = URL.createObjectURL(blob);
	link.download = `entre-theme-${frappe.datetime.now_date()}.json`;
	document.body.appendChild(link);
	link.click();
	setTimeout(() => {
		URL.revokeObjectURL(link.href);
		link.remove();
	}, 0);
}

function importTheme(frm) {
	const input = document.createElement('input');
	input.type = 'file';
	input.accept = '.json,application/json';
	input.addEventListener('change', () => {
		const file = input.files && input.files[0];
		if (!file) return;
		const reader = new FileReader();
		reader.onload = () => {
			let data;
			try {
				data = JSON.parse(reader.result);
			} catch (e) {
				frappe.msgprint(__('Este ficheiro não é um tema exportado (JSON inválido).'));
				return;
			}
			const values = (data && data.values) || {};
			const known = {};
			Object.keys(values).forEach((key) => {
				const df = frappe.meta.get_docfield(DOCTYPE, key);
				if (df && !LAYOUT_TYPES.includes(df.fieldtype) && !NOT_EXPORTED.includes(key)) {
					known[key] = values[key];
				}
			});
			if (!Object.keys(known).length) {
				frappe.msgprint(__('Não foram encontradas definições do Entre Theme neste ficheiro.'));
				return;
			}
			frm.set_value(known).then(() => {
				frappe.show_alert({ message: __('Tema importado. Reveja e grave para aplicar.'), indicator: 'blue' });
			});
		};
		reader.readAsText(file);
	});
	input.click();
}

// ── Form events ────────────────────────────────────────────────────
const events = {
	refresh(frm) {
		if (frm.doc.manage_print_style) {
			frm.add_custom_button(__('Estilo de Impressão'), () => {
				frappe.set_route('Form', 'Print Style', 'Entre Theme');
			}, __('Ver'));
		}
		frm.add_custom_button(__('Página de Login'), () => {
			window.open('/login', '_blank');
		}, __('Ver'));
		renderPreview(frm);
		checkContrast(frm);
	},

	apply_preset(frm) {
		const name = frm.doc.theme_preset;
		if (!name) return;
		frappe.call({
			method: 'entre_theme.presets.get_preset',
			args: { name },
			callback(r) {
				if (!r.message) return;
				frm.set_value(r.message).then(() => {
					frappe.show_alert({
						message: __('Predefinição "{0}" aplicada ao formulário. Reveja e grave.', [name]),
						indicator: 'blue',
					});
				});
			},
		});
	},

	export_theme(frm) {
		exportTheme(frm);
	},

	import_theme(frm) {
		importTheme(frm);
	},

	after_save(frm) {
		// Settings apply live: refresh the current page's theme, no rebuild needed.
		if (window.entre_theme) {
			window.entre_theme.refresh();
		}
		frappe.show_alert({
			message: frm.doc.manage_print_style
				? __('Tema aplicado. Estilo de impressão "Entre Theme" actualizado.')
				: __('Tema aplicado'),
			indicator: 'green',
		});
	},
};

PREVIEW_FIELDS.forEach((fieldname) => {
	events[fieldname] = (frm) => {
		renderPreview(frm);
		checkContrast(frm);
	};
});

frappe.ui.form.on(DOCTYPE, events);
