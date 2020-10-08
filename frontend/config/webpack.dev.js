const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  output: {
    publicPath: '/'
  },
  mode: 'development',
  devtool: 'inline-source-map',
  devServer: {
    overlay: true,
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        pathRewrite: {
          '^/api': ''
        }
      }
    }
  },
});
