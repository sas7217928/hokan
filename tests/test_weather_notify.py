import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import datetime as dt

from weather_notify import format_message, parse_time, should_run  # noqa: E402

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


class ScheduleTest(unittest.TestCase):
    T = parse_time("12:00")

    def test_before_target(self):
        self.assertFalse(should_run(dt.datetime(2026, 10, 6, 11, 59), None, self.T))

    def test_at_target(self):
        self.assertTrue(should_run(dt.datetime(2026, 10, 6, 12, 0), None, self.T))

    def test_late_wake_still_runs(self):
        self.assertTrue(should_run(dt.datetime(2026, 10, 6, 15, 0), dt.date(2026, 10, 5), self.T))

    def test_once_per_day(self):
        self.assertFalse(should_run(dt.datetime(2026, 10, 6, 12, 5), dt.date(2026, 10, 6), self.T))


if __name__ == "__main__":
    unittest.main()
