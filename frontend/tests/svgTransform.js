// eslint-disable-next-line @typescript-eslint/no-var-requires
const path = require("path");

module.exports = {
  process(src, absoluteFilename) {
    const filename = path.relative("", absoluteFilename);
    return `module.exports = "${filename}";`;
  }
};
