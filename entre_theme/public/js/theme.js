/**
 * applyThemeVars reads the theme dict and applies them as CSS Custom Properties 
 * on the root HTML element, enabling dynamic theme switching without compilation.
 * @param {Object} vars 
 */
function applyThemeVars(vars) {
	if(!vars) return;
	
	const root = document.documentElement;
	
	if(vars.primary_color) root.style.setProperty('--primary-color', vars.primary_color);
	if(vars.navbar_bg) root.style.setProperty('--navbar-bg', vars.navbar_bg);
	if(vars.sidebar_bg) root.style.setProperty('--sidebar-bg', vars.sidebar_bg);
	if(vars.font_family) root.style.setProperty('--font-family', `"${vars.font_family}", system-ui, -apple-system, sans-serif`);
	
	if(vars.enable_animations === 0) {
		root.style.setProperty('--transition', 'none');
	} else {
		root.style.setProperty('--transition', 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)');
	}
	
	// Inject custom CSS if provided
	if(vars.custom_css) {
		let styleTag = document.getElementById('entre-custom-css');
		if(!styleTag) {
			styleTag = document.createElement('style');
			styleTag.id = 'entre-custom-css';
			document.head.appendChild(styleTag);
		}
		styleTag.innerHTML = vars.custom_css;
	}
}

/**
 * Fetch theme variables from server and apply them.
 */
function fetchAndApplyTheme() {
	frappe.call({
		method: 'entre_theme.api.get_theme_vars',
		callback: function(r) {
			if(r.message) {
				applyThemeVars(r.message);
			}
		}
	});
}

// Hook into Frappe's lifecycle
frappe.ready(function() {
	// Apply initially
	fetchAndApplyTheme();
	
	// Re-apply if necessary when routes change (as occasionally Frappe resets DOM)
	frappe.router.on('change', function() {
		// Just ensure styles persist
		const styleTag = document.getElementById('entre-custom-css');
		if(!styleTag) fetchAndApplyTheme();
	});
});
