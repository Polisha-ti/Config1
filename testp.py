import unittest
import os
import math
import shutil
import zipfile
import getpass
from shellp import ShellEmulator

class TestShellEmulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Создание виртуальной файловой системы перед тестами."""
        cls.fs_zip = 'test_virtual_fs.zip'
        cls.fs_root = '/tmp/shell_emulator_fs'
        os.makedirs('test_virtual_fs', exist_ok=True)
        
        # Создаем файлы
        with open('test_virtual_fs/file1.txt', 'w') as f:
            f.write("строка1\nстрока2\nстрока1\n")
        with open('test_virtual_fs/file2.txt', 'w') as f:
            f.write("строка3\nстрока4\n")
        os.makedirs('test_virtual_fs/subdir', exist_ok=True)
        with open('test_virtual_fs/subdir/file3.txt', 'w') as f:
            f.write("строка5\nстрока6\n")

        # Архивируем
        with zipfile.ZipFile(cls.fs_zip, 'w') as zipf:
            for root, dirs, files in os.walk('test_virtual_fs'):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), 'test_virtual_fs')
                    )

    @classmethod
    def tearDownClass(cls):
        """Очистка после тестов."""
        shutil.rmtree('test_virtual_fs')
        os.remove(cls.fs_zip)

    def setUp(self):
        """Инициализация эмулятора перед каждым тестом."""
        self.shell = ShellEmulator("test-host", self.fs_zip, None)

    def tearDown(self):
        """Очистка директории после каждого теста."""
        shutil.rmtree(self.shell.fs_root, ignore_errors=True)

    # Тесты для команды `ls`
    def test_ls_root(self):
        """Проверка команды ls в корне."""
        result = self.shell.run_command("ls")
        self.assertIn("file1.txt", result)
        self.assertIn("file2.txt", result)
        self.assertIn("subdir", result)

    def test_ls_subdir(self):
        """Проверка команды ls в поддиректории."""
        self.shell.run_command("cd subdir")
        result = self.shell.run_command("ls")
        self.assertIn("file3.txt", result)

    def test_ls_invalid_dir(self):
        """Проверка команды ls в несуществующей директории."""
        self.shell.current_directory = "/nonexistent"
        result = self.shell.run_command("ls")
        self.assertIn("Путь '/nonexistent' не существует", result)

    # Тесты для команды `cd`
    def test_cd_to_subdir(self):
        """Проверка команды cd в поддиректорию."""
        result = self.shell.run_command("cd subdir")
        self.assertEqual(result, "Перешли в директорию: /subdir")

    def test_cd_to_parent_dir(self):
        """Проверка команды cd .. для возврата на уровень выше."""
        self.shell.run_command("cd subdir")
        result = self.shell.run_command("cd ..")
        self.assertEqual(result, "Перешли в директорию: /")

    def test_cd_invalid_dir(self):
        """Проверка команды cd в несуществующую директорию."""
        result = self.shell.run_command("cd invalid_dir")
        self.assertEqual(result, "Директория 'invalid_dir' не существует.")

    # Тесты для команды `whoami`
    def test_whoami_user(self):
        """Проверка команды whoami."""
        result = self.shell.run_command("whoami")
        self.assertEqual(result, getpass.getuser())

    def test_whoami_after_ls(self):
        """Выполнение whoami после другой команды."""
        self.shell.run_command("ls")
        result = self.shell.run_command("whoami")
        self.assertEqual(result, getpass.getuser())

    def test_whoami_with_no_fs(self):
        """Выполнение whoami без изменений файловой системы."""
        result = self.shell.run_command("whoami")
        self.assertEqual(result, getpass.getuser())

    # Тесты для команды `uniq`
    def test_uniq_remove_duplicates(self):
        """Проверка uniq для удаления дубликатов."""
        result = self.shell.run_command("uniq file1.txt")
        self.assertEqual(result.strip(), "строка1\nстрока2")

    def test_uniq_empty_file(self):
        """Проверка uniq на пустом файле."""
        with open(os.path.join(self.shell.fs_root, "empty.txt"), "w") as f:
            pass
        result = self.shell.run_command("uniq empty.txt")
        self.assertEqual(result.strip(), "")

    def test_uniq_invalid_file(self):
        """Проверка uniq для несуществующего файла."""
        result = self.shell.run_command("uniq nonexistent.txt")
        self.assertIn("Файл 'nonexistent.txt' не существует.", result)


if __name__ == "__main__":
    unittest.main()
