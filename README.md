Задание №1
Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС. Эмулятор должен запускаться из реальной командной строки, а файл с виртуальной файловой системой не нужно распаковывать у пользователя. Эмулятор принимает образ виртуальной файловой системы в виде файла формата zip. Эмулятор должен работать в режиме GUI.
Лог-файл имеет формат json и содержит все действия во время последнего сеанса работы с эмулятором. Для каждого действия указаны дата и время.
Стартовый скрипт служит для начального выполнения заданного списка команд из файла.
Необходимо поддержать в эмуляторе команды ls, cd и exit, а также следующие команды:
1. uniq.
2. who.
3. whoami.
Все функции эмулятора должны быть покрыты тестами, а для каждой из поддерживаемых команд необходимо написать 3 теста.
