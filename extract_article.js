#!/usr/bin/env node
// shamelessly borrowed from: https://olano.dev/blog/from-rss-to-my-kindle/

const { JSDOM } = require("jsdom");
const { Readability } = require('@mozilla/readability');

if (process.argv.length < 3) {
    console.error("missing argument; pass me an URL");
    process.exit(1);
}

function parseURL(input) {
    try {
        return new URL(input);
    } catch (e) {
        console.error(e.code, e.input);
        process.exit(1);
    }
}

JSDOM.fromURL(parseURL(process.argv[2])).then(function (dom) {
  let reader = new Readability(dom.window.document);
  let article = reader.parse();
  process.stdout.write(JSON.stringify(article), process.exit);
});
