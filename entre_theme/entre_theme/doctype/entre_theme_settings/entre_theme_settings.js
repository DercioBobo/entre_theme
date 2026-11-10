frappe.ui.form.on('Entre Theme Settings', {
	refresh: function(frm) {
		if (frm.doc.manage_print_style) {
			frm.add_custom_button(__('Estilo de Impressão'), function() {
				frappe.set_route('Form', 'Print Style', 'Entre Theme');
			}, __('Ver'));
		}
	},

	after_save: function(frm) {
		// Settings apply live: refresh the current page's theme, no rebuild needed.
		if (window.entre_theme) {
			window.entre_theme.refresh();
		}
		frappe.show_alert({
			message: frm.doc.manage_print_style
				? __('Tema aplicado. Estilo de impressão "Entre Theme" actualizado.')
				: __('Tema aplicado'),
			indicator: 'green'
		});
	}
});
