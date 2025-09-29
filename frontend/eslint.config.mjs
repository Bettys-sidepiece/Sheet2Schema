import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    ignores: [
      "node_modules/**",
      ".next/**",
      "out/**",
      "build/**",
      "next-env.d.ts",
    ],
    rules: {
      // Allow unescaped entities (quotes, apostrophes in JSX)
      "react/no-unescaped-entities": "off",

      // Allow unused variables if prefixed with _
      "@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],

      // Allow unused expressions (fixes `no-unused-expressions`)
      "@typescript-eslint/no-unused-expressions": "off",
    },
  },
];

export default eslintConfig;
