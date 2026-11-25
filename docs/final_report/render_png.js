// Renders docs/final_report/diagrams/*.svg to PNG at 2x (run from anywhere; needs frontend/node_modules).
const path = require('path');
const fs = require('fs');
const { chromium } = require(require.resolve('playwright', { paths: [path.join(__dirname, '../../frontend'), __dirname] }));
(async () => {
  const dir = path.join(__dirname, 'diagrams');
  const out = path.join(__dirname, 'png');
  fs.mkdirSync(out, { recursive: true });
  for (const f of fs.readdirSync(out).filter(n => n.endsWith('.png'))) fs.unlinkSync(path.join(out, f));
  const browser = await chromium.launch();
  for (const f of fs.readdirSync(dir).filter(n => n.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const m = svg.match(/width='([\d.]+)' height='([\d.]+)'/);
    const w = Math.ceil(+m[1]), h = Math.ceil(+m[2]);
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 2.5 });
    await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
    await page.screenshot({ path: path.join(out, f.replace('.svg', '.png')), clip: { x: 0, y: 0, width: w, height: h } });
    await page.close();
  }
  await browser.close();
  console.log('rendered');
})();
