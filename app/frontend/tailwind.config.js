/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Manrope", "Avenir Next", "Segoe UI", "sans-serif"],
        display: ["Cormorant Garamond", "Georgia", "serif"],
      },
      boxShadow: {
        shell: "0 24px 70px rgba(176, 150, 170, 0.16)",
        soft: "0 16px 38px rgba(176, 150, 170, 0.12)",
      },
      keyframes: {
        spinSoft: {
          to: {
            transform: "rotate(360deg)",
          },
        },
        cardIn: {
          from: {
            opacity: "0",
            transform: "translateY(14px)",
          },
          to: {
            opacity: "1",
            transform: "translateY(0)",
          },
        },
      },
      animation: {
        "spin-soft": "spinSoft 0.8s linear infinite",
        "card-in": "cardIn 0.45s ease both",
      },
    },
  },
  plugins: [],
};
