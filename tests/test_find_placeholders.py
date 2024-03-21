import unittest

from src.models.placeholders import find_unique_placeholders

class TestFindPlaceholders(unittest.TestCase):

    def test_find_placeholders(self) -> None:
        self.assertEqual(find_unique_placeholders("there is not plaholders here"),[])
        self.assertEqual(find_unique_placeholders("there is a plaholders here: $0placeholder"),["$0placeholder"])
        self.assertEqual(find_unique_placeholders("there is a unique plaholder here: $0placeholder and $0placeholder"),["$0placeholder"])


if __name__ == '__main__':
    unittest.main()
