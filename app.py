"""
정밀 부가가치세(VAT) 검토용 웹 애플리케이션 서버
- 추가 패키지 설치 불필요 (Python 표준 라이브러리 기반)
- Decimal 정밀 연산 API 및 대화형 UI 제공
"""

import http.server
import socketserver
import json
import webbrowser
import os
import sys
from decimal import Decimal
from vat_core import calculate_single, calculate_cart, RoundingPolicy, TaxType

PORT = 8055
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class VatApiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(BASE_DIR, "index.html"), "rb") as f:
                self.wfile.write(f.read())
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/calculate_single":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            amount = Decimal(str(data.get("amount", 0)))
            is_gross = bool(data.get("is_gross", False))
            tax_type = TaxType(data.get("tax_type", "TAXABLE"))
            simplified_rate = Decimal(str(data.get("simplified_rate", 0.3)))
            service_charge = Decimal(str(data.get("service_charge", 0)))
            rounding_policy = RoundingPolicy(data.get("rounding_policy", "TRUNCATE"))
            is_non_deductible = bool(data.get("is_non_deductible", False))

            result = calculate_single(
                amount=amount,
                is_gross=is_gross,
                tax_type=tax_type,
                simplified_rate=simplified_rate,
                service_charge=service_charge,
                rounding_policy=rounding_policy,
                is_non_deductible=is_non_deductible
            )

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
            return

        elif self.path == "/api/calculate_cart":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            items = data.get("items", [])
            rounding_policy = RoundingPolicy(data.get("rounding_policy", "TRUNCATE"))
            adjust_penny = bool(data.get("adjust_penny", True))

            result = calculate_cart(
                items=items,
                rounding_policy=rounding_policy,
                adjust_penny=adjust_penny
            )

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server():
    os.chdir(BASE_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), VatApiHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"==================================================")
        print(f" 정밀 부가가치세(VAT) 검토용 웹 애플리케이션 시작됨")
        print(f" 접속 주소: {url}")
        print(f" 종료하려면 터미널에서 Ctrl+C를 누르세요.")
        print(f"==================================================")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버가 종료되었습니다.")

if __name__ == "__main__":
    run_server()
