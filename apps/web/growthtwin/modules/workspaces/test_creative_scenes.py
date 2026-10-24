"""Pure synthetic scene checks; no database, file, browser or provider access."""

from copy import deepcopy
from unittest import TestCase

from growthtwin.modules.workspaces.creative_scenes import (
    SceneValidationError,
    seed_scene,
    validate_scene,
)


class CreativeSceneTests(TestCase):
    def scene(self, fixture="product", **changes):
        values = {
            "fixture": fixture,
            "tagline_text": "İçimizi ısıtan çömlek · Şık, özenli, özgün",
            "primary_color": "#AABBCC",
            "logo_key": f"{fixture}:logo:v1",
        }
        values.update(changes)
        return seed_scene(**values)

    def assert_invalid(self, scene, fixture="product"):
        with self.assertRaisesRegex(SceneValidationError, "Invalid synthetic scene"):
            validate_scene(scene, fixture=fixture)

    def test_seeds_both_fixtures_from_literal_identity_fields(self):
        for fixture in ("product", "service"):
            with self.subTest(fixture=fixture):
                value = self.scene(fixture)
                self.assertEqual(1, value["schema_version"])
                self.assertEqual((800, 800), (value["width"], value["height"]))
                self.assertEqual(fixture, value["fixture"])
                self.assertEqual("#AABBCC", value["layers"][2]["color"])
                self.assertIn("İçimizi", value["layers"][2]["text"])
                self.assertEqual(f"{fixture}:logo:v1", value["layers"][1]["asset"])
                self.assertEqual(
                    ["hero", "logo", "title", "subtitle"],
                    [layer["id"] for layer in value["layers"]],
                )
                self.assertEqual(value, validate_scene(value, fixture=fixture))
                self.assertNotIn("background", value)
                self.assertNotIn("objects", value)

    def test_seed_rejects_unknown_fixture_logo_and_invalid_identity_literals(self):
        for changes in (
            {"fixture": "private-brand"},
            {"fixture": []},
            {"logo_key": "service:logo:v1"},
            {"logo_key": "https://example.invalid/logo.png"},
            {"tagline_text": "x" * 101},
            {"tagline_text": None},
            {"primary_color": ["#ffffff"]},
            {"primary_color": "red"},
        ):
            with self.subTest(changes=changes), self.assertRaises(SceneValidationError):
                self.scene(**changes)

    def test_input_and_returned_scene_never_share_nested_containers(self):
        original = self.scene()
        saved = deepcopy(original)
        result = validate_scene(original, fixture="product")
        result["layers"][2]["text"] = "Sonraki değişiklik"
        self.assertEqual(saved, original)
        original["layers"][0]["x"] = 600
        self.assertEqual(115, result["layers"][0]["x"])
        self.assertEqual(saved, self.scene())

    def test_exact_top_level_shape_and_fixture_are_required(self):
        value = self.scene()
        for candidate in (
            None,
            [],
            "{}",
            {**value, "objects": []},
            {**value, "owner_id": 1},
        ):
            with self.subTest(candidate_type=type(candidate)):
                self.assert_invalid(candidate)
        for key in value:
            candidate = deepcopy(value)
            del candidate[key]
            self.assert_invalid(candidate)
        self.assert_invalid(value, fixture="service")
        for fixture in (None, [], "foreign"):
            self.assert_invalid(value, fixture=fixture)

    def test_fixed_version_and_dimensions_reject_bool_float_and_alternate_values(self):
        for key, valid in (("schema_version", 1), ("width", 800), ("height", 800)):
            for value in (True, float(valid), str(valid), valid + 1, None):
                candidate = self.scene()
                candidate[key] = value
                with self.subTest(key=key, value=value):
                    self.assert_invalid(candidate)

    def test_exact_fixed_layer_count_order_and_types(self):
        for value in (None, {}, (), [], [self.scene()["layers"][0]] * 5):
            candidate = self.scene()
            candidate["layers"] = value
            self.assert_invalid(candidate)
        candidate = self.scene()
        candidate["layers"][0], candidate["layers"][1] = (
            candidate["layers"][1],
            candidate["layers"][0],
        )
        self.assert_invalid(candidate)
        for index in range(4):
            for key, value in (
                ("id", "foreign"),
                ("type", "svg"),
                ("onload", "alert(1)"),
            ):
                candidate = self.scene()
                candidate["layers"][index][key] = value
                self.assert_invalid(candidate)
            candidate = self.scene()
            candidate["layers"][index] = []
            self.assert_invalid(candidate)

    def test_foreign_assets_urls_data_and_paths_are_not_accepted(self):
        for index in (0, 1):
            for value in (
                "service:logo:v1",
                "product:logo:v2",
                "https://example.invalid/p.png",
                "data:image/svg+xml,<svg/>",
                "blob:external",
                "../private.png",
                ["product:logo:v1"],
            ):
                candidate = self.scene()
                candidate["layers"][index]["asset"] = value
                self.assert_invalid(candidate)

    def test_numeric_bounds_accept_finite_limits_and_reject_invalid_types(self):
        for key, low, high in (
            ("x", 0, 700),
            ("y", 0, 700),
            ("scale", 0.5, 1.5),
            ("angle", -45, 45),
        ):
            for value in (low, high, (low + high) / 2):
                candidate = self.scene()
                candidate["layers"][0][key] = value
                self.assertEqual(
                    candidate, validate_scene(candidate, fixture="product")
                )
            for value in (
                low - 0.01,
                high + 0.01,
                True,
                False,
                "1",
                None,
                [],
                float("nan"),
                float("inf"),
                -float("inf"),
                10**1000,
            ):
                candidate = self.scene()
                candidate["layers"][0][key] = value
                with self.subTest(key=key, value_type=type(value)):
                    self.assert_invalid(candidate)

    def test_text_uses_browser_utf16_length_and_rejects_lone_surrogates(self):
        for text in ("", "Ö" * 100, "😀" * 50, "İlk satır\nİkinci satır"):
            value = self.scene(tagline_text=text)
            self.assertEqual(text, value["layers"][2]["text"])
        for text in ("x" * 101, "😀" * 51, "😀" * 50 + "x", "\ud800", "\udfff", [], 1):
            with (
                self.subTest(text_type=type(text)),
                self.assertRaises(SceneValidationError),
            ):
                self.scene(tagline_text=text)

    def test_control_characters_are_rejected_in_both_text_layers(self):
        for index in (2, 3):
            for code in (*range(10), *range(11, 32), 127):
                value = self.scene()
                value["layers"][index]["text"] = "Örnek" + chr(code)
                self.assert_invalid(value)

    def test_colors_require_exact_string_hex_without_coercion_or_css(self):
        for index in (2, 3):
            for color in (
                ["#ffffff"],
                {"value": "#ffffff"},
                None,
                "#ffffff\n",
                "white",
                "#fff",
                "#ffffff;display:none",
                "url(https://example.invalid)",
            ):
                value = self.scene()
                value["layers"][index]["color"] = color
                self.assert_invalid(value)

    def test_rejection_keeps_input_unchanged_and_does_not_echo_values(self):
        value = self.scene()
        value["layers"][0]["asset"] = "private-sensitive-reference"
        before = deepcopy(value)
        with self.assertRaises(SceneValidationError) as raised:
            validate_scene(value, fixture="product")
        self.assertEqual(before, value)
        self.assertNotIn("private-sensitive", str(raised.exception))
