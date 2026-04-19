frappe.ui.form.on('Entre Theme Settings', {
	refresh: function(frm) {
		frm.add_custom_button(__('Aplicar Tema'), function() {
			frappe.call({
				method: 'entre_theme.api.apply_theme',
				callback: function(r) {
					if(!r.exc) {
						// Optionally reload to apply preview, but the message will instruct the user to build
					}
				}
			});
		}).addClass('btn-primary');
	}
});
