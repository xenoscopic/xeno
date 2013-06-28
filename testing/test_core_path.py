# System modules
import unittest

# xeno imports
from xeno.core.path import Path


class TestPath(unittest.TestCase):
    def test_path_only(self):
        """Test to make sure path-only specifications work.
        """
        # Create the path
        file_path = '/some/local/path'
        p = Path(file_path)

        # Do the checks
        self.assertIsNone(p.username)
        self.assertIsNone(p.hostname)
        self.assertIsNone(p.port)
        self.assertEqual(p.file_path, file_path)
        self.assertTrue(p.is_local)

    def test_hostname_and_path(self):
        """Test to make sure hostname and path specifications work.
        """
        # Create the path
        p = Path('myhost:/the/path')

        # Do the checks
        self.assertIsNone(p.username)
        self.assertEqual(p.hostname, 'myhost')
        self.assertIsNone(p.port)
        self.assertEqual(p.file_path, '/the/path')
        self.assertFalse(p.is_local)

    def test_username_hostname_and_path(self):
        """Test to make sure username, hostname, and path specifications work.
        """
        # Create the path
        p = Path('jacob@myhost:/the/path')

        # Do the checks
        self.assertEqual(p.username, 'jacob')
        self.assertEqual(p.hostname, 'myhost')
        self.assertIsNone(p.port)
        self.assertEqual(p.file_path, '/the/path')
        self.assertFalse(p.is_local)

    def test_username_hostname_port_and_path(self):
        """Test to make sure username, hostname, port, and path specifications
        work.
        """
        # Create the path
        p = Path('jacob@myhost:25:/the/path')

        # Do the checks
        self.assertEqual(p.username, 'jacob')
        self.assertEqual(p.hostname, 'myhost')
        self.assertEqual(p.port, 25)
        self.assertEqual(p.file_path, '/the/path')
        self.assertFalse(p.is_local)

    def test_hostname_port_and_path(self):
        """Test to make sure hostname, port, and path specifications work.
        """
        # Create the path
        p = Path('myhost:25:/the/path')

        # Do the checks
        self.assertIsNone(p.username)
        self.assertEqual(p.hostname, 'myhost')
        self.assertEqual(p.port, 25)
        self.assertEqual(p.file_path, '/the/path')
        self.assertFalse(p.is_local)

    def test_invalid_port(self):
        """Test to make sure invalid ports fail.
        """
        # Create the path, making sure it fails on the bogus port
        with self.assertRaises(ValueError):
            p = Path('jacob@myhost:a:/the/path')

    def test_double_port(self):
        """Test to make sure multiple hostnames/ports fail.
        """
        # Create the path, making sure it fails on the bogus port
        with self.assertRaises(ValueError):
            p = Path('jacob@myhost:5:10:/the/path')

    def test_username_and_path(self):
        """Test to make sure username-only specifications with a path fail.
        """
        # Create the path, making sure it fails on the bogus username
        with self.assertRaises(ValueError):
            p = Path('jacob@/the/path')

    def test_empty_path(self):
        """Test to make sure specifications without a path fail.
        """
        # Create the path, making sure it fails on the empty path
        with self.assertRaises(ValueError):
            p = Path('')

    def test_username_empty_path(self):
        """Test to make sure specifications without a path fail, this time with
        a username thrown in for kicks.
        """
        # Create the path, making sure it fails on the empty path
        with self.assertRaises(ValueError):
            p = Path('jacob@')


# Run the tests if this is the main module
if __name__ == '__main__':
    unittest.main()
