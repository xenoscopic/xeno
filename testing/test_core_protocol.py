# System modules
import unittest

# xeno imports
from xeno.core.protocol import create_initialization_token, \
    check_for_initialization_token


class TestProtocol(unittest.TestCase):
    def test_creae(self):
        """Test to make sure token creation works okay.
        """
        # Create a token
        token = create_initialization_token('/Users/Jacob/repo')

        # Make sure it is correct
        self.assertEqual(token,
                         '<xeno-init>/Users/Jacob/repo</xeno-init>')

    def test_parse(self):
        """Test to make sure token detection works okay.
        """
        # Create a token manually
        token = '<xeno-init>/Users/Jacob/repo</xeno-init>'

        # Make sure it parses correctly
        self.assertEqual(check_for_initialization_token(token),
                         '/Users/Jacob/repo')

    def test_no_match(self):
        """Test to make sure tokens aren't falsely detected.
        """
        self.assertEqual(check_for_initialization_token('afs'),
                         None)
        self.assertEqual(check_for_initialization_token(''),
                         None)
        # This is the case that requires it be at the start of the string
        self.assertEqual(
            check_for_initialization_token(
                ' <xeno-init>/Users/Jacob/repo</xeno-init>'
            ),
            None
        )


# Run the tests if this is the main module
if __name__ == '__main__':
    unittest.main()
