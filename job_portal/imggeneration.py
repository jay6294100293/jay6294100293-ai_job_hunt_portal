# template_screenshots.py
import asyncio
from playwright.async_api import async_playwright
import os
import sys
import django
from django.core.management import call_command

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_job_hunt.settings')
django.setup()


async def capture_template_screenshots(output_dir='template_images', base_url='http://localhost:8000'):
    """
    Capture screenshots of all resume templates using Playwright.

    Args:
        output_dir: Directory where images will be saved
        base_url: Base URL of your running Django development server
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()

        # Create a context with specific viewport size
        # A4 aspect ratio at reasonable pixel density
        context = await browser.new_context(
            viewport={'width': 384, 'height': 250}  # ~A4 dimensions at 150 DPI
        )

        # Create a new page
        page = await context.new_page()

        # Capture screenshots for each template (adjust range as needed)
        for template_id in range(1, 7):  # For templates 1-6
            try:
                # Navigate to template preview URL
                template_url = f"{base_url}/preview-template/{template_id}/"
                print(f"Navigating to {template_url}")

                await page.goto(template_url, wait_until='networkidle')

                # Wait additional time for any lazy-loaded content or fonts
                await page.wait_for_timeout(1000)

                # Capture screenshot
                screenshot_path = os.path.join(output_dir, f"template_{template_id}.png")

                # Take full page screenshot
                await page.screenshot(path=screenshot_path, clip={'x': 0, 'y': 0, 'width': 384, 'height': 250})

                print(f"✓ Captured template {template_id} - saved to {screenshot_path}")

            except Exception as e:
                print(f"❌ Error capturing template {template_id}: {e}")

        # Close browser
        await browser.close()

        print(f"\nAll screenshots saved to {os.path.abspath(output_dir)}")


# To run this script directly
if __name__ == "__main__":
    # Get output directory from command line if provided
    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'template_images'

    # Get base URL from command line if provided
    base_url = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:8000/job'

    # Ensure the development server is running
    print("Make sure your Django development server is running!")
    print(f"Expected URL: {base_url}/preview-template/1/")

    # Run the screenshot function
    asyncio.run(capture_template_screenshots(output_dir, base_url))