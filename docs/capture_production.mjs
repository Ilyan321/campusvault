/**
 * capture_production.mjs
 * Screenshots the LIVE production app at batchmate.ilyankhan.tech
 * All desktop shots: 1920x1080 @ deviceScaleFactor:1 = true 1080p
 * Mobile shots: 390x844 @ deviceScaleFactor:1
 */
import pwPkg from '/home/ilyan/ilmai/frontend/node_modules/playwright/index.js';
const { chromium } = pwPkg;
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, 'screenshots');
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

const PROD_URL = 'https://batchmate.ilyankhan.tech';

async function go() {
  console.log('🚀 Launching browser...');
  const browser = await chromium.launch({ headless: true });

  // ── DESKTOP 1920x1080 @ 1x ─────────────────────────────────────────────
  const desk = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    colorScheme: 'dark',
  });
  const page = await desk.newPage();

  // ── Screenshot 01: Homepage / Launchpad ──────────────────────────────────
  console.log('📸 [1/6] Loading production homepage...');
  await page.goto(PROD_URL, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(OUT, '01_desktop_launchpad.png') });
  console.log('   ✅ 01_desktop_launchpad.png  (1920x1080)');

  // ── Screenshot 02: Grounded RAG Answer ───────────────────────────────────
  console.log('📸 [2/6] Clicking a high-yield topic to trigger RAG answer...');
  const cidrBtn = page.locator('button:has-text("CIDR")').first();
  const anyBtn  = page.locator('button[class*="cursor"]').nth(3);
  if (await cidrBtn.count() > 0) {
    await cidrBtn.click();
  } else {
    await anyBtn.click();
  }
  // Wait for streaming answer — the backend is live so this should work
  try {
    await page.waitForSelector('button:has-text("Copy")', { timeout: 25000 });
    await page.waitForTimeout(3000); // Let it finish streaming
  } catch {
    await page.waitForTimeout(12000);
  }
  await page.screenshot({ path: path.join(OUT, '02_desktop_grounded_answer.png') });
  console.log('   ✅ 02_desktop_grounded_answer.png  (1920x1080)');

  // ── Screenshot 03: Source Inspector / Citations Drawer ───────────────────
  console.log('📸 [3/6] Opening source inspector drawer...');
  // Dump all button texts so we know what's available
  const btns = await page.locator('button').allTextContents();
  console.log('   Available buttons:', JSON.stringify(btns.map(b => b.trim()).filter(Boolean)));

  const sourceSelectors = [
    'button:has-text("Inspect Notes")',
    'button:has-text("Source")',
    'button:has-text("Inspect")',
    'button:has-text("Citations")',
    'button:has-text("View Source")',
    '[aria-label*="source" i]',
    '[aria-label*="inspect" i]',
  ];
  let opened = false;
  for (const sel of sourceSelectors) {
    const el = page.locator(sel).first();
    if (await el.count() > 0) {
      console.log(`   Found: ${sel}`);
      await el.click();
      await page.waitForTimeout(1500);
      opened = true;
      break;
    }
  }
  await page.screenshot({ path: path.join(OUT, '03_desktop_source_inspector.png') });
  console.log(`   ✅ 03_desktop_source_inspector.png  (drawer ${opened ? 'open' : 'not found — full page fallback'})`);

  // Close drawer if open
  const closeBtn = page.locator('button:has-text("Close"), [aria-label*="close" i]').first();
  if (await closeBtn.count() > 0) { await closeBtn.click(); await page.waitForTimeout(500); }

  // ── Screenshot 04: Upload Modal ───────────────────────────────────────────
  console.log('📸 [4/6] Opening upload modal...');
  const uploadBtn = page.locator('button:has-text("Upload")').first();
  if (await uploadBtn.count() > 0) {
    await uploadBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(OUT, '04_desktop_upload_modal.png') });
    console.log('   ✅ 04_desktop_upload_modal.png  (1920x1080)');
    const cancel = page.locator('button:has-text("Cancel"), button:has-text("Close")').first();
    if (await cancel.count() > 0) await cancel.click();
  } else {
    console.log('   ⚠️  Upload button not found');
  }

  await desk.close();

  // ── MOBILE 390x844 @ 1x ────────────────────────────────────────────────
  const mob = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1,
    isMobile: true,
    hasTouch: true,
    colorScheme: 'dark',
  });
  const mpage = await mob.newPage();

  // ── Screenshot 05: Mobile Workstation with Answer ──────────────────────
  console.log('📸 [5/6] Mobile — loading homepage...');
  await mpage.goto(PROD_URL, { waitUntil: 'networkidle', timeout: 30000 });
  await mpage.waitForTimeout(2000);
  const mCidr = mpage.locator('button:has-text("CIDR")').first();
  if (await mCidr.count() > 0) {
    await mCidr.click();
  } else {
    await mpage.locator('button').nth(5).click();
  }
  try {
    await mpage.waitForSelector('button:has-text("Copy")', { timeout: 25000 });
    await mpage.waitForTimeout(3000);
  } catch {
    await mpage.waitForTimeout(12000);
  }
  await mpage.screenshot({ path: path.join(OUT, '05_mobile_workstation.png') });
  console.log('   ✅ 05_mobile_workstation.png  (390x844)');

  // ── Screenshot 06: Mobile Curriculum Drawer ───────────────────────────
  console.log('📸 [6/6] Mobile curriculum drawer...');
  // Try hamburger / menu buttons
  const menuSelectors = [
    'button[aria-label*="menu" i]',
    'button[aria-label*="curriculum" i]',
    'button[aria-label*="syllabus" i]',
    'button[aria-label*="open" i]',
    '[data-testid*="menu"]',
    'button svg', // icon-only button
  ];
  let menuOpened = false;
  for (const sel of menuSelectors) {
    const el = mpage.locator(sel).first();
    if (await el.count() > 0) {
      await el.click();
      await mpage.waitForTimeout(1000);
      const vis = await mpage.locator('[role="dialog"], aside, [class*="drawer"], [class*="sidebar"]').count();
      if (vis > 0) { menuOpened = true; break; }
    }
  }
  await mpage.screenshot({ path: path.join(OUT, '06_mobile_curriculum_drawer.png') });
  console.log(`   ✅ 06_mobile_curriculum_drawer.png  (drawer ${menuOpened ? 'open' : 'fallback'})`);

  await mob.close();
  await browser.close();

  console.log('\n✨ All screenshots captured from PRODUCTION (real styles, real data)');
  console.log('📁', OUT);
  console.log('\n📊 Slide → Screenshot:');
  console.log('   Slide 1 (Title)       → 01_desktop_launchpad.png');
  console.log('   Slide 2 (Problem)     → 01_desktop_launchpad.png');
  console.log('   Slide 3 (Agentic RAG) → 02_desktop_grounded_answer.png');
  console.log('   Slide 4 (Pipeline)    → 03_desktop_source_inspector.png');
  console.log('   Slide 5 (Demo)        → 05_mobile_workstation.png + 03_desktop_source_inspector.png');
  console.log('   Slide 6 (Community)   → 04_desktop_upload_modal.png');
  console.log('   Slide 7 (Roadmap)     → 06_mobile_curriculum_drawer.png');
}

go().catch(e => { console.error('❌', e.message); process.exit(1); });
