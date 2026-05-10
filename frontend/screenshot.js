const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  console.log("Navigating to dashboard...");
  await page.goto('http://localhost:3000');
  
  // Wait for Launch Auditor button and click
  await page.waitForSelector('button');
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const launchBtn = buttons.find(b => b.textContent.includes('Launch Auditor'));
    if (launchBtn) launchBtn.click();
  });
  
  // Wait for upload input
  await page.waitForSelector('input[type="file"]');
  const inputUploadHandle = await page.$('input[type="file"]');
  await inputUploadHandle.uploadFile('C:/Users/atrij/OneDrive/Desktop/WK_VibeCode/Test/vulnerable.tf');

  console.log("Waiting for analysis...");
  // Wait for results
  await page.waitForSelector('.recharts-wrapper', { timeout: 60000 });
  
  // Wait for 3 seconds for animations
  await new Promise(r => setTimeout(r, 3000));

  console.log("Taking Dashboard screenshot...");
  await page.screenshot({ path: '../Output/dashboard.png', fullPage: true });

  console.log("Taking Findings screenshot...");
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const btn = buttons.find(b => b.textContent.includes('Findings'));
    if (btn) btn.click();
  });
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: '../Output/findings.png', fullPage: true });

  console.log("Taking Attack Chains screenshot...");
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const btn = buttons.find(b => b.textContent.includes('Attack Chains'));
    if (btn) btn.click();
  });
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: '../Output/attack_chains.png', fullPage: true });

  console.log("Taking Compliance screenshot...");
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const btn = buttons.find(b => b.textContent.includes('Compliance'));
    if (btn) btn.click();
  });
  await new Promise(r => setTimeout(r, 1000));
  await page.screenshot({ path: '../Output/compliance.png', fullPage: true });

  await browser.close();
  console.log("Done");
})();
