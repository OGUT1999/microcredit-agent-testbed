// Local-source 320 vs 1280 check of the Omnequa partners page (pinned vision d66b126 dist, served on localhost only).
const { chromium } = require('/opt/node-tools/node_modules/playwright-core');
const fs = require('fs');
const OUT = process.argv[2];
const obs = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const inputs = obs.synthetic_inputs, labels = obs.field_labels;
const order = Object.keys(inputs);
const reminder = 'Please review and remove private worker records before sending.';
const expectedBrief = order.map(k => labels[k] + ':\n' + inputs[k] + '\n').join('\n') + '\n' + reminder + '\n';
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const results = { browser_version: browser.version(), runs: {} };
  for (const [name, vp] of [['w1280_control', { width: 1280, height: 800 }], ['w320', { width: 320, height: 640 }]]) {
    const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, permissions: ['clipboard-read', 'clipboard-write'], baseURL: 'http://127.0.0.1:8765' });
    const page = await ctx.newPage();
    const requests = [], blocked = [], consoleMsgs = [], pageErrors = [];
    page.on('console', m => consoleMsgs.push({ type: m.type(), text: m.text().slice(0, 200) }));
    page.on('pageerror', e => pageErrors.push(String(e).slice(0, 200)));
    await page.route('**/*', r => {
      const u = r.request().url();
      if (u.startsWith('http://127.0.0.1:8765/') || u.startsWith('data:')) { requests.push(u); r.continue(); } else { blocked.push(u); r.abort(); }
    });
    const R = { viewport: vp };
    await page.goto('/partners/', { waitUntil: 'load' });
    const metrics = async () => page.evaluate(() => {
      const de = document.documentElement, vw = window.innerWidth;
      const wide = [];
      for (const el of document.querySelectorAll('body *')) {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && (r.right > vw + 0.5 || r.left < -0.5)) wide.push({ tag: el.tagName.toLowerCase(), id: el.id || null, cls: (el.className && el.className.toString().slice(0, 40)) || null, left: Math.round(r.left), right: Math.round(r.right), width: Math.round(r.width) });
      }
      return { innerWidth: vw, clientWidth: de.clientWidth, scrollWidth: de.scrollWidth, bodyScrollWidth: document.body.scrollWidth, horizontalScroll: de.scrollWidth > de.clientWidth, dpr: devicePixelRatio, overflowingElementCount: wide.length, overflowingElements: wide.slice(0, 12) };
    });
    R.initial = await metrics();
    await page.screenshot({ path: `${OUT}/${name}-initial-viewport.png` });
    for (const k of order) await page.fill('#' + k, inputs[k]);
    R.button_enabled_after_fill = await page.evaluate(() => !document.getElementById('prepare-draft').disabled);
    await page.focus('#prepare-draft');
    await page.keyboard.press('Enter');
    await page.waitForFunction(() => !document.getElementById('plain-draft-panel').hidden, null, { timeout: 5000 }).catch(() => {});
    const brief = await page.evaluate(() => ({ panelHidden: document.getElementById('plain-draft-panel').hidden, value: document.getElementById('plain-draft').value, status: document.getElementById('draft-status').textContent, linkHidden: document.getElementById('email-draft-link').hidden, href: document.getElementById('email-draft-link').getAttribute('href') }));
    R.prepare = { panel_visible: !brief.panelHidden, brief_equals_expected: brief.value === expectedBrief, brief_utf16_units: brief.value.length, status: brief.status, link_visible: !brief.linkHidden, href_present: brief.href !== null };
    R.after_prepare = await metrics();
    await page.locator('#plain-draft').scrollIntoViewIfNeeded();
    await page.screenshot({ path: `${OUT}/${name}-prepared-viewport.png` });
    await page.screenshot({ path: `${OUT}/${name}-prepared-fullpage.png`, fullPage: true });
    // actual keyboard copy of the readonly brief, read from clipboard
    await page.focus('#plain-draft');
    await page.keyboard.press('Control+a'); await page.keyboard.press('Control+c');
    const clip = await page.evaluate(() => navigator.clipboard.readText());
    R.copy = { clipboard_equals_expected: clip === expectedBrief, clipboard_utf16_units: clip.length };
    // edit invalidation
    await page.focus('#employer'); await page.keyboard.press('End'); await page.keyboard.type('X');
    const inv = await page.evaluate(() => ({ value: document.getElementById('plain-draft').value, panelHidden: document.getElementById('plain-draft-panel').hidden, linkHidden: document.getElementById('email-draft-link').hidden, href: document.getElementById('email-draft-link').getAttribute('href'), status: document.getElementById('draft-status').textContent }));
    R.edit_invalidation = { brief_cleared: inv.value === '', panel_hidden: inv.panelHidden, link_hidden: inv.linkHidden, href_removed: inv.href === null, status: inv.status };
    // reprepare then reload cleanup
    await page.fill('#employer', inputs.employer);
    await page.focus('#prepare-draft'); await page.keyboard.press('Enter');
    R.reprepare_equals_expected = await page.evaluate((e) => document.getElementById('plain-draft').value === e, expectedBrief);
    await page.reload({ waitUntil: 'load' });
    R.reload = await page.evaluate((ids) => ({ fields_empty: ids.every(i => document.getElementById(i).value === ''), panel_hidden: document.getElementById('plain-draft-panel').hidden, link_hidden: document.getElementById('email-draft-link').hidden, href_null: document.getElementById('email-draft-link').getAttribute('href') === null }), order);
    R.network = { localhost_requests: requests.length, external_blocked_requests: blocked, mailto_activated: false };
    R.console = { messages: consoleMsgs, page_errors: pageErrors };
    results.runs[name] = R;
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(`${OUT}/results.json`, JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 1).slice(0, 6000));
})().catch(e => { console.log('ERR', e.message.split('\n').slice(0, 3).join(' | ')); process.exit(1); });
