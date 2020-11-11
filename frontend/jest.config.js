module.exports = {
  preset: "@vue/cli-plugin-unit-jest/presets/typescript-and-babel",
  testMatch: [
    "<rootDir>/tests/*.spec.(js|jsx|ts|tsx)",
    "<rootDir>/src/**/tests/*.spec.(js|jsx|ts|tsx)"
  ],
  transform: {
    "^.+\\.svg$": "<rootDir>/tests/svgTransform.js"
  }
};
