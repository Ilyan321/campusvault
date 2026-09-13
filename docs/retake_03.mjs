// Targeted retake of screenshot 03 — source inspector
// Tries multiple button selectors to find the Inspect Notes / source drawer button
import { createServer } from '/home/ilyan/ilmai/frontend/node_modules/vite/dist/node/index.js';
import pwPkg from '/home/ilyan/ilmai/frontend/node_modules/playwright/index.js';
const { chromium } = pwPkg;
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUTPUT = path.join(__dirname, 'screenshots', '03_desktop_source_inspector.png');

async function main() {
  console.log('🚀 Starting Vite...');
  const server = await createServer({
    root: path.join(__dirname, '../frontend'),
    server: { port: 5173 }
  });
  await server.listen();
  await new Promise(r => setTimeout(r, 2000));

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    colorScheme: 'dark'
  });
  const page = await ctx.newPage();

  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Click a high-yield prompt to trigger a RAG answer
  const cidrBtn = page.locator('button:has-text("CIDR Subnetting")').first();
  if (await cidrBtn.count() > 0) {
    await cidrBtn.click();
  } else {
    const anyBtn = page.locator('.grid button').first();
    if (await anyBtn.count() > 0) await anyBtn.click();
  }

  // Wait for the answer to stream in (up to 25s)
  try {
    await page.waitForSelector('button:has-text("Copy")', { timeout: 25000 });
  } catch {
    await page.waitForTimeout(12000);
  }
  await page.waitForTimeout(3000);

  // Debug: dump all visible button texts
  const buttons = await page.locator('button').allTextContents();
  console.log('Visible buttons:', buttons.slice(0, 20));

  // Try many possible selectors for the inspect/source drawer button
  const selectors = [
    'button:has-text("Inspect Notes")',
    'button:has-text("Inspect")',
    'button:has-text("View Source")',
    'button:has-text("Sources")',
    'button:has-text("Citations")',
    'button:has-text("View Notes")',
    'button:has-text("Source")',
    '[aria-label*="inspect" i]',
    '[aria-label*="source" i]',
    '[title*="inspect" i]',
    '[title*="source" i]',
  ];

  let found = false;
  for (const sel of selectors) {
    const el = page.locator(sel).first();
    if (await el.count() > 0) {
      console.log(`✅ Found button with selector: ${sel}`);
      await el.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: OUTPUT });
      console.log('✅ 03_desktop_source_inspector.png captured at 1920x1080!');
      found = true;
      break;
    }
  }

  if (!found) {
    console.log('⚠️  No source inspector button found. Taking full-page screenshot of grounded answer as fallback.');
    await page.screenshot({ path: OUTPUT });
    console.log('Fallback screenshot saved.');
  }

  await ctx.close();
  await browser.close();
  await server.close();
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
