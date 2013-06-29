# System modules
import os
import unittest

# xeno imports
from xeno.version import XENO_VERSION, STRINGIFY_VERSION
from xeno.core.protocol import create_initialization_token, \
    check_for_initialization_token, INITIALIZATION_KEY_REMOTE_VERSION, \
    INITIALIZATION_KEY_IS_FILE, INITIALIZATION_KEY_REMOTE_PATH, \
    INITIALIZATION_KEY_REPOSITORY_PATH


class TestProtocol(unittest.TestCase):
    def test_create_and_parse(self):
        """Test to make sure token creation works okay.
        """
        # Test with the user's home directory and a bogus repo
        path = os.path.expanduser('~')
        repo_path = '/Some/Repo/Path/'

        # Create a token
        token = create_initialization_token(path, repo_path)
        print(token)

        # Decode it
        decoded_object = check_for_initialization_token(token)

        # Make sure it is correct
        self.assertEqual(
            decoded_object,
            {
                INITIALIZATION_KEY_REMOTE_VERSION:
                STRINGIFY_VERSION(XENO_VERSION),
                INITIALIZATION_KEY_IS_FILE: False,
                INITIALIZATION_KEY_REMOTE_PATH: path,
                INITIALIZATION_KEY_REPOSITORY_PATH: repo_path
            }
        )

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
                ' <xeno-init>abcd</xeno-init>'
            ),
            None
        )


# Run the tests if this is the main module
if __name__ == '__main__':
    unittest.main()
