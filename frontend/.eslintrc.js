module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    "plugin:vue/essential",
    "eslint:recommended",
    //"@vue/javascript/recommended",
    //"@vue/prettier",
    //"@vue/prettier/@typescript-eslint"
  ],
  parserOptions: {
    ecmaVersion: 2020
  },
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off"
  },
  overrides: [
    {
      files: [
        "**/__tests__/*.{j,t}s?(x)",
        "src/**/tests/*.spec.{j,t}s?(x)",
        "**/tests/**/*.spec.{j,t}s?(x)",
        "**/tests/__mocks__/*.{j,t}s?(x)",
      ],
      env: {
        jest: true
      }
    }
  ]
};
