const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUTPUT_DIR = path.join(__dirname, 'screenshots');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// ─── IMPORTANT: All screenshots are 1920×1080 @ 1x scale = true 1080p ──────
// deviceScaleFactor: 1  → 1920×1080 final PNG (Full HD, NOT 4K/3K)
// deviceScaleFactor: 2  → would produce 3840×2160 (4K) — DO NOT USE

async function captureAll() {
  console.log('🚀 Launching Chromium for 1080p Hackathon Screenshot Capture...');
  const browser = await chromium.launch({ headless: true });

  // ─── DESKTOP CONTEXT: 1920×1080 @ 1x = True 1080p ──────────────────────
  const desktopContext = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,   // 1x = 1080p  (change to 2 = 4K, which we don't want)
    colorScheme: 'dark'
  });
  const page = await desktopContext.newPage();

  // ── Screenshot 1: Desktop Launchpad (Slide 1 & 2 hero image) ────────────
  console.log('📸 [1/6] Capturing Desktop Workstation & Launchpad...');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '01_desktop_launchpad.png') });
  console.log('   ✅ 01_desktop_launchpad.png  →  SLIDE 1 (Title) & SLIDE 2 (Problem) hero');

  // ── Screenshot 2: Grounded RAG Answer with KaTeX (Slide 3 & 5) ──────────
  console.log('📸 [2/6] Executing Agentic RAG Grounded Query (CIDR Subnetting)...');
  const trackBtn = await page.locator('button:has-text("CIDR Subnetting")').first();
  if (await trackBtn.count() > 0) {
    await trackBtn.click();
  } else {
    const anyCard = await page.locator('.grid button').first();
    await anyCard.click();
  }

  console.log('   Waiting for Agentic RAG answer, KaTeX math & citations...');
  try {
    await page.waitForSelector('button:has-text("Copy")', { timeout: 20000 });
  } catch (e) {
    await page.waitForTimeout(10000);
  }
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '02_desktop_grounded_answer.png') });
  console.log('   ✅ 02_desktop_grounded_answer.png  →  SLIDE 3 (RAG vs Agentic RAG) & SLIDE 5 (Demo)');

  // ── Screenshot 3: Source Inspector Drawer (Slide 4 & 5) ─────────────────
  console.log('📸 [3/6] Opening Agentic RAG Source Inspector Drawer...');
  const inspectBtn = await page.locator('button:has-text("Inspect Notes")').first();
  if (await inspectBtn.count() > 0) {
    await inspectBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(OUTPUT_DIR, '03_desktop_source_inspector.png') });
    console.log('   ✅ 03_desktop_source_inspector.png  →  SLIDE 4 (Architecture) & SLIDE 5 (Demo right frame)');

    const closeBtn = await page.locator('button:has-text("Close Drawer")').first();
    if (await closeBtn.count() > 0) {
      await closeBtn.click();
      await page.waitForTimeout(500);
    }
  } else {
    console.log('   ⚠️  Inspect Notes button not found — skipping screenshot 3');
  }

  // ── Screenshot 4: Upload / AST Ingestion Modal (Slide 6) ─────────────────
  console.log('📸 [4/6] Opening Study Material Upload & AST Ingestion Modal...');
  const uploadNavBtn = await page.locator('button:has-text("Upload Notes"), button:has-text("Upload")').first();
  if (await uploadNavBtn.count() > 0) {
    await uploadNavBtn.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, '04_desktop_upload_modal.png') });
    console.log('   ✅ 04_desktop_upload_modal.png  →  SLIDE 6 (Community Impact)');

    const closeUpload = await page.locator('button:has-text("Cancel")').first();
    if (await closeUpload.count() > 0) {
      await closeUpload.click();
    }
  } else {
    console.log('   ⚠️  Upload button not found — skipping screenshot 4');
  }

  await desktopContext.close();

  // ─── MOBILE CONTEXT: 390×844 logical px @ 1x scale ──────────────────────
  // Final PNG = 390×844 pixels. Keeps it HD-quality but mobile proportions.
  // We do NOT use deviceScaleFactor:3 which would produce 1170×2532 (3K).
  console.log('📸 [5/6] Capturing Mobile Workstation Viewport (1x scale)...');
  const mobileContext = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1,   // 1x = 390×844 final PNG (NOT 3K)
    isMobile: true,
    hasTouch: true,
    colorScheme: 'dark'
  });
  const mobilePage = await mobileContext.newPage();
  await mobilePage.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await mobilePage.waitForTimeout(1500);

  const mobilePrompt = await mobilePage.locator('.grid button:has-text("CIDR Subnetting")').first();
  if (await mobilePrompt.count() > 0) {
    await mobilePrompt.click();
  } else {
    const anyPrompt = await mobilePage.locator('.grid button').first();
    await anyPrompt.click();
  }

  try {
    await mobilePage.waitForSelector('button:has-text("Copy")', { timeout: 20000 });
  } catch (e) {
    await mobilePage.waitForTimeout(10000);
  }
  await mobilePage.waitForTimeout(3000);
  await mobilePage.screenshot({ path: path.join(OUTPUT_DIR, '05_mobile_workstation.png') });
  console.log('   ✅ 05_mobile_workstation.png  →  SLIDE 5 (Demo left frame — mobile view)');

  // ── Screenshot 6: Mobile Curriculum Timeline Drawer (Slide 7) ───────────
  console.log('📸 [6/6] Capturing Mobile Curriculum Slide-Over Drawer...');
  const mobileDrawerBtn = await mobilePage.locator(
    'button[aria-label="Open Syllabus Menu"], button[title*="Curriculum"], button[aria-label*="menu"], button[aria-label*="Menu"]'
  ).first();
  if (await mobileDrawerBtn.count() > 0) {
    await mobileDrawerBtn.click();
    await mobilePage.waitForTimeout(1000);
    await mobilePage.screenshot({ path: path.join(OUTPUT_DIR, '06_mobile_curriculum_drawer.png') });
    console.log('   ✅ 06_mobile_curriculum_drawer.png  →  SLIDE 7 (Future Vision)');
  } else {
    console.log('   ⚠️  Mobile drawer button not found — skipping screenshot 6');
  }

  await mobileContext.close();
  await browser.close();

  console.log('\n✨ All 1080p presentation screenshots captured!');
  console.log('📁 Saved in:', OUTPUT_DIR);
  console.log('\n📊 Screenshot → Slide Mapping:');
  console.log('   01_desktop_launchpad.png        → Slide 1 (Title/Hero) + Slide 2 (Problem)');
  console.log('   02_desktop_grounded_answer.png  → Slide 3 (RAG vs Agentic RAG) + Slide 5 (Demo)');
  console.log('   03_desktop_source_inspector.png → Slide 4 (Architecture) + Slide 5 (Demo right)');
  console.log('   04_desktop_upload_modal.png     → Slide 6 (Community Impact)');
  console.log('   05_mobile_workstation.png       → Slide 5 (Demo left frame)');
  console.log('   06_mobile_curriculum_drawer.png → Slide 7 (Future Vision)');
}

captureAll().catch(err => {
  console.error('❌ Screenshot capture failed:', err);
  process.exit(1);
});
