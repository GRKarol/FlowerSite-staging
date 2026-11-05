// node karty/render.cjs  -> PDF (96x61 mm ze spadem) i PNG 300 dpi z każdego pliku HTML w karty/wydruk
// Wymaga zainstalowanego playwright (npm i -g playwright) i przeglądarki chromium.
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('fs'), path = require('path');
const dir = path.join(__dirname, 'wydruk');
(async () => {
  const b = await chromium.launch();
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.html'));
  for (const f of files) {
    const p = await b.newPage({ viewport: { width: 363, height: 231 }, deviceScaleFactor: 300 / 96 });
    await p.goto('file://' + path.join(dir, f));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(400);
    const base = path.join(dir, f.replace(/\.html$/, ''));
    await p.pdf({ path: base + '.pdf', width: '96mm', height: '61mm', printBackground: true });
    await p.screenshot({ path: base + '.png' });
    await p.close();
    console.log(f);
  }
  await b.close();
})();
