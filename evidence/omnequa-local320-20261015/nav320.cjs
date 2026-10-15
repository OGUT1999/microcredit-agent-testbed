const { chromium } = require('/opt/node-tools/node_modules/playwright-core');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const out = {};
  for (const [name, vp] of [['w1280_control', { width: 1280, height: 800 }], ['w320', { width: 320, height: 640 }]]) {
    const ctx = await browser.newContext({ viewport: vp, baseURL: 'http://127.0.0.1:8765' });
    const page = await ctx.newPage();
    await page.route('**/*', r => r.request().url().startsWith('http://127.0.0.1:8765/') ? r.continue() : r.abort());
    await page.goto('/partners/', { waitUntil: 'load' });
    out[name] = await page.evaluate(() => {
      const hdr = document.querySelector('header') || document.body;
      const navs = [...document.querySelectorAll('nav')].map(n => { const cs = getComputedStyle(n); const r = n.getBoundingClientRect(); return { cls: n.className || null, ariaLabel: n.getAttribute('aria-label'), overflowX: cs.overflowX, display: cs.display, flexWrap: cs.flexWrap, clientWidth: n.clientWidth, scrollWidth: n.scrollWidth, left: Math.round(r.left), right: Math.round(r.right), links: [...n.querySelectorAll('a')].map(a => { const b = a.getBoundingClientRect(); return { text: a.textContent.trim(), left: Math.round(b.left), right: Math.round(b.right), fullyVisible: b.left >= 0 && b.right <= innerWidth }; }) }; });
      let anc = []; const n0 = document.querySelector('nav'); if (n0) { for (let e = n0; e && e !== document.documentElement; e = e.parentElement) anc.push({ tag: e.tagName.toLowerCase(), cls: (e.className || '').toString().slice(0, 30), overflowX: getComputedStyle(e).overflowX, scrollWidth: e.scrollWidth, clientWidth: e.clientWidth }); }
      return { innerWidth, docScrollWidth: document.documentElement.scrollWidth, navs, nav_ancestors: anc };
    });
    // keyboard reachability: tab through header links, record the focused link rect after each focus
    const seq = [];
    for (let i = 0; i < 8; i++) {
      await page.keyboard.press('Tab');
      seq.push(await page.evaluate(() => { const a = document.activeElement; if (!a || a === document.body) return null; const b = a.getBoundingClientRect(); return { tag: a.tagName.toLowerCase(), text: (a.textContent || '').trim().slice(0, 24), left: Math.round(b.left), right: Math.round(b.right), inViewport: b.left >= 0 && b.right <= innerWidth }; }));
    }
    out[name].tab_sequence = seq;
    await page.screenshot({ path: `out/${name}-nav-after-tabs.png` });
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync('out/nav-results.json', JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out.w320, null, 1).slice(0, 4500));
  console.log('CONTROL nav links fully visible:', JSON.stringify(out.w1280_control.navs.map(n => n.links.every(l => l.fullyVisible))));
})().catch(e => { console.log('ERR', e.message.split('\n').slice(0, 3).join(' | ')); process.exit(1); });
