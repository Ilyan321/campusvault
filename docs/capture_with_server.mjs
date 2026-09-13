// Starts Vite dev server, waits for it, then captures screenshots, then kills Vite
import { createServer } from '/home/ilyan/ilmai/frontend/node_modules/vite/dist/node/index.js';
import pwPkg from '/home/ilyan/ilmai/frontend/node_modules/playwright/index.js';
const { chromium } = pwPkg;
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUTPUT_DIR = path.join(__dirname, 'screenshots');
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

async function main() {
  console.log('🚀 Starting Vite dev server...');
  const server = await createServer({
    root: path.join(__dirname, '../frontend'),
    server: { port: 5173 }
  });
  await server.listen();
  server.printUrls();
  await new Promise(r => setTimeout(r, 2000)); // Let it fully boot

  console.log('\n📸 Launching Chromium for 1080p screenshot capture...');
  const browser = await chromium.launch({ headless: true });

  // ─── DESKTOP 1920×1080 @ 1x = True 1080p ───────────────────────────────
  const desktopCtx = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    colorScheme: 'dark'
  });
  const page = await desktopCtx.newPage();

  // Screenshot 1 — Desktop Launchpad
  console.log('📸 [1/6] Desktop Launchpad (Slide 1 & 2)...');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '01_desktop_launchpad.png') });
  console.log('   ✅ 01_desktop_launchpad.png');

  // Screenshot 2 — Grounded RAG Answer
  console.log('📸 [2/6] Agentic RAG Grounded Answer (Slide 3 & 5)...');
  const cidrBtn = page.locator('button:has-text("CIDR Subnetting")').first();
  if (await cidrBtn.count() > 0) {
    await cidrBtn.click();
  } else {
    await page.locator('.grid button').first().click();
  }
  try {
    await page.waitForSelector('button:has-text("Copy")', { timeout: 20000 });
  } catch { await page.waitForTimeout(10000); }
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '02_desktop_grounded_answer.png') });
  console.log('   ✅ 02_desktop_grounded_answer.png');

  // Screenshot 3 — Source Inspector
  console.log('📸 [3/6] Source Inspector Drawer (Slide 4 & 5)...');
  const inspectBtn = page.locator('button:has-text("Inspect Notes")').first();
  if (await inspectBtn.count() > 0) {
    await inspectBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(OUTPUT_DIR, '03_desktop_source_inspector.png') });
    console.log('   ✅ 03_desktop_source_inspector.png');
    const closeBtn = page.locator('button:has-text("Close Drawer")').first();
    if (await closeBtn.count() > 0) { await closeBtn.click(); await page.waitForTimeout(500); }
  } else {
    console.log('   ⚠️  Inspect Notes not found');
  }

  // Screenshot 4 — Upload Modal
  console.log('📸 [4/6] Upload Modal (Slide 6)...');
  const uploadBtn = page.locator('button:has-text("Upload Notes"), button:has-text("Upload")').first();
  if (await uploadBtn.count() > 0) {
    await uploadBtn.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, '04_desktop_upload_modal.png') });
    console.log('   ✅ 04_desktop_upload_modal.png');
    const cancel = page.locator('button:has-text("Cancel")').first();
    if (await cancel.count() > 0) await cancel.click();
  }
  await desktopCtx.close();

  // ─── MOBILE 390×844 @ 1x ─────────────────────────────────────────────────
  const mobileCtx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1,
    isMobile: true,
    hasTouch: true,
    colorScheme: 'dark'
  });
  const mob = await mobileCtx.newPage();
  await mob.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await mob.waitForTimeout(1500);

  const mobilePrompt = mob.locator('.grid button:has-text("CIDR Subnetting")').first();
  if (await mobilePrompt.count() > 0) {
    await mobilePrompt.click();
  } else {
    await mob.locator('.grid button').first().click();
  }
  try {
    await mob.waitForSelector('button:has-text("Copy")', { timeout: 20000 });
  } catch { await mob.waitForTimeout(10000); }
  await mob.waitForTimeout(3000);

  // Screenshot 5 — Mobile Workstation
  console.log('📸 [5/6] Mobile Workstation (Slide 5 left frame)...');
  await mob.screenshot({ path: path.join(OUTPUT_DIR, '05_mobile_workstation.png') });
  console.log('   ✅ 05_mobile_workstation.png');

  // Screenshot 6 — Mobile Curriculum Drawer
  console.log('📸 [6/6] Mobile Curriculum Drawer (Slide 7)...');
  const drawerBtn = mob.locator(
    'button[aria-label="Open Syllabus Menu"], button[title*="Curriculum"], button[aria-label*="menu"], button[aria-label*="Menu"]'
  ).first();
  if (await drawerBtn.count() > 0) {
    await drawerBtn.click();
    await mob.waitForTimeout(1000);
    await mob.screenshot({ path: path.join(OUTPUT_DIR, '06_mobile_curriculum_drawer.png') });
    console.log('   ✅ 06_mobile_curriculum_drawer.png');
  } else {
    console.log('   ⚠️  Mobile drawer button not found');
  }
  await mobileCtx.close();

  await browser.close();
  await server.close();

  console.log('\n✨ All 1080p screenshots captured!');
  console.log('📁 Output:', OUTPUT_DIR);
  console.log('\n📊 Slide → Screenshot Mapping:');
  console.log('   Slide 1 (Title)       → 01_desktop_launchpad.png');
  console.log('   Slide 2 (Problem)     → 01_desktop_launchpad.png (split layout)');
  console.log('   Slide 3 (Agentic RAG) → 02_desktop_grounded_answer.png');
  console.log('   Slide 4 (Pipeline)    → 03_desktop_source_inspector.png');
  console.log('   Slide 5 (Demo)        → 05_mobile_workstation.png + 03_desktop_source_inspector.png');
  console.log('   Slide 6 (Community)   → 04_desktop_upload_modal.png');
  console.log('   Slide 7 (Roadmap)     → 06_mobile_curriculum_drawer.png');
}

main().catch(err => {
  console.error('❌ Failed:', err.message);
  process.exit(1);
});
