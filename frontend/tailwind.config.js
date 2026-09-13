export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      boxShadow: {
        glass: "0 24px 80px rgba(15, 23, 42, 0.18)",
      },
      backgroundImage: {
        hero: "radial-gradient(circle at top, rgba(59, 130, 246, 0.25), transparent 35%), radial-gradient(circle at right, rgba(168, 85, 247, 0.18), transparent 28%)",
      },
    },
  },
  plugins: [],
};
