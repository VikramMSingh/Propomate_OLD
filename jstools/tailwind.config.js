module.exports = {
    future: {
        removeDeprecatedGapUtilities: true,
        purgeLayersByDefault: true,
    },
    purge: {
        enabled: true, //true for production build
        content: [
            '../**/templates/*.html',
            '../**/templates/**/*.html'
        ],
	safelist: [
      	    'bg-purple-900']
    },
    theme: {
        extend: {},
    },
    variants: {},
    plugins: [],
}
