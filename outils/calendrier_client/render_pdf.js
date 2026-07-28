const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');

const HEADER_TEMPLATE = `
<div style="font-family:Inter,Arial,sans-serif;font-size:7.5px;color:#1B2D5C;width:100%;
            padding:6px 15mm 4px;display:flex;justify-content:space-between;align-items:center;
            border-bottom:1px solid #F37021;box-sizing:border-box">
  <span style="font-weight:800;letter-spacing:.3px">EXCELLENCE+ — CALENDRIER ÉDITORIAL CLIENT</span>
  <span style="color:#9CA0A8">AORA × EXCELLENCE+ · CC-EXC-001 · Extrait août-septembre 2026</span>
</div>`;

const FOOTER_TEMPLATE = `
<div style="font-family:Inter,Arial,sans-serif;font-size:7.5px;color:#1B2D5C;width:100%;
            padding:4px 15mm 6px;display:flex;justify-content:space-between;align-items:center;
            border-top:1px solid #F37021;box-sizing:border-box">
  <span style="color:#9CA0A8">AORA Communication Agency — L'EXCELLENCE À VOTRE PORTÉE.</span>
  <span style="font-weight:800">PAGE <span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>`;

(async () => {
  const inputPath = process.argv[2];
  const outputPath = process.argv[3];
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + path.resolve(inputPath), { waitUntil: 'networkidle' });
  await page.pdf({
    path: outputPath,
    format: 'A4',
    landscape: true,
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: HEADER_TEMPLATE,
    footerTemplate: FOOTER_TEMPLATE,
    margin: { top: '14mm', bottom: '12mm', left: '0mm', right: '0mm' },
  });
  await browser.close();
  if (errors.length) {
    console.error('JS errors during render:', errors);
    process.exit(1);
  }
  console.log('PDF written:', outputPath);
})();
