// Jest setup file to polyfill web APIs needed by cheerio/undici in Node.js 18

// Polyfill File API for Node.js 18
if (typeof global.File === 'undefined') {
  const { Blob } = require('buffer');

  class File extends Blob {
    constructor(bits, name, options = {}) {
      super(bits, options);
      this.name = name;
      this.lastModified = options.lastModified || Date.now();
    }
  }

  global.File = File;
}

// Polyfill FormData if needed
if (typeof global.FormData === 'undefined') {
  try {
    const { FormData } = require('undici');
    global.FormData = FormData;
  } catch (e) {
    // FormData not available, skip
  }
}
