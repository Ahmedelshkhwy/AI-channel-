// Records the tool walkthrough as sharp 1080x1920 clips (CDP screencast, variable frame timing).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const B = 'http://localhost:5000', D = __dirname + '/data/', OUT = __dirname + '/raw/';
const W = 810, H = 1440, DPR = 1080 / 810;
const only = process.argv[2];

const TOUCH = `(() => { const add = () => { if (document.getElementById('__t')) return;
  const c = document.createElement('div'); c.id='__t';
  c.style.cssText='position:fixed;z-index:2147483647;pointer-events:none;width:34px;height:34px;margin:-17px 0 0 -17px;border-radius:50%;background:rgba(15,118,110,.28);border:2px solid rgba(255,255,255,.95);box-shadow:0 2px 10px rgba(0,0,0,.35);left:-80px;top:-80px;transition:transform .12s';
  document.body.appendChild(c);
  document.addEventListener('mousemove', e => { c.style.left=e.clientX+'px'; c.style.top=e.clientY+'px'; }, true);
  document.addEventListener('mousedown', e => { c.style.transform='scale(.7)';
    const r=document.createElement('div'); r.style.cssText='position:fixed;z-index:2147483646;pointer-events:none;border-radius:50%;border:3px solid #0f766e;width:20px;height:20px;left:'+(e.clientX-10)+'px;top:'+(e.clientY-10)+'px;transition:all .5s ease-out;opacity:.95';
    document.body.appendChild(r); requestAnimationFrame(()=>{r.style.width=r.style.height='80px';r.style.left=(e.clientX-40)+'px';r.style.top=(e.clientY-40)+'px';r.style.opacity='0';}); setTimeout(()=>r.remove(),700);}, true);
  document.addEventListener('mouseup', () => c.style.transform='', true);
  const s=window.__lastXY; if (s) { c.style.left=s[0]+'px'; c.style.top=s[1]+'px'; }
 }; if (document.body) add(); else document.addEventListener('DOMContentLoaded', add); })();`;

const pause = (p, ms) => p.waitForTimeout(ms);
async function moveTo(p, loc, steps = 28) {
  await loc.scrollIntoViewIfNeeded(); await pause(p, 150);
  const b = await loc.boundingBox(); const x = b.x + b.width / 2, y = b.y + b.height / 2;
  await p.mouse.move(x, y, { steps }); await pause(p, 250);
}
async function tap(p, loc) { await moveTo(p, loc); await p.mouse.down(); await pause(p, 110); await p.mouse.up(); }
async function scroll(p, total, step = 5, wait = 14) { for (let d = 0; d < total; d += step) { await p.mouse.wheel(0, step); await pause(p, wait); } }
async function scrollTo(p, sel, offset = 120) {
  const y = await p.locator(sel).first().evaluate(e => e.getBoundingClientRect().top);
  await scroll(p, Math.max(0, y - offset));
}

async function scene(browser, name, fn) {
  if (only && !only.split(',').includes(name)) return;
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DPR, storageState: __dirname + '/state.json', acceptDownloads: true });
  await ctx.addInitScript(TOUCH);
  const p = await ctx.newPage();
  const dir = OUT + name; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const cdp = await ctx.newCDPSession(p); const frames = [];
  cdp.on('Page.screencastFrame', async f => {
    const file = `${dir}/${String(frames.length).padStart(5, '0')}.jpg`;
    fs.writeFileSync(file, Buffer.from(f.data, 'base64')); frames.push([file, f.metadata.timestamp]);
    try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch (e) {}
  });
  await p.goto(B + '/healthz');
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 1080, maxHeight: 1920, everyNthFrame: 1 });
  const t0 = Date.now() / 1000;
  await fn(p);
  await pause(p, 400);
  const tEnd = Date.now() / 1000;
  await cdp.send('Page.stopScreencast');
  await ctx.close();
  // Drop frames from the healthz warm-up, then build a constant 30 fps clip from the frame timestamps.
  const keep = frames.filter(f => f[1] >= t0 - 0.05);
  let list = '';
  keep.forEach((f, i) => { const next = i + 1 < keep.length ? keep[i + 1][1] : tEnd; list += `file '${f[0]}'\nduration ${Math.max(0.001, next - f[1]).toFixed(4)}\n`; });
  list += `file '${keep[keep.length - 1][0]}'\n`;
  fs.writeFileSync(dir + '.txt', list);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', dir + '.txt', '-vf', 'fps=30,scale=1080:1920:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', OUT + name + '.mp4']);
  console.log(name, keep.length, 'frames', (tEnd - t0).toFixed(1) + 's');
}

(async () => {
  const browser = await chromium.launch();

  await scene(browser, '1-upload', async p => {
    await p.goto(B + '/upload'); await pause(p, 1400);
    await moveTo(p, p.locator('.dropzone')); await p.mouse.down(); await pause(p, 100); await p.mouse.up();
    await p.setInputFiles('input[type=file]', [D + 'maadi_items.xlsx']); await pause(p, 1100);
    await tap(p, p.locator('form[enctype] input[name=branch]')); await p.keyboard.type('فرع المعادي', { delay: 120 }); await pause(p, 800);
    await tap(p, p.locator('form[enctype] button[type=submit]'));
    await p.waitForURL('**/upload/review/**'); await pause(p, 1800);
    const days = p.locator('input[name=period_days]');
    await tap(p, days); await pause(p, 500); await p.keyboard.type('90', { delay: 260 }); await pause(p, 700); await p.keyboard.press('Tab'); await p.mouse.move(600, 900, { steps: 15 }); await pause(p, 900);
    await scrollTo(p, '.mapping-table', 160); await pause(p, 2600);
    await scroll(p, 300); await pause(p, 1500);
    const go = p.locator('form[method=post]:has(input[name=period_days]) button[type=submit]').last();
    await tap(p, go);
    await p.waitForURL('**/imports/**'); await pause(p, 2200);
    await scroll(p, 700, 5, 16); await pause(p, 1800);
  });

  await scene(browser, '2-dashboard', async p => {
    await p.goto(B + '/'); await pause(p, 2200);
    await scroll(p, 900, 5, 16); await pause(p, 1500);
    await scroll(p, 900, 5, 16); await pause(p, 1500);
    await p.goto(B + '/abc'); await pause(p, 2200);
    await scroll(p, 800, 5, 16); await pause(p, 1800);
  });

  await scene(browser, '3-transfers', async p => {
    await p.goto(B + '/actions'); await pause(p, 1800);
    await scrollTo(p, 'h2:has-text("حوّل بين الفروع")', 90); await pause(p, 2500);
    const rows = p.locator('section.section-head:has(h2:has-text("حوّل بين الفروع")) + section.panel tbody tr');
    for (const i of [0, 1, 2]) { await moveTo(p, rows.nth(i).locator('td').nth(3), 22); await pause(p, 900); }
    await scroll(p, 420, 5, 16); await pause(p, 900);
    const btn = p.locator('a[href*="transfers.xlsx"]');
    const dl = p.waitForEvent('download'); await tap(p, btn); const d = await dl;
    await d.saveAs(__dirname + '/dl/transfers_all.xlsx'); await pause(p, 2200);
  });

  await scene(browser, '4-branch', async p => {
    await p.goto(B + '/actions'); await pause(p, 1500);
    const sel = p.locator('select[name=branch]').first();
    await moveTo(p, sel); await p.mouse.down(); await pause(p, 100); await p.mouse.up();
    await pause(p, 500); await sel.selectOption('فرع الشيخ زايد'); await p.waitForLoadState('load'); await pause(p, 2000);
    await scrollTo(p, 'h2:has-text("حوّل بين الفروع")', 90); await pause(p, 2500);
    await scroll(p, 420, 5, 16); await pause(p, 700);
    const dl = p.waitForEvent('download'); await tap(p, p.locator('a[href*="transfers.xlsx"]')); const d = await dl;
    await d.saveAs(__dirname + '/dl/transfers_zayed.xlsx'); await pause(p, 1800);
  });

  await scene(browser, '5-orders', async p => {
    await p.goto(B + '/actions'); await pause(p, 800);
    await scrollTo(p, 'h2:has-text("طلبيات الشراء")', 90); await pause(p, 2500);
    await scroll(p, 600, 5, 16); await pause(p, 1200);
    const btn = p.locator('a[href*="purchase-orders.xlsx"]').first();
    const dl = p.waitForEvent('download'); await tap(p, btn); const d = await dl;
    await d.saveAs(__dirname + '/dl/purchase_orders.xlsx'); await pause(p, 1800);
  });

  await scene(browser, '6-users', async p => {
    await p.goto(B + '/users'); await pause(p, 1600);
    const form = p.locator('form:has(input[name=action][value=create])');
    await scrollTo(p, 'form:has(input[name=action][value=create])', 100); await pause(p, 900);
    await tap(p, form.locator('input[name=username]')); await p.keyboard.type('maadi.manager', { delay: 90 });
    await tap(p, form.locator('input[name=password]')); await p.keyboard.type('maadi-pass-1', { delay: 70 });
    await moveTo(p, form.locator('select[name=role]')); await pause(p, 600);
    await tap(p, form.locator('label.checkbox-row:has-text("فرع المعادي")')); await pause(p, 900);
    await tap(p, form.locator('button[type=submit]')); await p.waitForLoadState('load'); await pause(p, 2000);
    await p.evaluate(() => window.scrollTo(0, 0)); await pause(p, 600);
    await scroll(p, 700, 5, 16); await pause(p, 2000);
  });

  await scene(browser, '7-settings', async p => {
    await p.goto(B + '/settings'); await pause(p, 2000);
    await scroll(p, 500, 5, 16); await pause(p, 1200);
    await scrollTo(p, '#settings-form', 100); await pause(p, 1000);
    for (const [key, val] of [['lead_time_days', '5'], ['target_cover_days', '30'], ['slow_moving_cover_days', '120']]) {
      const inp = p.locator(`#settings-form input[type=number][name=${key}]`);
      if (!(await inp.count())) continue;
      await tap(p, inp); await p.keyboard.press('Control+A'); await p.keyboard.type(val, { delay: 200 }); await pause(p, 900);
    }
    await tap(p, p.locator('#settings-form button[value=save]')); await p.waitForLoadState('load'); await pause(p, 2200);
    const re = p.locator('form:has(input[name=action][value=reanalyze]) button[type=submit]');
    await scrollTo(p, 'form:has(input[name=action][value=reanalyze])', 500); await pause(p, 1200);
    await tap(p, re); await p.waitForLoadState('load'); await pause(p, 1500);
    await p.evaluate(() => window.scrollTo(0, 0)); await pause(p, 2500);
  });

  for (const kind of ['transfers', 'orders']) await scene(browser, '8-excel-' + kind, async p => {
    await p.goto('file://' + __dirname + '/excel.html#' + kind); await pause(p, 2600);
    if (kind === 'transfers') { for (const r of [2, 3]) { await moveTo(p, p.locator('tr').nth(r).locator('td').nth(4), 24); await pause(p, 900); }
      await moveTo(p, p.locator('tr.t td').nth(4), 24); await pause(p, 1500); }
    const n = await p.locator('.tab').count();
    for (let i = 1; i < n; i++) { await tap(p, p.locator('.tab').nth(i)); await pause(p, 2200); }
  });
  await browser.close();
})();
