module.exports = {
  preset: "@vue/cli-plugin-unit-jest/presets/typescript-and-babel",
  testMatch: [
    "<rootDir>/tests/*.spec.(js|jsx|ts|tsx)",
    "<rootDir>/src/**/tests/*.spec.(js|jsx|ts|tsx)"
  ],
  transform: {
    "^.+\\.svg$": "<rootDir>/tests/svgTransform.js"
  },
  collectCoverage: true,
  collectCoverageFrom: ["src/**/*.{js,ts,vue}", "!**/node_modules/**"],
  coverageReporters: ["lcov", "html", "text-summary"],
  moduleFileExtensions: ["js", "ts", "json", "vue"]
};
