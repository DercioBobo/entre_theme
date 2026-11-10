frappe.ui.form.on('Entre Theme Settings', {
	after_save: function() {
		// Settings apply live: refresh the current page's theme, no rebuild needed.
		if (window.entre_theme) {
			window.entre_theme.refresh();
		}
		frappe.show_alert({ message: __('Tema aplicado'), indicator: 'green' });
	}
});
