const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    "/api",
    createProxyMiddleware({
      target: "http://localhost:8000",
    })
  );
  app.use(
    "/docs",
    createProxyMiddleware({
      target: "http://localhost:8000",
    })
  );
  app.use(
    "/openapi.json",
    createProxyMiddleware({
      target: "http://localhost:8000",
    })
  );
};
