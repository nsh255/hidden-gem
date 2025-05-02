/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        'silver': {
          50: '#f7f7f7',
          100: '#ededed',
          200: '#d3d3d3',
          300: '#b3b3b3',
          400: '#9e9e9e',
          500: '#818181',
          600: '#696969',
          700: '#535353',
          800: '#323232',
          900: '#1c1c1c',
        },
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}
