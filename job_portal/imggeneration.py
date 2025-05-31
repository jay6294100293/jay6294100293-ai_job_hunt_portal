# job_portal/demo_template_image_generator.py
import asyncio
import json
import logging
from pathlib import Path
from playwright.async_api import async_playwright
import os
import sys
import django
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
import traceback
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Configure logging with UTF-8 encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('template_generator.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- Enhanced Django Environment Setup ---
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_job_hunt_portal.settings')

try:
    django.setup()
    logger.info("Django environment successfully initialized")
except Exception as e:
    logger.error(f"Error setting up Django: {e}")
    logger.error(f"PROJECT_ROOT: {PROJECT_ROOT}")
    logger.error(f"sys.path: {sys.path}")
    sys.exit(1)


@dataclass
class TemplateConfig:
    """Configuration for template screenshot generation"""
    template_id: int
    name: str
    description: str
    viewport: Dict[str, int]
    clip_region: Dict[str, int]
    wait_time: int = 3000
    quality: int = 90


@dataclass
class GenerationResult:
    """Result of screenshot generation"""
    template_id: int
    success: bool
    file_path: Optional[str] = None
    error: Optional[str] = None
    file_size: Optional[int] = None


class DemoTemplateImageGenerator:
    """Enhanced generator for demo resume template images using demo URLs"""

    # Demo resume types you can use (adjust based on your demo data)
    DEMO_RESUME_TYPES = ['professional', 'creative', 'technical', 'executive', 'modern', 'minimal', 'experienced']

    # Template configurations with optimized settings for full resume capture
    TEMPLATE_CONFIGS = [
        TemplateConfig(
            template_id=1,
            name="Professional",
            description="Clean professional template",
            viewport={'width': 1200, 'height': 1600},
            clip_region={'x': 0, 'y': 0, 'width': 800, 'height': 1200}
        ),
        TemplateConfig(
            template_id=2,
            name="Modern",
            description="Modern design template",
            viewport={'width': 1200, 'height': 1600},
            clip_region={'x': 0, 'y': 0, 'width': 800, 'height': 1200}
        ),
        TemplateConfig(
            template_id=3,
            name="Creative",
            description="Creative layout template",
            viewport={'width': 1200, 'height': 1600},
            clip_region={'x': 0, 'y': 0, 'width': 800, 'height': 1200}
        ),
        TemplateConfig(
            template_id=4,
            name="Executive",
            description="Executive style template",
            viewport={'width': 1200, 'height': 1600},
            clip_region={'x': 0, 'y': 0, 'width': 800, 'height': 1200}
        ),
        TemplateConfig(
            template_id=5,
            name="Minimal",
            description="Minimalist template",
            viewport={'width': 1200, 'height': 1600},
            clip_region={'x': 0, 'y': 0, 'width': 800, 'height': 1200}
        ),
        TemplateConfig(
            template_id=6,
            name="Technical",
            description="Technical resume template",
            viewport={'width': 1200, 'height': 1600},
            clip_region={'x': 0, 'y': 0, 'width': 800, 'height': 1200}
        ),
    ]

    def __init__(self,
                 output_dir: str = 'demo_resume_thumbnails',
                 base_url: str = 'http://127.0.0.1:8000',
                 demo_resume_type: str = 'experienced'):  # Changed default to match your example
        self.output_dir = Path(PROJECT_ROOT) / 'static' / 'img' / output_dir
        self.base_url = base_url.rstrip('/')
        self.demo_resume_type = demo_resume_type  # Use demo resume type instead of resume_id
        self.results: List[GenerationResult] = []

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir.absolute()}")
        logger.info(f"Using demo resume type: {self.demo_resume_type}")

    def validate_demo_setup(self) -> bool:
        """Validate that demo URLs are accessible"""
        try:
            # Try to reverse a demo URL to check if the pattern works
            # Using correct format: template1, template2, etc. (no dash)
            test_path = reverse('job_portal:preview_demo_resume',
                                kwargs={
                                    'resume_type_slug': self.demo_resume_type,
                                    'template_slug': 'template1'  # No dash in template slug
                                })
            test_url = f"{self.base_url}{test_path}"
            logger.info(f"Demo URL pattern validation successful: {test_url}")
            return True
        except Exception as e:
            logger.warning(f"Demo URL pattern validation failed: {e}")
            logger.info("Will use manual URL construction")
            return True  # Still proceed with manual URL construction

    async def get_resume_content_bounds(self, page) -> Dict[str, int]:
        """Dynamically detect the resume content area for full resume capture"""
        try:
            # Try to find the resume container and get its bounding box
            selectors_to_try = [
                '.resume-container',
                '.template-container',
                '.resume',
                '.document',
                '.content',
                'main',
                '.page-content'
            ]

            for selector in selectors_to_try:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        bounding_box = await element.bounding_box()
                        if bounding_box and bounding_box['width'] > 100 and bounding_box['height'] > 100:
                            logger.info(f"Found resume content bounds using selector: {selector}")
                            logger.info(f"Bounds: {bounding_box}")

                            # Add padding and ensure we capture the full resume
                            padding = 30
                            return {
                                'x': max(0, int(bounding_box['x'] - padding)),
                                'y': max(0, int(bounding_box['y'] - padding)),
                                'width': min(1000, int(bounding_box['width'] + padding * 2)),
                                'height': min(1400, int(bounding_box['height'] + padding * 2))
                            }
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            logger.warning("Could not detect resume content bounds, using full viewport capture")
            # Return larger default bounds to capture full resume
            return {'x': 0, 'y': 0, 'width': 800, 'height': 1200}

        except Exception as e:
            logger.error(f"Error detecting content bounds: {e}")
            return {'x': 0, 'y': 0, 'width': 800, 'height': 1200}
        """Test if demo URLs are actually accessible"""
        try:
            test_url = self.generate_demo_url(self.TEMPLATE_CONFIGS[0])  # Test first template
            logger.info(f"Testing demo URL accessibility: {test_url}")

            response = await page.goto(test_url, timeout=15000)

            if response and response.status < 400:
                logger.info(f"Demo URL test successful - Status: {response.status}")
                return True
            else:
                logger.error(f"Demo URL test failed - Status: {response.status if response else 'No response'}")
                return False

        except Exception as e:
            logger.error(f"Demo URL accessibility test failed: {e}")
            return False

    def generate_demo_url(self, template_config: TemplateConfig) -> str:
        """Generate demo URL for template preview using your correct URL format"""
        try:
            # Use your demo resume URLs from job_portal_url.py
            # Correct format: job/demo/<resume_type_slug>/<template_slug>/
            # where template_slug is like 'template1', 'template2', etc. (no dash)
            demo_path = reverse('job_portal:preview_demo_resume',
                                kwargs={
                                    'resume_type_slug': self.demo_resume_type,
                                    'template_slug': f'template{template_config.template_id}'
                                    # No dash, just template1, template2, etc.
                                })
            url = f"{self.base_url}{demo_path}"
            logger.info(f"Generated demo URL: {url}")
            return url
        except Exception as e:
            logger.warning(f"Could not reverse demo URL for template {template_config.template_id}: {e}")
            # Manual URL construction as fallback using correct format
            url = f"{self.base_url}/job/demo/{self.demo_resume_type}/template{template_config.template_id}/"
            logger.info(f"Using fallback demo URL: {url}")
            return url

    async def test_demo_url_accessibility(self, page) -> bool:
        """Test if demo URLs are actually accessible"""
        try:
            test_url = self.generate_demo_url(self.TEMPLATE_CONFIGS[0])  # Test first template
            logger.info(f"Testing demo URL accessibility: {test_url}")

            response = await page.goto(test_url, timeout=15000)

            if response and response.status < 400:
                logger.info(f"Demo URL test successful - Status: {response.status}")
                return True
            else:
                logger.error(f"Demo URL test failed - Status: {response.status if response else 'No response'}")
                return False

        except Exception as e:
            logger.error(f"Demo URL accessibility test failed: {e}")
            return False

    async def capture_template_screenshot(self,
                                          page,
                                          template_config: TemplateConfig) -> GenerationResult:
        """Capture screenshot for a single template with robust loading strategy"""
        result = GenerationResult(template_id=template_config.template_id, success=False)

        try:
            # Generate URL
            template_url = self.generate_demo_url(template_config)
            logger.info(f"Capturing template {template_config.template_id} ({template_config.name})")
            logger.info(f"URL: {template_url}")

            # Set viewport using correct Playwright API
            await page.set_viewport_size(template_config.viewport)

            # Navigate with basic wait strategy first
            logger.info(f"Navigating to {template_url}")
            response = await page.goto(
                template_url,
                wait_until='domcontentloaded',
                timeout=60000
            )

            # Check if the page loaded successfully
            if response is None or response.status >= 400:
                raise Exception(f"Page failed to load. Status: {response.status if response else 'No response'}")

            logger.info(f"Page loaded with status: {response.status}")

            # Try multiple wait strategies with fallbacks
            wait_successful = False

            # Strategy 1: Try networkidle with shorter timeout
            try:
                logger.info("Waiting for network idle...")
                await page.wait_for_load_state('networkidle', timeout=10000)
                wait_successful = True
                logger.info("Network idle achieved")
            except Exception as e:
                logger.warning(f"Network idle failed: {e}")

            # Strategy 2: Wait for load state if networkidle failed
            if not wait_successful:
                try:
                    logger.info("Waiting for load state...")
                    await page.wait_for_load_state('load', timeout=15000)
                    wait_successful = True
                    logger.info("Load state achieved")
                except Exception as e:
                    logger.warning(f"Load state failed: {e}")

            # Strategy 3: Just wait for a fixed time if all else fails
            if not wait_successful:
                logger.info("Using fallback fixed wait time...")
                await page.wait_for_timeout(5000)

            # Additional wait for rendering
            await page.wait_for_timeout(template_config.wait_time)

            # Try to wait for common resume elements
            selectors_to_try = [
                '.resume-container',
                '.template-container',
                '.resume',
                '.document',
                'body',
                'main'
            ]

            element_found = False
            for selector in selectors_to_try:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    logger.info(f"Found element: {selector}")
                    element_found = True
                    break
                except:
                    continue

            if not element_found:
                logger.warning(f"No common resume elements found for template {template_config.template_id}")

            # Get dynamic content bounds for better cropping
            content_bounds = await self.get_resume_content_bounds(page)

            # Generate filename with template name (JPEG format)
            filename = f"template_{template_config.template_id}_{template_config.name.lower()}.jpg"
            file_path = self.output_dir / filename

            logger.info(f"Taking screenshot for template {template_config.template_id}")
            logger.info(f"Using content bounds: {content_bounds}")

            # Check if we should capture full page or use clipping
            if content_bounds['height'] > 1200:
                # If resume is very long, take full page screenshot
                logger.info("Resume is very long, taking full page screenshot")
                await page.screenshot(
                    path=str(file_path),
                    quality=template_config.quality,
                    type='jpeg',
                    full_page=True
                )
            else:
                # Use clipping for normal sized resumes
                await page.screenshot(
                    path=str(file_path),
                    clip=content_bounds,
                    quality=template_config.quality,
                    type='jpeg',
                    full_page=False
                )

            # Verify file was created and get size
            if file_path.exists():
                file_size = file_path.stat().st_size
                if file_size > 0:
                    result.success = True
                    result.file_path = str(file_path)
                    result.file_size = file_size
                    logger.info(f"SUCCESS: Template {template_config.template_id} captured successfully")
                    logger.info(f"  File: {filename} ({file_size} bytes)")
                else:
                    result.error = "Screenshot file is empty"
                    logger.error(f"ERROR: Screenshot file is empty for template {template_config.template_id}")
            else:
                result.error = "Screenshot file was not created"
                logger.error(f"ERROR: Screenshot file not created for template {template_config.template_id}")

        except Exception as e:
            result.error = str(e)
            logger.error(f"ERROR: capturing template {template_config.template_id}: {e}")
            logger.error(traceback.format_exc())

        return result

    async def generate_all_templates(self,
                                     specific_templates: Optional[List[int]] = None,
                                     concurrent: bool = False) -> List[GenerationResult]:
        """Generate screenshots for all or specific templates using demo URLs"""

        # Validate demo setup
        if not self.validate_demo_setup():
            logger.error("Cannot proceed without valid demo URL setup")
            return []

        # Filter templates if specific ones requested
        templates_to_process = self.TEMPLATE_CONFIGS
        if specific_templates:
            templates_to_process = [
                config for config in self.TEMPLATE_CONFIGS
                if config.template_id in specific_templates
            ]

        logger.info(f"Processing {len(templates_to_process)} templates using demo URLs")
        logger.info(f"Demo resume type: {self.demo_resume_type}")

        async with async_playwright() as p:
            # Launch browser with optimized settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-web-security',
                    '--ignore-certificate-errors'
                ]
            )

            # Create context with optimized settings
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                ignore_https_errors=True,
                java_script_enabled=True
            )

            try:
                # Test demo URL accessibility first
                test_page = await context.new_page()
                url_accessible = await self.test_demo_url_accessibility(test_page)
                await test_page.close()

                if not url_accessible:
                    logger.error("Demo URLs are not accessible. Please check:")
                    logger.error("1. Django server is running")
                    logger.error("2. Demo resume view is properly configured")
                    logger.error("3. URL patterns are correct")
                    return []

                if concurrent and len(templates_to_process) > 1:
                    # Concurrent processing (faster but more resource intensive)
                    tasks = []
                    for template_config in templates_to_process:
                        page = await context.new_page()
                        task = self.capture_template_screenshot(page, template_config)
                        tasks.append(task)

                    self.results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Handle exceptions in results
                    processed_results = []
                    for i, result in enumerate(self.results):
                        if isinstance(result, Exception):
                            processed_results.append(
                                GenerationResult(
                                    template_id=templates_to_process[i].template_id,
                                    success=False,
                                    error=str(result)
                                )
                            )
                        else:
                            processed_results.append(result)
                    self.results = processed_results

                else:
                    # Sequential processing (more stable)
                    page = await context.new_page()
                    self.results = []

                    for template_config in templates_to_process:
                        result = await self.capture_template_screenshot(page, template_config)
                        self.results.append(result)

                        # Small delay between templates
                        await asyncio.sleep(1)

            finally:
                await browser.close()

        return self.results

    def generate_summary_report(self) -> Dict:
        """Generate a summary report of the generation process"""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        total_size = sum(r.file_size or 0 for r in successful)

        report = {
            'timestamp': str(asyncio.get_event_loop().time()),
            'total_templates': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'total_file_size': total_size,
            'output_directory': str(self.output_dir),
            'demo_resume_type': self.demo_resume_type,
            'successful_templates': [
                {
                    'template_id': r.template_id,
                    'file_path': r.file_path,
                    'file_size': r.file_size
                } for r in successful
            ],
            'failed_templates': [
                {
                    'template_id': r.template_id,
                    'error': r.error
                } for r in failed
            ]
        }

        # Save report
        report_path = self.output_dir / 'generation_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def print_summary(self):
        """Print generation summary to console"""
        report = self.generate_summary_report()

        print("\n" + "=" * 60)
        print("DEMO TEMPLATE IMAGE GENERATION SUMMARY")
        print("=" * 60)
        print(f"Demo Resume Type: {report['demo_resume_type']}")
        print(f"Total Templates Processed: {report['total_templates']}")
        print(f"Successfully Generated: {report['successful']}")
        print(f"Failed: {report['failed']}")
        print(f"Total File Size: {report['total_file_size']} bytes")
        print(f"Output Directory: {report['output_directory']}")

        if report['successful_templates']:
            print("\nSUCCESSFUL TEMPLATES:")
            for template in report['successful_templates']:
                print(f"  Template {template['template_id']}: {template['file_size']} bytes")

        if report['failed_templates']:
            print("\nFAILED TEMPLATES:")
            for template in report['failed_templates']:
                print(f"  Template {template['template_id']}: {template['error']}")

        print("\n" + "=" * 60)


async def main():
    """Main execution function with enhanced argument parsing for demo URLs"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate demo resume template images using demo URLs')
    parser.add_argument('--output-dir', default='demo_resume_thumbnails',
                        help='Output directory name (default: demo_resume_thumbnails)')
    parser.add_argument('--base-url', default='http://127.0.0.1:8000',
                        help='Base URL for Django server (default: http://127.0.0.1:8000)')
    parser.add_argument('--demo-type', default='experienced',
                        choices=['professional', 'creative', 'technical', 'executive', 'modern', 'minimal',
                                 'experienced'],
                        help='Demo resume type to use (default: experienced)')
    parser.add_argument('--templates', nargs='+', type=int,
                        help='Specific template IDs to generate (default: all)')
    parser.add_argument('--concurrent', action='store_true',
                        help='Use concurrent processing (faster but more resource intensive)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')

    # Parse command line arguments if available, otherwise use defaults
    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        # Default arguments for direct execution
        args = argparse.Namespace(
            output_dir='demo_resume_thumbnails',
            base_url='http://127.0.0.1:8000',
            demo_type='experienced',
            templates=None,
            concurrent=False,
            verbose=False
        )

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("--- DEMO RESUME TEMPLATE IMAGE GENERATOR ---")
    print(f"Output directory: '{args.output_dir}'")
    print(f"Base URL: {args.base_url}")
    print(f"Demo resume type: {args.demo_type}")
    print(f"Specific templates: {args.templates or 'All templates (1-6)'}")
    print(f"Concurrent processing: {args.concurrent}")

    # Show example URLs that will be generated
    print(f"\nExample URLs that will be captured:")
    for i in range(1, 4):  # Show first 3 as examples
        example_url = f"{args.base_url}/job/demo/{args.demo_type}/template{i}/"
        print(f"  Template {i}: {example_url}")
    if args.templates is None or len([t for t in args.templates if t > 3]) > 0:
        print(f"  ... and more")

    generator = DemoTemplateImageGenerator(
        output_dir=args.output_dir,
        base_url=args.base_url,
        demo_resume_type=args.demo_type
    )

    print(f"\nIMPORTANT CHECKLIST:")
    print(f"- Django development server running at: {args.base_url}")
    print(f"- Demo resume URLs are accessible: /job/demo/{args.demo_type}/template{1}/")
    print(f"- Demo resume view 'preview_demo_resume' is working")
    print(f"- Output directory is writable: {generator.output_dir}")
    print()

    # Generate screenshots
    results = await generator.generate_all_templates(
        specific_templates=args.templates,
        concurrent=args.concurrent
    )

    # Print summary
    generator.print_summary()

    return results


if __name__ == "__main__":
    # Set up event loop policy for Windows
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except (ImportError, AttributeError):
            logger.warning("Could not set Windows event loop policy, using default")

    try:
        results = asyncio.run(main())
        exit_code = 0 if all(r.success for r in results) else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Generation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)