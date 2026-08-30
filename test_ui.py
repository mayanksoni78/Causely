import asyncio
from playwright.async_api import async_playwright
import uuid
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        print("1. Navigating to Dashboard...")
        await page.goto("http://localhost:5174/")
        await page.wait_for_timeout(2000)

        # Check if we are on Login page (redirected)
        if "/login" in page.url:
            print("2. Filling out Registration...")
            await page.screenshot(path="auth_before.png")
            
            # Click "Create one free"
            if await page.locator("text=Create one free").count() > 0:
                await page.click("text=Create one free")
                await page.wait_for_timeout(1000)
                
            email = f"test_{uuid.uuid4().hex[:8]}@example.com"
            
            # Find inputs. In the snippet they have ids. Let's use placeholders or generic
            # Signup inputs usually have specific ids or types.
            inputs = await page.locator("input").element_handles()
            
            # 1. Name, 2. Email, 3. Pwd, 4. Confirm Pwd
            await page.fill("input[type='email']", email)
            # Find name by type="text"
            text_inputs = await page.locator("input[type='text']").element_handles()
            if text_inputs:
                await text_inputs[0].fill("Test User")
                
            pwd_inputs = await page.locator("input[type='password']").element_handles()
            if len(pwd_inputs) >= 2:
                await pwd_inputs[0].fill("password123")
                await pwd_inputs[1].fill("password123")
                
            await page.screenshot(path="auth_filled.png")
            await page.click("button:has-text('Create Account')")
            await page.wait_for_timeout(3000)
            
            # Check if we need to create a project
            if await page.locator("text=Create Project").count() > 0 or await page.locator("text=New Project").count() > 0:
                print("2.5 Creating project...")
                await page.fill("input[placeholder*='Project']", "Car Rental Test")
                # sometimes button is "Create" or "Create Project"
                if await page.locator("button:has-text('Create')").count() > 0:
                    await page.click("button:has-text('Create')")
                else:
                    await page.keyboard.press("Enter")
                await page.wait_for_timeout(2000)

        await page.screenshot(path="dashboard_after_login.png")

        print("3. Navigating to Sources...")
        await page.click("a[href='/sources']")
        await page.wait_for_timeout(2000)
        
        print("4. Adding GitHub Source...")
        # Expand accordion if necessary
        try:
            await page.click("text=Code Repositories")
            await page.wait_for_timeout(500)
        except:
            pass

        await page.click("button:has-text('Connect'):near(:text('GitHub'))")
        await page.wait_for_timeout(1000)
        
        # Fill repo URL
        await page.fill("input[type='text']", "https://github.com/mayanksoni78/Car_Rental")
        # Token is optional now, leaving it empty
        await page.click("button:has-text('Connect Source')")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="sources.png")

        print("5. Submitting Incident...")
        await page.click("a[href='/incidents/new']")
        await page.wait_for_timeout(2000)
        
        inputs = await page.locator("input[type='text']").element_handles()
        if inputs:
            await inputs[0].fill("Razorpay Payment Failure")
        else:
            await page.keyboard.type("Razorpay Payment Failure")
            
        desc = """Investigate a payment failure in the Car Rental application.

Users are unable to complete Razorpay payments. During checkout, the browser console shows an ERR_BLOCKED_BY_CLIENT error for lumberjack.razorpay.com/v2/logz and an "Unrecognized feature: otp-credentials" warning. At the same time, the backend logs show that the Razorpay order creation request is failing.

log fileRAZORPAY_KEY_ID=rzp_test_SqSwR2y2vTKsum
RAZORPAY_KEY_SECRET=14cmEKHkC2wsYRrM03kAb02u,"""
        await page.fill("textarea", desc)
        
        await page.screenshot(path="incident_form.png")
        await page.click("button:has-text('Start Investigation')")
        print("6. Waiting for investigation to complete...")
        
        # Wait up to 60s for the investigation to finish
        for _ in range(40):
            await page.wait_for_timeout(2000)
            text = await page.content()
            if "Insufficient evidence" in text or "Verified Hypotheses" in text or "INSUFFICIENT_EVIDENCE" in text:
                break
        
        await page.screenshot(path="investigation_result.png")
        print("Done! Screenshots saved.")
        
        import shutil
        app_dir = r"C:\Users\mayan\.gemini\antigravity\brain\f12dafce-a356-4459-b8f0-024e6375d09a\.user_uploaded"
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
            
        shutil.copy("investigation_result.png", os.path.join(app_dir, "investigation_result.png"))
        shutil.copy("dashboard_after_login.png", os.path.join(app_dir, "dashboard_after_login.png"))
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
