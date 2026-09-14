import unittest

from label_presets import (
    CUSTOM_PRESET,
    DEFAULT_PRESET,
    LABEL_SIZE_PRESETS,
    find_matching_preset,
)


class LabelPresetTests(unittest.TestCase):
    def test_default_preset_is_80_by_53_mm(self):
        self.assertEqual(LABEL_SIZE_PRESETS[DEFAULT_PRESET], (80.0, 53.0))

    def test_each_preset_can_be_found_by_its_dimensions(self):
        for name, dimensions in LABEL_SIZE_PRESETS.items():
            with self.subTest(name=name):
                self.assertEqual(find_matching_preset(*dimensions), name)

    def test_unknown_dimensions_are_custom(self):
        self.assertEqual(find_matching_preset(12.5, 18.25), CUSTOM_PRESET)


if __name__ == "__main__":
    unittest.main()
