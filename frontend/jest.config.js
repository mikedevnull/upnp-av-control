module.exports = {
  verbose: true,
  collectCoverage: true,
  collectCoverageFrom: ["src/**/*.{js,vue}", "!**/node_modules/**"],
  coverageReporters: ["lcov", "html", "text-summary"],
  moduleFileExtensions: [
    "js",
    "json",
    "vue"
  ],
  transform: {
    "^.+\\.vue$": "vue-jest",
    "^.+\\.js$": "babel-jest",
    "^.+\\.svg$": "<rootDir>/tests/svgTransform.js"
  },
  moduleNameMapper: {
    "^@/assets/(.*)": "<rootDir>/src/assets/$1",
    "^@/(.*)$": "<rootDir>/src/$1"
  }
};
