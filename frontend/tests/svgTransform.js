var path = require('path')
module.exports = {
  process(src, absoluteFilename) {
    var filename = path.relative('', absoluteFilename)
    return `module.exports = "${filename}";`
  },
};
