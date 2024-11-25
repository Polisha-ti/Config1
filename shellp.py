import os
import zipfile
import argparse
import json
import shutil
import sys
import getpass
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulator:
    def __init__(self, hostname, fs_archive, startup_script):
        self.hostname = hostname
        self.current_directory = '/'
        self.fs_root = '/tmp/shell_emulator_fs'
        self.log_file = "shell_log.json"
        self.log_data = []

        # Распаковка виртуальной файловой системы
        self.extract_fs(fs_archive)

        # Запуск стартового скрипта, если он задан
        if startup_script:
            self.execute_startup_script(startup_script)

    def extract_fs(self, fs_archive):
        """Распаковывает виртуальную файловую систему в заданную папку."""
        if os.path.exists(self.fs_root):
            shutil.rmtree(self.fs_root)
        os.makedirs(self.fs_root)

        with zipfile.ZipFile(fs_archive, 'r') as zip_ref:
            zip_ref.extractall(self.fs_root)

    def execute_startup_script(self, script_path):
        """Выполняет команды из стартового скрипта."""
        with open(script_path, 'r') as script:
            for line in script:
                self.run_command(line.strip())

    def prompt(self):
        """Возвращает приглашение к вводу."""
        return f"{self.hostname}:{self.current_directory}$ "

    def log_action(self, command, result=None):
        """Логирует команды и результаты в JSON."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result if result else "None",
        }
        self.log_data.append(log_entry)
        with open(self.log_file, 'w') as log:
            json.dump(self.log_data, log, ensure_ascii=False, indent=4)

    def run_command(self, command):
        """Обрабатывает ввод пользователя."""
        if command.startswith('ls'):
            return self.ls()
        elif command.startswith('cd'):
            return self.cd(command.split(' ')[1] if len(command.split()) > 1 else '/')
        elif command == 'whoami':
            return self.whoami()
        elif command == 'who':
            return self.who()
        elif command == 'exit':
            self.exit()
        elif command.startswith('uniq'):
            _, file = command.split(' ')
            return self.uniq(file)
        else:
            result = f"Команда '{command}' не поддерживается."
            return result

    def ls(self):
        """Команда ls."""
        path = os.path.join(self.fs_root, self.current_directory.strip('/'))
        if os.path.exists(path):
            files = os.listdir(path)
            result = '  '.join(files)
            return result  # Возвращаем строку результата
        else:
            return f"Путь '{self.current_directory}' не существует."  # Возвращаем сообщение об ошибке

    def cd(self, path):
        if path.startswith('/'):
            new_dir = os.path.join(self.fs_root, path.strip('/'))
        else:
            new_dir = os.path.join(self.fs_root, self.current_directory.strip('/'), path.strip('/'))

    # Обработка '..' для возврата на уровень выше
        if path == '..':
            self.current_directory = os.path.dirname(self.current_directory.rstrip('/'))
            if not self.current_directory:
                self.current_directory = '/'
            return f"Перешли в директорию: {self.current_directory}"

        if os.path.isdir(new_dir):
            if path.startswith('/'):
                self.current_directory = '/' + path.strip('/')
            else:
                self.current_directory = os.path.join(self.current_directory, path).replace('\\', '/')
            return f"Перешли в директорию: {self.current_directory}"
        else:
            return f"Директория '{path}' не существует."




    def whoami(self):
        """Команда whoami."""
        return getpass.getuser()

    def who(self):
        """Команда who."""
        return os.popen('who').read().strip()

    def uniq(self, file):
        """Команда uniq."""
        file_path = os.path.join(self.fs_root, self.current_directory.strip('/'), file.strip('/'))
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
                unique_lines = sorted(set(lines), key=lines.index)
                return ''.join(unique_lines)
        else:
            return f"Файл '{file}' не существует."
        
    def exit(self):
        """Команда exit."""
        print("Выход из эмулятора.")
        sys.exit(0)

class ShellGUI:
    def __init__(self, shell):
        self.shell = shell
        self.root = tk.Tk()
        self.root.title("Shell Emulator")

        # Поле ввода команды
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.command_label = tk.Label(self.input_frame, text="Команда:")
        self.command_label.pack(side=tk.LEFT, padx=5)

        self.command_entry = tk.Entry(self.input_frame, width=50)
        self.command_entry.pack(side=tk.LEFT, padx=5)

        self.run_button = tk.Button(self.input_frame, text="Выполнить", command=self.run_command)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.input_frame, text="Очистить", command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Поле вывода результатов
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.output_text = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Запуск GUI
        self.root.mainloop()

    def run_command(self):
        """Обрабатывает выполнение команды через GUI."""
        command = self.command_entry.get()
        if not command:
            return

        # Выполняем команду и записываем результат
        result = self.shell.run_command(command)
        self.shell.log_action(command, result)
        self.display_output(f"{self.shell.prompt()}{command}\n{result}\n")

    def display_output(self, text):
        """Выводит текст в окно вывода."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def clear_output(self):
        """Очищает окно вывода."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)


def generate_files():
    """Функция для генерации всех нужных файлов в директории."""
    virtual_fs_dir = 'virtual_fs'
    if not os.path.exists(virtual_fs_dir):
        os.makedirs(virtual_fs_dir)
        with open(os.path.join(virtual_fs_dir, 'file1.txt'), 'w') as f:
            f.write("Это содержимое файла 1.\n")
        with open(os.path.join(virtual_fs_dir, 'file2.txt'), 'w') as f:
            f.write("Это содержимое файла 2.\nЭто содержимое файла 2.\n")

        os.makedirs(os.path.join(virtual_fs_dir, 'subdir'))
        with open(os.path.join(virtual_fs_dir, 'subdir', 'file3.txt'), 'w') as f:
            f.write("Это содержимое файла в поддиректории.\n")

    fs_zip = 'virtual_fs.zip'
    with zipfile.ZipFile(fs_zip, 'w') as zip_ref:
        for root, dirs, files in os.walk(virtual_fs_dir):
            for file in files:
                zip_ref.write(os.path.join(root, file), 
                              os.path.relpath(os.path.join(root, file), virtual_fs_dir))

    print(f"Создан архив виртуальной файловой системы: {fs_zip}")

    startup_script = 'startup_script.sh'
    with open(startup_script, 'w') as f:
        f.write('ls\n')
        f.write('cd subdir\n')
        f.write('ls\n')
        f.write('whoami\n')
        f.write('cd')

    print(f"Создан стартовый скрипт: {startup_script}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Эмулятор shell для UNIX-подобных систем.")
    parser.add_argument("--hostname", required=True, help="Имя компьютера для показа в приглашении к вводу.")
    parser.add_argument("--filesystem", required=True, help="Путь к архиву виртуальной файловой системы.")
    parser.add_argument("--startup_script", help="Путь к стартовому скрипту для выполнения команд.")
    parser.add_argument("--generate_files", action="store_true", help="Сгенерировать все необходимые файлы в текущей директории.")

    args = parser.parse_args()

    if args.generate_files:
        generate_files()
    else:
        shell = ShellEmulator(args.hostname, args.filesystem, args.startup_script)
        ShellGUI(shell)
