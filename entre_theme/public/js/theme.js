/**
 * applyThemeVars reads the theme dict and applies them as CSS Custom Properties 
 * on the root HTML element, enabling dynamic theme switching without compilation.
 * @param {Object} vars 
 */
function applyThemeVars(vars) {
	if(!vars) return;
	
	const root = document.documentElement;

	// Loop over everything and dynamically set standard ones
	for (const [key, value] of Object.entries(vars)) {
		if (['font_family', 'enable_animations', 'custom_css', 'button_shadow'].includes(key)) {
			continue; // Handle specially below
		}
		if (value) {
			const cssVar = '--' + key.replace(/_/g, '-');
			root.style.setProperty(cssVar, value);
		}
	}

	// Handle specials
	if(vars.font_family) {
		root.style.setProperty('--font-family', `"${vars.font_family}", system-ui, -apple-system, sans-serif`);
	}
	
	if(vars.enable_animations === 0) {
		root.style.setProperty('--transition', 'none');
	} else {
		root.style.setProperty('--transition', 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)');
	}

	if(vars.button_shadow && vars.button_shadow !== "0" && vars.button_shadow !== 0 && vars.button_shadow !== "none") {
		// Only set if Truthy / checked
		root.style.setProperty('--button-shadow', '0px 4px 14px rgba(0,0,0,0.2)');
	} else {
		root.style.setProperty('--button-shadow', 'none');
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
