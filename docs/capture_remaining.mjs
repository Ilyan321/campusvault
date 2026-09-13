/**
 * capture_remaining.mjs — captures 02, 04, 05, 06 properly
 * 02: Actually submits a query via the text input and waits for streamed answer
 * 04: Upload modal
 * 05: Mobile with answer
 * 06: Mobile curriculum drawer
 */
import pwPkg from '/home/ilyan/ilmai/frontend/node_modules/playwright/index.js';
const { chromium } = pwPkg;
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, 'screenshots');
const PROD = 'https://batchmate.ilyankhan.tech';

async function go() {
  const browser = await chromium.launch({ headless: true });

  // ── DESKTOP ─────────────────────────────────────────────────────────────
  const desk = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    colorScheme: 'dark',
  });
  const page = await desk.newPage();
  await page.goto(PROD, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(2000);

  // ── Screenshot 02: Type query directly into textarea & submit ────────────
  console.log('📸 [02] Typing CIDR query into input and submitting...');
  const textarea = page.locator('textarea').first();
  await textarea.fill('How do you calculate usable host IPs in a CIDR /26 subnet? Show the binary math and formula.');
  await page.waitForTimeout(500);
  // Press Enter to submit
  await page.keyboard.press('Enter');

  // Wait for streaming — look for the answer text appearing
  console.log('   Waiting for RAG answer to stream...');
  try {
    // Wait until we see actual answer content (not just the welcome message)
    await page.waitForFunction(() => {
      const msgs = document.querySelectorAll('[class*="message"], [class*="answer"], [class*="response"], p');
      for (const m of msgs) {
        if (m.textContent && m.textContent.length > 200 && m.textContent.includes('subnet')) return true;
      }
      return false;
    }, { timeout: 30000 });
    await page.waitForTimeout(3000); // Let streaming finish
  } catch {
    await page.waitForTimeout(15000);
  }
  await page.screenshot({ path: path.join(OUT, '02_desktop_grounded_answer.png') });
  console.log('   ✅ 02_desktop_grounded_answer.png');

  // ── Screenshot 03: Click "Source" button now that answer is shown ────────
  console.log('📸 [03] Opening Source inspector...');
  const sourceBtn = page.locator('button:has-text("Source")').first();
  if (await sourceBtn.count() > 0) {
    await sourceBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(OUT, '03_desktop_source_inspector.png') });
    console.log('   ✅ 03_desktop_source_inspector.png');
    // Press Escape to close instead of clicking Close button
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
  }

  // ── Screenshot 04: Upload Modal ─────────────────────────────────────────
  console.log('📸 [04] Opening Upload modal...');
  const uploadBtn = page.locator('button:has-text("Upload")').first();
  if (await uploadBtn.count() > 0) {
    await uploadBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(OUT, '04_desktop_upload_modal.png') });
    console.log('   ✅ 04_desktop_upload_modal.png');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);
  }

  await desk.close();

  // ── MOBILE ──────────────────────────────────────────────────────────────
  const mob = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1,
    isMobile: true,
    hasTouch: true,
    colorScheme: 'dark',
  });
  const mpage = await mob.newPage();
  await mpage.goto(PROD, { waitUntil: 'networkidle', timeout: 30000 });
  await mpage.waitForTimeout(2000);

  // Type and submit on mobile too
  console.log('📸 [05] Mobile — submitting query...');
  const mTextarea = mpage.locator('textarea').first();
  await mTextarea.fill('How do you calculate usable host IPs in a CIDR /26 subnet?');
  await mpage.keyboard.press('Enter');
  try {
    await mpage.waitForFunction(() => {
      const msgs = document.querySelectorAll('p, [class*="message"]');
      for (const m of msgs) {
        if (m.textContent && m.textContent.length > 200) return true;
      }
      return false;
    }, { timeout: 30000 });
    await mpage.waitForTimeout(3000);
  } catch {
    await mpage.waitForTimeout(15000);
  }
  await mpage.screenshot({ path: path.join(OUT, '05_mobile_workstation.png') });
  console.log('   ✅ 05_mobile_workstation.png');

  // ── Screenshot 06: Mobile Curriculum Drawer ──────────────────────────────
  console.log('📸 [06] Mobile curriculum drawer...');
  // The drawer button is usually a hamburger in the top-left on mobile
  // Try clicking visible buttons that might open the sidebar
  const allBtns = await mpage.locator('button').all();
  let drawerOpened = false;
  for (const btn of allBtns.slice(0, 5)) {
    const box = await btn.boundingBox();
    if (box && box.x < 60 && box.y < 100) { // top-left area = hamburger
      await btn.click();
      await mpage.waitForTimeout(1000);
      const sidebar = await mpage.locator('aside, [role="dialog"], [class*="drawer"], [class*="sidebar"]').count();
      if (sidebar > 0) { drawerOpened = true; break; }
    }
  }
  if (!drawerOpened) {
    // Try swiping from left edge to open drawer
    await mpage.touchscreen.tap(10, 400);
    await mpage.waitForTimeout(800);
  }
  await mpage.screenshot({ path: path.join(OUT, '06_mobile_curriculum_drawer.png') });
  console.log(`   ✅ 06_mobile_curriculum_drawer.png (drawer: ${drawerOpened})`);

  await mob.close();
  await browser.close();
  console.log('\n✨ Done! Check screenshots folder.');
}

go().catch(e => { console.error('❌', e.message); process.exit(1); });
