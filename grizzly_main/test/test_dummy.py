import unittest


class TestStringMethods(unittest.TestCase):
    """
    Basic unitest example from: https://docs.python.org/3/library/unittest.html#basic-example
    """

    def test_upper(self) -> None:
        """
        Test string .upper() method
        :return: None
        """
        self.assertEqual("foo".upper(), "FOO")

    def test_isupper(self) -> None:
        """
        Test string .isupper() method
        :return: None
        """
        self.assertTrue("FOO".isupper())
        self.assertFalse("Foo".isupper())

    def test_split(self) -> None:
        """
        Test string .split() method
        :return: None
        """
        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)  # type: ignore


if __name__ == "__main__":
    unittest.main()
