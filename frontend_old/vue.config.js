module.exports = {
  devServer: {
    proxy: {
      "^/api": {
        target: "http://127.0.0.1:8000",
        ws: true,
        pathRewrite: {
          "^/api": ""
        }
      }
    }
  },
  pages: {
    index: {
      entry: "./src/main.js"
    }
  },
  css: {
    loaderOptions: {
      sass: {
        webpackImporter: false,
        sassOptions: {
          includePaths: ["./node_modules"]
        }
      }
    }
  }
};
