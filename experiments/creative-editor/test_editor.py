"""Focused isolated browser checks; no Django, database, account or external API."""

import base64
import http.client
import json
import struct
import tempfile
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright
from serve import make_server


class SyntheticEditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(
            viewport={"width": 1440, "height": 1100}, device_scale_factor=1
        )
        self.external_requests = []

        def local_only(route):
            if route.request.url.startswith(self.base + "/"):
                route.continue_()
            else:
                self.external_requests.append(route.request.url)
                route.abort()

        self.context.route("**/*", local_only)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.assertEqual([], self.errors)
        self.assertEqual([], self.external_requests)
        self.context.close()

    def open(self):
        self.page.goto(self.base)
        self.page.wait_for_function("!document.getElementById('save').disabled")

    def test_turkish_text_transform_save_reload_and_png_without_external_requests(self):
        self.open()
        title = "İçimizi ısıtan çömlek · Şığ, özenli, özgün"
        self.page.locator("#copy").fill(title)
        self.page.locator("#x").fill("72")
        self.page.locator("#y").fill("145")
        self.page.locator("#angle").fill("5")
        self.page.locator("#scale").fill("0.9")
        self.page.locator("#save").click()
        stored = self.page.evaluate(
            "JSON.parse(localStorage.getItem('yaparo.synthetic.design.v1.product'))"
        )
        self.assertEqual(1, stored["schema_version"])
        self.assertEqual(title, stored["layers"][2]["text"])
        self.assertEqual(72, stored["layers"][2]["x"])
        self.assertNotIn("objects", stored)
        self.assertNotIn("version", stored)
        self.page.reload()
        self.page.wait_for_function("!document.getElementById('save').disabled")
        self.assertEqual(title, self.page.locator("#copy").input_value())
        self.assertEqual("72", self.page.locator("#x").input_value())
        self.assertEqual("145", self.page.locator("#y").input_value())
        self.assertEqual("5", self.page.locator("#angle").input_value())
        self.assertEqual("0.9", self.page.locator("#scale").input_value())
        with self.page.expect_download() as event:
            self.page.locator("#download").click()
        download = event.value
        self.assertEqual("yaparo-sentetik-product.png", download.suggested_filename)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "export.png"
            download.save_as(target)
            data = target.read_bytes()
            self.assertEqual(b"\x89PNG\r\n\x1a\n", data[:8])
            self.assertEqual((800, 800), struct.unpack(">II", data[16:24]))
            self.assertGreater(len(data), 15000)
            dimensions = self.page.evaluate(
                """async encoded => {
                    const image = new Image();
                    image.src = 'data:image/png;base64,' + encoded;
                    await image.decode();
                    return [image.naturalWidth, image.naturalHeight];
                }""",
                base64.b64encode(data).decode("ascii"),
            )
            self.assertEqual([800, 800], dimensions)

    def test_fixed_fixtures_are_separate_and_mobile_has_no_overflow(self):
        self.open()
        self.page.locator("#copy").fill("Ürün taslağı özel başlık")
        self.page.locator("#save").click()
        self.page.locator("#fixture").select_option("service")
        self.page.wait_for_function("!document.getElementById('save').disabled")
        self.assertIn("Evin", self.page.locator("#copy").input_value())
        self.page.locator("#copy").fill("Şehrinde özenli hizmet")
        self.page.locator("#save").click()
        self.page.locator("#fixture").select_option("product")
        self.page.wait_for_function("!document.getElementById('save').disabled")
        self.assertEqual(
            "Ürün taslağı özel başlık", self.page.locator("#copy").input_value()
        )
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(
            self.page.evaluate(
                "document.documentElement.scrollWidth <= window.innerWidth"
            )
        )
        self.page.get_by_role("button", name="Örnek logo", exact=True).click()
        self.assertTrue(self.page.locator("#text-fields").is_hidden())
        self.page.locator("#x").fill("120")
        self.page.locator("#scale").fill("0.75")
        self.page.locator("#angle").fill("-10")
        self.page.locator("#save").click()
        self.assertEqual(
            120,
            self.page.evaluate(
                "JSON.parse(localStorage.getItem('yaparo.synthetic.design.v1.product')).layers[1].x"
            ),
        )
        self.page.reload()
        self.page.wait_for_function("!document.getElementById('save').disabled")
        self.page.get_by_role("button", name="Örnek logo", exact=True).click()
        self.assertEqual("120", self.page.locator("#x").input_value())
        self.assertEqual("0.75", self.page.locator("#scale").input_value())
        self.assertEqual("-10", self.page.locator("#angle").input_value())

    def test_untrusted_saved_data_is_rejected_without_fetch_or_execution(self):
        self.open()
        self.page.locator("#save").click()
        valid = self.page.evaluate(
            "JSON.parse(localStorage.getItem('yaparo.synthetic.design.v1.product'))"
        )
        cases = []
        remote_asset = json.loads(json.dumps(valid))
        remote_asset["layers"][0]["asset"] = "https://example.invalid/private.png"
        cases.append(json.dumps(remote_asset))
        extra_field = json.loads(json.dumps(valid))
        extra_field["layers"][2]["onload"] = "alert(1)"
        cases.append(json.dumps(extra_field))
        too_big = json.loads(json.dumps(valid))
        too_big["width"] = 1000000
        cases.append(json.dumps(too_big))
        too_long = json.loads(json.dumps(valid))
        too_long["layers"][2]["text"] = "a" * 101
        cases.extend([json.dumps(too_long), "{broken", "a" * 12001])
        invalid_color = json.loads(json.dumps(valid))
        invalid_color["layers"][2]["color"] = ["#ffffff"]
        cases.append(json.dumps(invalid_color))
        invalid_color["layers"][2]["color"] = {"value": "#ffffff"}
        cases.append(json.dumps(invalid_color))
        for payload in cases:
            with self.subTest(payload=payload[:40]):
                self.page.evaluate(
                    "value => localStorage.setItem('yaparo.synthetic.design.v1.product', value)",
                    payload,
                )
                self.page.reload()
                self.page.wait_for_function("!document.getElementById('save').disabled")
                self.assertIn(
                    "güvenli değil", self.page.locator("#status").inner_text()
                )
                self.assertEqual(
                    "Gününe küçük bir güzellik.",
                    self.page.locator("#copy").input_value(),
                )
                self.assertEqual(
                    payload,
                    self.page.evaluate(
                        "localStorage.getItem('yaparo.synthetic.design.v1.product')"
                    ),
                )

    def test_cancelled_fixture_change_preserves_unsaved_edit(self):
        self.open()
        self.page.locator("#copy").fill("Kaybolmaması gereken Türkçe düzenleme")
        self.page.once("dialog", lambda dialog: dialog.dismiss())
        self.page.locator("#fixture").select_option("service")
        self.assertEqual("product", self.page.locator("#fixture").input_value())
        self.assertEqual(
            "Kaybolmaması gereken Türkçe düzenleme",
            self.page.locator("#copy").input_value(),
        )
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.locator("#fixture").select_option("service")
        self.page.wait_for_function("!document.getElementById('save').disabled")
        self.assertIn("Evin", self.page.locator("#copy").input_value())

    def test_server_exposes_only_allowlisted_experiment_files(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        for path in (
            "/../PROJECT.md",
            "/%2e%2e/PROJECT.md",
            "/serve.py",
            "/node_modules/",
            "/package-lock.json",
        ):
            connection.request("GET", path)
            response = connection.getresponse()
            self.assertEqual(404, response.status)
            response.read()
        connection.request("GET", "/", headers={"Host": "attacker.invalid"})
        response = connection.getresponse()
        self.assertEqual(403, response.status)
        response.read()
        connection.request("GET", "/")
        response = connection.getresponse()
        self.assertEqual(200, response.status)
        self.assertIn(
            "connect-src 'none'", response.getheader("Content-Security-Policy")
        )
        response.read()
        connection.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
