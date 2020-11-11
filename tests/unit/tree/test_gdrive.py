import os

import pytest

from dvc.exceptions import FileMissingError
from dvc.tree import GDriveTree
from dvc.tree.gdrive import GDriveURLInfo
from tests.basic_env import TestDvc


class TestGDriveURL(TestDvc):
    def setUp(self):
        super().setUp()
        if not os.getenv(GDriveTree.GDRIVE_CREDENTIALS_DATA):
            pytest.skip("no gdrive credentials data available")

        self.paths_answers = [
            ("1nKf4XcsNCN3oLujqlFTJoK5Fvx9iKCZb", "data.txt"),
            ("16onq6BZiiUFj083XloYVk7LDDpklDr7h/file.txt", "file.txt"),
            ("16onq6BZiiUFj083XloYVk7LDDpklDr7h/dir/data.txt", "data.txt"),
            ("root/test_data/data.txt", "data.txt"),
        ]

        self.invalid_paths = [
            "============",
            "16onq6BZiiUFj083XloYVk7LDDpklDr7h/fake_dir",
        ]

    def get_tree(self, path_info):
        url = path_info.replace(path="").url
        return GDriveTree(self.dvc, {"url": url})

    def test_get_file_name(self):
        for path, answer in self.paths_answers:
            path_info = GDriveURLInfo("gdrive://" + path)
            tree = self.get_tree(path_info)
            assert tree.exists(path_info)
            filename = tree.get_file_name(path_info)
            assert filename == answer

    def test_get_file_name_non_existing(self):
        for invalid_path in self.invalid_paths:
            path = "gdrive://" + invalid_path
            path_info = GDriveURLInfo(path)

            tree = self.get_tree(path_info)
            assert not tree.exists(path_info)

            with pytest.raises(FileMissingError) as e:
                _ = tree.get_file_name(path_info)
            assert path in str(e.value)