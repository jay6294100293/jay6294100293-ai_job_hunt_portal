# job_portal/imggeneration.py
import asyncio
from playwright.async_api import async_playwright
import os
import sys
import django
from django.urls import reverse  # For resolving URLs
# from django.conf import settings # Not strictly needed if output path is relative or constructed from PROJECT_ROOT
import traceback

# --- Corrected Django Environment Setup ---
# Get the absolute path to the directory containing manage.py (your project root)
# This script is in job_portal/, so ../ moves up one level to the project root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set the DJANGO_SETTINGS_MODULE environment variable
# Your settings file is in ai_job_hunt_portal/settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_job_hunt_portal.settings')
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"sys.path: {sys.path}")
    print(
        "Ensure you are running this script from the project root directory (e.g., E:\\PYCHARM_PROJECTS\\ai_job_hunt_portal) or that DJANGO_SETTINGS_MODULE is correctly set.")
    sys.exit(1)


# --- End Django Environment Setup ---


async def capture_template_screenshots(output_dir_name='resume_thumbnails', base_url='http://127.0.0.1:8000',
                                       resume_id_for_preview=1):
    """
    Capture screenshots of all resume templates using Playwright.

    Args:
        output_dir_name: Name of the directory (within static/img) where images will be saved.
        base_url: Base URL of your running Django development server.
        resume_id_for_preview: The ID of a Resume object to use for generating previews.
                               This resume should have representative data.
    """
    output_dir_path = os.path.join(PROJECT_ROOT, 'static', 'img', output_dir_name)

    os.makedirs(output_dir_path, exist_ok=True)
    print(f"Attempting to save screenshots to: {os.path.abspath(output_dir_path)}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={'width': 1200, 'height': 1697}
        )
        page = await context.new_page()

        for template_id in range(1, 7):
            actual_template_id_for_url = template_id
            template_url = "COULD_NOT_REVERSE_URL"
            try:
                path_to_view = reverse('job_portal:view_resume', kwargs={'resume_id': resume_id_for_preview})
                clean_base_url = base_url.rstrip('/')
                template_url = f"{clean_base_url}{path_to_view}?template={actual_template_id_for_url}"

                print(f"Navigating to {template_url}")

                await page.goto(template_url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(4000)  # Increased wait for rendering, fonts, etc.

                screenshot_filename = f"template{template_id}.png"
                screenshot_path = os.path.join(output_dir_path, screenshot_filename)

                # Adjusted clip region for better thumbnail preview.
                # You might need to fine-tune these values based on your template's actual rendered appearance.
                # The goal is to get a representative top portion.
                clip_region = {'x': 0, 'y': 0, 'width': 480,
                               'height': 680}  # Slightly larger for better detail if scaled down

                await page.screenshot(path=screenshot_path, clip=clip_region)

                print(f"✓ Captured template {template_id} - saved to {screenshot_path}")

            except Exception as e:
                print(f"❌ Error capturing template {template_id} (Attempted URL: {template_url}): {e}")
                traceback.print_exc()

        await browser.close()
        print(f"\nAll screenshot attempts complete. Check directory: {os.path.abspath(output_dir_path)}")


async def main():
    output_dir_arg = sys.argv[1] if len(sys.argv) > 1 else 'resume_thumbnails'
    base_url_arg = sys.argv[2] if len(sys.argv) > 2 else 'http://127.0.0.1:8000'
    try:
        resume_id_arg = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    except ValueError:
        print("Error: resume_id (3rd argument) must be an integer. Using default ID 1.")
        resume_id_arg = 1

    print("--- Resume Template Screenshot Generator ---")
    print(f"Output directory name: '{output_dir_arg}' (will be inside 'PROJECT_ROOT/static/img/')")
    print(f"Base URL for Django server: {base_url_arg}")
    print(f"Using Resume ID for preview: {resume_id_arg}")
    print("\nIMPORTANT:")
    print(f"1. Ensure your Django development server is running at '{base_url_arg}'.")
    print(f"2. Ensure a Resume with ID '{resume_id_arg}' exists and has representative data.")
    print(
        f"3. Ensure the output directory '{os.path.join(PROJECT_ROOT, 'static', 'img', output_dir_arg)}' is writable.\n")

    await capture_template_screenshots(output_dir_name=output_dir_arg, base_url=base_url_arg,
                                       resume_id_for_preview=resume_id_arg)


if __name__ == "__main__":
    # This is crucial for Playwright's async operations on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

# # template_screenshots.py
# import asyncio
# from playwright.async_api import async_playwright
# import os
# import sys
# import django
# from django.core.management import call_command
#
# # Set up Django environment
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_job_hunt_portal.settings')
# django.setup()
#
#
# async def capture_template_screenshots(output_dir='template_images', base_url='http://localhost:8000'):
#     """
#     Capture screenshots of all resume templates using Playwright.
#
#     Args:
#         output_dir: Directory where images will be saved
#         base_url: Base URL of your running Django development server
#     """
#     # Create output directory if it doesn't exist
#     os.makedirs(output_dir, exist_ok=True)
#
#     async with async_playwright() as p:
#         # Launch browser
#         browser = await p.chromium.launch()
#
#         # Create a context with specific viewport size
#         # A4 aspect ratio at reasonable pixel density
#         context = await browser.new_context(
#             viewport={'width': 384, 'height': 250}  # ~A4 dimensions at 150 DPI
#         )
#
#         # Create a new page
#         page = await context.new_page()
#
#         # Capture screenshots for each template (adjust range as needed)
#         for template_id in range(1, 7):  # For templates 1-6
#             try:
#                 # Navigate to template preview URL
#                 template_url = f"{base_url}/preview-template/{template_id}/"
#                 print(f"Navigating to {template_url}")
#
#                 await page.goto(template_url, wait_until='networkidle')
#
#                 # Wait additional time for any lazy-loaded content or fonts
#                 await page.wait_for_timeout(1000)
#
#                 # Capture screenshot
#                 screenshot_path = os.path.join(output_dir, f"template_{template_id}.png")
#
#                 # Take full page screenshot
#                 await page.screenshot(path=screenshot_path, clip={'x': 0, 'y': 0, 'width': 384, 'height': 250})
#
#                 print(f"✓ Captured template {template_id} - saved to {screenshot_path}")
#
#             except Exception as e:
#                 print(f"❌ Error capturing template {template_id}: {e}")
#
#         # Close browser
#         await browser.close()
#
#         print(f"\nAll screenshots saved to {os.path.abspath(output_dir)}")
#
#
# # To run this script directly
# if __name__ == "__main__":
#     # Get output directory from command line if provided
#     output_dir = sys.argv[1] if len(sys.argv) > 1 else 'template_images'
#
#     # Get base URL from command line if provided
#     base_url = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:8000/job'
#
#     # Ensure the development server is running
#     print("Make sure your Django development server is running!")
#     print(f"Expected URL: {base_url}/preview-template/1/")
#
#     # Run the screenshot function
#     asyncio.run(capture_template_screenshots(output_dir, base_url))