const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch();
  for (const [v, w, h, t] of [['icon',1024,1024,false],['mark',1024,1024,true],['avatar',1024,1024,false],['full',2000,900,false]]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('file://' + path.join(__dirname, 'logo.html') + '?v=' + v); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
    await p.screenshot({ path: path.join(__dirname, 'deliver', `logo-${v}.png`), omitBackground: t }); }
  await b.close(); })();
