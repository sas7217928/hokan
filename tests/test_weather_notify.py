import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from weather_notify import format_message  # noqa: E402

DATA = {"daily": {
    "time": ["2026-10-06", "2026-10-07"],
    "weather_code": [0, 63],
    "temperature_2m_max": [24.2, 19.6],
    "temperature_2m_min": [15.0, 14.4],
    "precipitation_probability_max": [0, 80],
}}


class FormatTest(unittest.TestCase):
    def test_uses_tomorrow(self):
        msg = format_message(DATA, "東京")
        self.assertIn("2026-10-07", msg)
        self.assertIn("雨", msg)
        self.assertIn("最高 20℃ / 最低 14℃", msg)
        self.assertIn("80%", msg)
        self.assertIn("傘", msg)

    def test_no_umbrella_when_dry(self):
        data = {"daily": {k: [v[0], v[0]] for k, v in DATA["daily"].items()}}
        self.assertNotIn("傘", format_message(data, "東京"))

    def test_null_precipitation(self):
        data = {"daily": {**DATA["daily"], "precipitation_probability_max": [0, None]}}
        self.assertIn("降水確率: -", format_message(data, "東京"))


if __name__ == "__main__":
    unittest.main()
