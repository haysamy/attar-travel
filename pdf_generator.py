"""
PDF Generator Engine using Playwright with local Chrome/Edge auto-detection.
Supports high-quality vector rendering, crisp Arabic RTL fonts, and exact A4 dimensions.
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import asyncio
import tempfile
from typing import Optional, Union, Dict, Any
from playwright.async_api import async_playwright
import template_engine


def find_browser_executable() -> Optional[str]:
    """Auto-detects Chrome or Edge browser executable on Windows/OS."""
    import shutil
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path

    which_chrome = shutil.which("chrome") or shutil.which("msedge")
    if which_chrome:
        return which_chrome

    return None


async def generate_pdf_async(
    html_content: str,
    output_pdf_path: str,
    wait_for_fonts: bool = True,
    pdf_mode: str = "continuous"
) -> str:
    """
    Renders HTML content to a PDF file asynchronously using Playwright.
    pdf_mode:
      - 'continuous': Single continuous seamless page without A4 page breaks or borders.
      - 'a4': Standard multi-page A4 format.
    """
    browser_exe = find_browser_executable()
    launch_kwargs = {
        "headless": True,
        "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    }
    if browser_exe:
        launch_kwargs["executable_path"] = browser_exe

    mode = (pdf_mode or "continuous").strip().lower()

    async with async_playwright() as p:
        browser = await p.chromium.launch(**launch_kwargs)
        page = await browser.new_page(viewport={"width": 850, "height": 1200})

        # Set content
        await page.set_content(html_content, wait_until="networkidle")

        if wait_for_fonts:
            # Ensure Google Web Fonts (Cairo & Tajawal) finish loading
            try:
                await page.evaluate("document.fonts.ready")
            except Exception:
                pass

        if mode == "continuous":
            # Prepare DOM for seamless single-page measurement without margins or action buttons
            await page.add_style_tag(content="""
                html, body {
                    margin: 0 !important;
                    padding: 0 !important;
                    background: #ffffff !important;
                    width: 850px !important;
                    min-height: 0 !important;
                }
                .no-print {
                    display: none !important;
                }
                .page-container {
                    max-width: 850px !important;
                    width: 850px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    border: none !important;
                    border-radius: 0 !important;
                    box-shadow: none !important;
                }
                .avoid-break, tr, [data-purpose^="hotel-card"], footer, section, main {
                    break-inside: auto !important;
                    page-break-inside: auto !important;
                }
            """)

            # Measure exact height of the quotation container
            content_height = await page.evaluate("""() => {
                const container = document.querySelector('.page-container');
                if (container) {
                    return Math.ceil(container.getBoundingClientRect().height);
                }
                return Math.ceil(document.documentElement.scrollHeight);
            }""")
            content_height = max(content_height, 400) + 2

            # Lock @page size to the exact container dimensions (no !important inside @page per CSS spec)
            await page.add_style_tag(content=f"""
                @page {{
                    size: 850px {content_height}px;
                    margin: 0mm;
                }}
                @media print {{
                    html, body {{
                        width: 850px !important;
                        height: {content_height}px !important;
                        max-height: {content_height}px !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        overflow: hidden !important;
                    }}
                    .page-container {{
                        width: 850px !important;
                        max-width: 850px !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        border: none !important;
                        border-radius: 0 !important;
                        box-shadow: none !important;
                    }}
                }}
            """)

            await page.pdf(
                path=output_pdf_path,
                width="850px",
                height=f"{content_height}px",
                print_background=True,
                prefer_css_page_size=False,
                margin={"top": "0px", "bottom": "0px", "left": "0px", "right": "0px"}
            )
        else:
            # Standard A4 multi-page PDF
            await page.pdf(
                path=output_pdf_path,
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
            )

        await browser.close()

    return os.path.abspath(output_pdf_path)


def generate_pdf(
    data_or_html: Union[str, Dict[str, Any]],
    output_pdf_path: str = "quotation.pdf",
    pdf_mode: str = "continuous"
) -> str:
    """
    Synchronous helper to generate PDF from JSON dictionary, JSON file, or HTML string.
    """
    if isinstance(data_or_html, dict):
        html_content = template_engine.render_html(data_or_html)
    elif isinstance(data_or_html, str):
        if data_or_html.strip().startswith("<"):
            html_content = data_or_html
        else:
            # File path
            if os.path.exists(data_or_html):
                import json
                with open(data_or_html, "r", encoding="utf-8") as f:
                    data = json.load(f)
                html_content = template_engine.render_html(data)
            else:
                raise ValueError(f"File not found: {data_or_html}")
    else:
        html_content = template_engine.render_html(data_or_html)

    return asyncio.run(generate_pdf_async(html_content, output_pdf_path, pdf_mode=pdf_mode))


if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "sample_full.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output_sample.pdf"
    mode_arg = sys.argv[3] if len(sys.argv) > 3 else "continuous"
    print(f"Generating PDF ({mode_arg}) from {input_file} -> {output_file}...")
    result = generate_pdf(input_file, output_file, pdf_mode=mode_arg)
    print(f"Success! PDF created at: {result}")

