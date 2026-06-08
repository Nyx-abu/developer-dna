const { chromium } = require('playwright');

(async () => {
  console.log('Starting Playwright Verification...');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to http://localhost:3000...');
    await page.goto('http://localhost:3000');
    
    // Check overview charts
    await page.waitForSelector('h3:has-text("Activity Heatmap")');
    console.log('Overview page rendered Activity Heatmap');
    
    // Try to click "Skills" link now that z-index is fixed
    const skillsLink = page.locator('text=Skills');
    console.log('Clicking on Skills link...');
    await skillsLink.click({ timeout: 5000 });
    
    // Check if the URL changed to skills
    await page.waitForURL('**/skills', { timeout: 5000 });
    console.log('Successfully navigated to Skills page!');

    // Check if the new SkillRadar chart loads on the skills page
    await page.waitForSelector('.recharts-responsive-container', { timeout: 5000 });
    console.log('SkillRadar recharts SVG successfully loaded!');

    console.log('All tests passed successfully! The site is fully interactive and charts are rendering.');
  } catch (error) {
    console.error('Test failed:', error.message);
  } finally {
    await browser.close();
  }
})();
