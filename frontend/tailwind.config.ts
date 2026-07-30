// This Tailwind configuration scopes scanning to the React source files.
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: []
} satisfies Config;
