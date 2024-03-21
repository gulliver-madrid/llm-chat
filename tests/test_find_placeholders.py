import unittest

from src.models.placeholders import find_placeholders

class TestFindPlaceholders(unittest.TestCase):

    def test_find_placeholders(self) -> None:
        self.assertEqual(find_placeholders("there is not plaholders here"),[])


if __name__ == '__main__':
    unittest.main()
