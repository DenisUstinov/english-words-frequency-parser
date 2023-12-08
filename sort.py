def sort_and_save(input_filename, output_filename):
    try:
        # Чтение строк из файла
        with open(input_filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Сортировка строк по алфавиту
        sorted_lines = sorted(lines)

        # Сохранение отсортированных строк в другой файл
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            output_file.writelines(sorted_lines)

        print(f'Строки из файла "{input_filename}" были отсортированы и сохранены в файл "{output_filename}".')
    except Exception as e:
        print(f'Произошла ошибка: {e}')

# Пример использования функции
sort_and_save('output.txt', 'output_sorted.txt')
