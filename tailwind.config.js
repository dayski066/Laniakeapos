// tailwind.config.js
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',     // Azul
        secondary: '#10B981',   // Verde
        accent: '#8B5CF6',      // Púrpura
        warning: '#F59E0B',     // Naranja
        danger: '#EF4444',      // Rojo
      },
    },
  },
  plugins: [],
}