import random


# Функция аналогична функции из файла с шифратором
# Служит источником потокового ключа для операции XOR
def generate_keystream(secret_key, nonce, bit_length):
    prng = random.Random()
    prng.seed(f"{secret_key}_{nonce}")
    return "".join(str(prng.randint(0, 1)) for _ in range(bit_length))


# Функция читает текстовый файл, игнорирует мусор,
# переводит графические символы обратно в нули и единицы, и вырезает чистую матрицу
def parse_ascii_grid(filepath):
    on = "██"
    off = "  "
    raw_grid = [] # Список для сырых данных
    # Читаем данные и очищаем их от мусора
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n\r')
            # Пропускаем пустые строки
            if not line.strip():
                continue
            # Создаем множество из уникальных символов строки (если есть что-то, кроме нужных символов - выбрасываем)
            chars_in_line = set(line.strip())
            if not chars_in_line.issubset({'█', ' '}):
                continue
            # Нормализуем (переводим визуальные обозначения обратно в 0 и 1)
            filtered = [c for c in line.replace(on, "1").replace(off, "0") if c in ('0', '1')]
            if filtered:
                raw_grid.append(filtered)

    # Ищем границы по высоте (Самая первая и самая последняя строки, содержащие хотя бы одну 1)
    y_coords = [y for y, row in enumerate(raw_grid) if '1' in row]
    min_y = y_coords[0]
    max_y = y_coords[-1]
    # Ищем границы по ширине (Самая левая и самая правая единицы задают боковые границы кадра)
    x_coords = [x for y in range(min_y, max_y + 1) for x, val in enumerate(raw_grid[y]) if val == '1']
    min_x = min(x_coords)
    max_x = max(x_coords)
    grid = [] # Список полностью очищенных данных
    width = max_x + 1 - min_x # Вычисляем ширину матрицы данных
    # Обрезаем все лишнее
    for y in range(min_y, max_y + 1):
        row = raw_grid[y][min_x: max_x + 1]
        grid.append(row)
    return grid


# Функция для дешифрации шифра
# При необходимости поворачивает шифр для правильной ориентации
# С помощью симметрии операции XOR и считанных данных определяет зашифрованное число
def decrypt_matrix(grid, secret_key):
    # Отсекаем внешнюю защитную рамку
    core = [row[2:-2] for row in grid[2:-2]]
    N = len(core) # Размер ядра данных
    # Автоповорот шифра
    for _ in range(4):
        marker_found = True # Флаг, показывающий, что маркер на месте
        for my in range(4):
            for mx in range(4):
                # Сравниваем каждый реальный пиксель ядра с эталоном (expected)
                if mx < 3 and my < 3 and not (mx == 1 and my == 1):
                    expected = '1'
                else:
                    expected = '0'
                # Прерываем, если хотя бы один пиксель не совпал
                if core[my][mx] != expected:
                    marker_found = False
                    break
            if not marker_found:
                break
        # Если нашли маркер, завершаем цикл, иначе - делаем поворот матрицы на 90 градусов
        if marker_found:
            break
        core = [list(row) for row in zip(*core[::-1])]

    # Считываем метаданные
    # Задаем размеры зон и высчитываем координаты левого верхнего угла центрального блока
    meta_w = 14
    meta_h = 12
    marker_zone = 4
    cx = (N - meta_w) // 2
    cy = (N - meta_h) // 2
    # Считываем данные из внутренней рамки (минуя 3 слоя рамки)
    meta_bits = ""
    for y in range(6):
        for x in range(8):
            meta_bits += core[cy + 3 + y][cx + 3 + x]

    # Разделяем считанные данные на 16 бит зашифрованной длины и 32 бита как открытый вектор (nonce)
    encrypted_len_bits = meta_bits[:16]
    nonce = int(meta_bits[16:], 2)
    # Расшифровываем длину аналогично шифрации (так как операция XOR симметрична)
    len_keystream = generate_keystream(secret_key, nonce, 16)
    decrypted_len_bits = "".join(str(int(m) ^ int(k)) for m, k in zip(encrypted_len_bits, len_keystream))
    bit_length = int(decrypted_len_bits, 2)
    # Собираем первые bit_length бит - наше исходное зашифрованное число
    encrypted_bits = ""
    for y in range(N):
        for x in range(N):
            # Пропускаем зону маркера
            if x < marker_zone and y < marker_zone:
                continue
            # Пропускаем зону метаданных
            if cx <= x < cx + meta_w and cy <= y < cy + meta_h:
                continue
            # Собираем биты пока не наберем нужную длину
            if len(encrypted_bits) < bit_length:
                encrypted_bits += core[y][x]

    # Аналогично дешифруем исходное число
    full_keystream = generate_keystream(secret_key, nonce, 16 + bit_length)
    data_keystream = full_keystream[16:]
    decrypted_bits = "".join(str(int(c) ^ int(k)) for c, k in zip(encrypted_bits, data_keystream))
    return int(decrypted_bits, 2)


if __name__ == "__main__":
    filepath = input("Введите путь к файлу с шифром (например, ../data/cipher.txt или data/cipher.txt (если запуск из корня проекта)): ").strip()
    SECRET_KEY = input("Введите секретный ключ: ").strip()
    grid = parse_ascii_grid(filepath)
    result = decrypt_matrix(grid, SECRET_KEY)
    print(f"РАСШИФРОВАННОЕ ЧИСЛО:\n{result}")