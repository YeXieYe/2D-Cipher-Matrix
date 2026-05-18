# Функция читает текстовый файл с шифром, очищает его от посторонних символов
# и вырезает часть матрицы с данными, отбрасывая пустые края
def parse_ascii_grid(filepath):
    # Список для хранения сырых данных из файла
    raw_grid = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Пропуск пустых строк и строк, содержащих посторонние символы
            if not line or not set(line).issubset({'█', ' '}):
                continue

            # Перевод визуальных блоков в бинарный формат (в 0 и 1)
            replaced_line = line.replace("██", "1").replace("  ", "0")
            filtered_row = [c for c in replaced_line if c in ('0', '1')]
            if filtered_row:
                raw_grid.append(filtered_row)

    # Поиск верхней и нижней границ части матрицы с данными
    y_coords = [y for y, row in enumerate(raw_grid) if '1' in row]
    min_y = y_coords[0]
    max_y = y_coords[-1]

    # Поворот матрицы для удобного поиска левой и правой границ
    transposed_grid = list(zip(*raw_grid))

    # Поиск левой и правой границ
    x_coords = [x for x, col in enumerate(transposed_grid) if '1' in col]
    min_x = min(x_coords)
    max_x = max(x_coords)

    # Формирование итоговой матрицы путем обрезки пустых краев
    grid = [raw_grid[y][min_x:max_x + 1] for y in range(min_y, max_y + 1)]
    return grid


# Функция извлекает данные из матрицы, восстанавливает криптографическую маску
# и расшифровывает исходное число
def decrypt_matrix(grid, secret_key):
    # Удаление внешней защитной рамки (первые и последние 2 строки/столбца)
    core = [row[2:-2] for row in grid[2:-2]]

    # Размер рабочей области матрицы
    matrix_size = len(core)

    # Автоматический поворот матрицы до тех пор, пока маркер не окажется в левом верхнем углу
    for _ in range(4):
        marker_found = True
        for my in range(4):
            for mx in range(4):
                # Ожидаемый шаблон маркера (квадрат 3x3 с пустой серединой)
                if mx < 3 and my < 3 and not (mx == 1 and my == 1):
                    expected = '1'
                else:
                    expected = '0'
                if core[my][mx] != expected:
                    marker_found = False
                    break
            if not marker_found:
                break

        if marker_found:
            break

        # Поворот матрицы на 90 градусов
        core = [list(row) for row in zip(*core[::-1])]

    # Габариты служебных зон
    meta_w = 14
    meta_h = 8
    marker_zone = 4

    # Вычисление координат центральной зоны метаданных
    cx = (matrix_size - meta_w) // 2
    cy = (matrix_size - meta_h) // 2

    # Извлечение зашифрованной длины из центрального блока
    encrypted_len_bits = ""
    for y in range(2):
        for x in range(8):
            encrypted_len_bits += core[cy + 3 + y][cx + 3 + x]

    # Чтение основного потока данных (в обход маркера и метаданных, 3 бита через 1 бит nonce)
    payload_bits = ""
    for x in range(matrix_size):
        for y in range(matrix_size):
            if x < marker_zone and y < marker_zone:
                continue
            if cx <= x < cx + meta_w and cy <= y < cy + meta_h:
                continue
            payload_bits += core[y][x]

    # Извлечение одноразового номера (каждый 4-й бит, инвертированный)
    nonce_bits = ""
    for i in range(16):
        if payload_bits[i * 4 + 3] == '1':
            nonce_bits += '0'
        else:
            nonce_bits += '1'

    # Перевод символов секретного ключа в бинарный формат (по 8 бит на символ)
    key_bits = "".join(format(ord(c), '08b') for c in secret_key)

    # Вычисление длины криптографической маски
    total_len = 16 + len(payload_bits)

    # Растягивание ключа и одноразового номера до нужной длины маски
    extended_key = "".join(key_bits[i % len(key_bits)] for i in range(total_len))
    extended_nonce = "".join(nonce_bits[i % len(nonce_bits)] for i in range(total_len))

    # Восстановление криптографической маски операцией XOR
    mask = "".join(str(int(k) ^ int(n)) for k, n in zip(extended_key, extended_nonce))

    # Расшифровка длины исходного числа (используются первые 16 бит маски)
    decrypted_len_bits = "".join(str(int(m) ^ int(k)) for m, k in zip(encrypted_len_bits, mask[:16]))

    # Перевод бинарной длины в десятичное число
    bit_length = int(decrypted_len_bits, 2)

    # Очистка потока от битов одноразового номера (оставляем только данные и шум)
    encrypted_data_bits = ""
    for i in range(len(payload_bits)):
        if i % 4 != 3:
            encrypted_data_bits += payload_bits[i]

    # Отсечение случайного шума в конце потока на основе расшифрованной длины
    encrypted_data_bits = encrypted_data_bits[:bit_length]

    # Финальная расшифровка числа с использованием оставшейся части маски
    decrypted_bits = "".join(str(int(c) ^ int(k)) for c, k in zip(encrypted_data_bits, mask[16:16 + bit_length]))
    return int(decrypted_bits, 2)


if __name__ == "__main__":
    filepath = input("Введите путь к файлу с шифром (например ../data/cipher_1.txt для запуска из корня): ").strip()
    secret_key = input("Введите секретный ключ: ").strip()
    grid = parse_ascii_grid(filepath)
    result = decrypt_matrix(grid, secret_key)
    print(f"\nРасшифрованное число:\n{result}")