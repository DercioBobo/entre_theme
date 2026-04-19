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

function injectTailwindEnvironment() {
	if (document.getElementById('tailwind-cdn')) return;

	// 1. Inject Tailwind CDN
	const script = document.createElement('script');
	script.id = 'tailwind-cdn';
	script.src = "https://cdn.tailwindcss.com";
	
	// 2. Map DocType variables to Tailwind theme!
	const config = document.createElement('script');
	config.innerHTML = `
		tailwind.config = {
			corePlugins: { preflight: false },
			theme: {
				extend: {
					colors: {
						primary: 'var(--primary-color)',
						'primary-hover': 'var(--primary-hover)',
						'card-bg': 'var(--card-bg)',
						'card-border': 'var(--card-border)',
						'input-bg': 'var(--input-bg)',
						'input-border': 'var(--input-border)',
						'input-focus': 'var(--input-focus-ring)',
						'navbar-bg': 'var(--navbar-bg)',
						'sidebar-bg': 'var(--sidebar-bg)',
						'sidebar-active': 'var(--sidebar-active-bg)',
						'sidebar-text': 'var(--sidebar-text)',
						'sidebar-text-active': 'var(--sidebar-text-active)',
					},
					borderRadius: {
						theme: 'var(--border-radius)',
					},
					boxShadow: {
						card: 'var(--card-shadow)',
						btn: 'var(--button-shadow)',
					}
				}
			}
		}
	`;
	
	document.head.appendChild(config);
	document.head.appendChild(script);

	// 3. Setup a Tailwind CSS block for @apply targeting standard Frappe components
	const tailwindStyles = document.createElement('style');
	tailwindStyles.type = "text/tailwindcss";
	tailwindStyles.innerHTML = \`
		/* Overriding core frappe UI components using Tailwind */
		.frappe-card, .widget, .widget-group .widget {
			@apply bg-card-bg rounded-theme shadow-card border border-card-border;
		}
		
		.form-control, .input-with-feedback {
			@apply rounded-theme bg-input-bg border border-input-border transition-all duration-200 outline-none;
		}

		.form-control:focus, .input-with-feedback:focus-within {
			@apply border-input-focus ring-2 ring-input-focus ring-opacity-20;
		}

		.btn-primary {
			@apply bg-primary border-primary text-white rounded-theme shadow-btn transition-all duration-200;
		}
		.btn-primary:focus { @apply ring-2 ring-primary ring-opacity-30; }
		.btn-primary:hover { @apply bg-primary-hover border-primary-hover -translate-y-px; }

		.desk-sidebar .sidebar-item-container {
			@apply mx-4 my-1 rounded-theme transition-all duration-200;
		}
		.desk-sidebar .standard-sidebar-item {
			@apply text-sidebar-text py-2 px-4 rounded-theme;
		}
		.desk-sidebar .standard-sidebar-item:hover, .desk-sidebar .standard-sidebar-item.selected {
			@apply bg-sidebar-active text-sidebar-text-active;
		}
	\`;
	document.head.appendChild(tailwindStyles);
}

/**
 * Fetch theme variables from server and apply them.
 */
function fetchAndApplyTheme() {
	injectTailwindEnvironment();
	
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
