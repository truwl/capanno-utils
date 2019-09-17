import tempfile
from unittest import TestCase


class TestBase(TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        pass