"""Pure bounded Yaparo scene v1; no ORM, files, URLs or Fabric deserialization.

Identity fields are supplied as literal values, so seeding cannot lazily query a
BrandIdentity. The caller owns authorization and immutable identity binding.
"""

import math
import re
from copy import deepcopy

SCENE_SIZE = 800
_FIXTURES = {
    "product": "Kurgusal seramik koleksiyonu · Ürün örneği",
    "service": "Kurgusal ev bakım hizmeti · Ankara örneği",
}
_LAYERS = (
    ("hero", "image"),
    ("logo", "image"),
    ("title", "text"),
    ("subtitle", "text"),
)
_COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")


class SceneValidationError(ValueError):
    """A scene is outside the fixed synthetic v1 contract."""


def _refuse():
    # Do not interpolate caller-controlled values into errors.
    raise SceneValidationError("Invalid synthetic scene.")


def _fixture(value):
    if type(value) is not str or value not in _FIXTURES:
        _refuse()


def _keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        _refuse()


def _number(value, minimum, maximum):
    if (
        type(value) not in (int, float)
        or not minimum <= value <= maximum
        or not math.isfinite(value)
    ):
        _refuse()


def _text(value):
    if type(value) is not str:
        _refuse()
    try:
        length = len(value.encode("utf-16-le")) // 2
    except UnicodeEncodeError:
        _refuse()
    if length > 100 or any(
        ord(character) <= 9 or 11 <= ord(character) <= 31 or ord(character) == 127
        for character in value
    ):
        _refuse()


def validate_scene(value, *, fixture):
    """Return an independent scene after exact bounded JSON-value validation.

    Text length follows browser UTF-16 units. Lone surrogates are rejected to keep
    future JSON/UTF-8 persistence valid. Parsing/body-byte and duplicate-key checks
    belong to a later HTTP boundary; this function accepts already decoded values.
    """
    _fixture(fixture)
    _keys(value, ("schema_version", "fixture", "width", "height", "layers"))
    if (
        type(value["schema_version"]) is not int
        or value["schema_version"] != 1
        or type(value["fixture"]) is not str
        or value["fixture"] != fixture
        or type(value["width"]) is not int
        or value["width"] != SCENE_SIZE
        or type(value["height"]) is not int
        or value["height"] != SCENE_SIZE
        or type(value["layers"]) is not list
        or len(value["layers"]) != len(_LAYERS)
    ):
        _refuse()
    for layer, (layer_id, kind) in zip(value["layers"], _LAYERS, strict=True):
        _keys(
            layer,
            ("id", "type", "x", "y", "scale", "angle")
            + (("text", "color") if kind == "text" else ("asset",)),
        )
        if (
            type(layer["id"]) is not str
            or layer["id"] != layer_id
            or type(layer["type"]) is not str
            or layer["type"] != kind
        ):
            _refuse()
        for name, minimum, maximum in (
            ("x", 0, 700),
            ("y", 0, 700),
            ("scale", 0.5, 1.5),
            ("angle", -45, 45),
        ):
            _number(layer[name], minimum, maximum)
        if kind == "image":
            suffix = "illustration" if layer_id == "hero" else "logo"
            if (
                type(layer["asset"]) is not str
                or layer["asset"] != f"{fixture}:{suffix}:v1"
            ):
                _refuse()
        else:
            _text(layer["text"])
            if type(layer["color"]) is not str or not _COLOR.fullmatch(layer["color"]):
                _refuse()
    return deepcopy(value)


def seed_scene(*, fixture, tagline_text, primary_color, logo_key):
    """Seed from immutable identity literals without extending scene v1.

    V1 has no background field or independently recolorable bitmap logo. Primary
    color seeds the title; secondary color/tone are not silently mapped elsewhere.
    """
    _fixture(fixture)
    if type(logo_key) is not str or logo_key != f"{fixture}:logo:v1":
        _refuse()
    layers = [
        {
            "id": "hero",
            "type": "image",
            "asset": f"{fixture}:illustration:v1",
            "x": 115,
            "y": 310,
            "scale": 1,
            "angle": 0,
        },
        {
            "id": "logo",
            "type": "image",
            "asset": logo_key,
            "x": 55,
            "y": 40,
            "scale": 1,
            "angle": 0,
        },
        {
            "id": "title",
            "type": "text",
            "text": tagline_text,
            "color": primary_color,
            "x": 55,
            "y": 135,
            "scale": 1,
            "angle": 0,
        },
        {
            "id": "subtitle",
            "type": "text",
            "text": _FIXTURES[fixture],
            "color": "#596b59",
            "x": 58,
            "y": 250,
            "scale": 1,
            "angle": 0,
        },
    ]
    return validate_scene(
        {
            "schema_version": 1,
            "fixture": fixture,
            "width": SCENE_SIZE,
            "height": SCENE_SIZE,
            "layers": layers,
        },
        fixture=fixture,
    )
