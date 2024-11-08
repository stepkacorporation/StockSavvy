/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "app/templates/**/*.html",
    "app/static/js/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("daisyui"),
  ],
  daisyui: {
    themes: ["dim", "light"],
  },
}
