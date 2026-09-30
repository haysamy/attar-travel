"""
Interactive Backend Server for Travel Package / Quotation Studio.
Powered by Python's built-in http.server, Playwright, and template_engine.
"""

import os
import sys
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import asyncio
import tempfile
import importlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import template_engine
import pdf_generator
import text_parser


PORT = 8080


def resolve_resource(filename: str) -> str:
    """Finds resource file whether running from source or inside PyInstaller bundle."""
    # 1. Bundled via PyInstaller
    if hasattr(sys, "_MEIPASS"):
        meipass_path = os.path.join(sys._MEIPASS, filename)
        if os.path.exists(meipass_path):
            return meipass_path

    # 2. Next to executable
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    exe_path = os.path.join(exe_dir, filename)
    if os.path.exists(exe_path):
        return exe_path

    # 3. Current working directory
    if os.path.exists(filename):
        return os.path.abspath(filename)

    return filename


class QuotationRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, content_type="text/html; charset=utf-8", status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(status_code=204)

    def do_GET(self):
        url = self.path.split("?")[0]

        if url == "/" or url == "/index.html":
            target = resolve_resource("app.html")
            if os.path.exists(target):
                with open(target, "r", encoding="utf-8") as f:
                    content = f.read()
                self._set_headers("text/html; charset=utf-8")
                self.wfile.write(content.encode("utf-8"))
            else:
                self._set_headers("text/plain; charset=utf-8", 404)
                self.wfile.write(b"app.html not found")

        elif url.startswith("/api/sample/"):
            sample_name = url.replace("/api/sample/", "").strip()
            file_map = {
                "full": "sample_full.json",
                "hotels": "sample_hotels_only.json",
                "flights": "sample_flights_only.json",
                "transports": "sample_transports_only.json",
            }
            target_fname = file_map.get(sample_name, "sample_full.json")
            target_file = resolve_resource(target_fname)
            if os.path.exists(target_file):
                with open(target_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._set_headers("application/json; charset=utf-8")
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            else:
                self._set_headers("application/json; charset=utf-8", 404)
                self.wfile.write(json.dumps({"error": "Sample file not found"}).encode("utf-8"))

        elif url.endswith(".webp") or url.endswith(".png"):
            fname = os.path.basename(url)
            fpath = resolve_resource(fname)
            if os.path.exists(fpath):
                with open(fpath, "rb") as f:
                    img_bytes = f.read()
                mime = "image/webp" if fname.endswith(".webp") else "image/png"
                self._set_headers(mime)
                self.wfile.write(img_bytes)
            else:
                self._set_headers("text/plain; charset=utf-8", 404)
                self.wfile.write(b"Image not found")

        elif url.endswith(".txt"):
            fname = os.path.basename(url)
            fpath = resolve_resource(fname)
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    txt = f.read()
                self._set_headers("text/plain; charset=utf-8")
                self.wfile.write(txt.encode("utf-8"))
            else:
                self._set_headers("text/plain; charset=utf-8", 404)
                self.wfile.write(b"File not found")

        else:
            self._set_headers("text/plain; charset=utf-8", 404)
            self.wfile.write(b"Not Found")

    def do_POST(self):
        url = self.path.split("?")[0]
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        # Auto-reload modules so changes are always fresh
        try:
            importlib.reload(template_engine)
            importlib.reload(text_parser)
            importlib.reload(pdf_generator)
        except Exception as e:
            print(f"[Reload Warning]: {e}")

        try:
            payload = json.loads(body) if body else {}
        except Exception as e:
            self._set_headers("application/json; charset=utf-8", 400)
            self.wfile.write(json.dumps({"error": f"Invalid JSON: {str(e)}"}).encode("utf-8"))
            return

        if url == "/api/parse-text":
            try:
                raw_text = payload.get("text", "")
                parsed_data = text_parser.parse_travel_text(raw_text)
                html_output = template_engine.render_html(parsed_data)
                response_obj = {
                    "data": parsed_data,
                    "html": html_output
                }
                self._set_headers("application/json; charset=utf-8")
                self.wfile.write(json.dumps(response_obj, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self._set_headers("application/json; charset=utf-8", 500)
                self.wfile.write(json.dumps({"error": f"Parse Error: {str(e)}"}).encode("utf-8"))

        elif url == "/api/render":
            try:
                html_output = template_engine.render_html(payload)
                self._set_headers("text/html; charset=utf-8")
                self.wfile.write(html_output.encode("utf-8"))
            except Exception as e:
                self._set_headers("text/plain; charset=utf-8", 500)
                self.wfile.write(f"Render Error: {str(e)}".encode("utf-8"))

        elif url == "/api/generate-pdf":
            try:
                from urllib.parse import parse_qs, urlparse
                query_params = parse_qs(urlparse(self.path).query)
                pdf_mode = "continuous"
                if "mode" in query_params and query_params["mode"]:
                    pdf_mode = query_params["mode"][0]
                elif isinstance(payload, dict) and "_pdf_mode" in payload:
                    pdf_mode = str(payload.pop("_pdf_mode") or "continuous")

                html_output = template_engine.render_html(payload)
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                    tmp_pdf_path = tmp_pdf.name

                asyncio.run(pdf_generator.generate_pdf_async(html_output, tmp_pdf_path, pdf_mode=pdf_mode))

                with open(tmp_pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                try:
                    os.remove(tmp_pdf_path)
                except Exception:
                    pass

                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", 'attachment; filename="quotation.pdf"')
                self.send_header("Content-Length", str(len(pdf_bytes)))
                self.end_headers()
                self.wfile.write(pdf_bytes)

            except Exception as e:
                self._set_headers("text/plain; charset=utf-8", 500)
                self.wfile.write(f"PDF Error: {str(e)}".encode("utf-8"))

        else:
            self._set_headers("text/plain; charset=utf-8", 404)
            self.wfile.write(b"Endpoint not found")


def run_server(port=PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, QuotationRequestHandler)
    print(f"================================================================")
    print(f"  نظام توليد عروض الأسعار السياحية (عطار ترافل) يعمل الآن بنجاح! ")
    print(f"  افتح المتصفح على الرابط: http://localhost:{port}")
    print(f"================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nتم إيقاف الخادم.")
        httpd.server_close()


if __name__ == "__main__":
    env_port = os.environ.get("PORT")
    if env_port and env_port.isdigit():
        port = int(env_port)
    elif len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    else:
        port = PORT
    run_server(port)
