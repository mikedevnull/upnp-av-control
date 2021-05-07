const colors = require('tailwindcss/colors')

module.exports = {
  theme: {
    extend: {
      colors: {
        transparent: 'transparent',
        current: 'currentColor',
        primary: {
          lightest: '#F3F4F6',
          light: '#6B7280',
          DEFAULT: '#37415',
          dark: '#111827',
        },
        secondary: colors.amber,
      },
    },
  },
}
