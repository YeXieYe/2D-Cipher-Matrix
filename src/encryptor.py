import math
import random


# Функция шифрует целое число с использованием ключа и одноразового случайного значения (nonce)
# Генерирует поток данных, в котором скрыты биты числа и случайное значение
def encrypt(number, secret_key):
    # Перевод исходного числа и его размер в двоичный формат
    target_bin = format(number, 'b')
    bit_length = len(target_bin)

    # Генерация одноразового номера (nonce) для обеспечения уникальности каждого шифрования
    nonce = random.randint(0, 65535)
    nonce_bin = format(nonce, '016b')

    # Перевод символов секретного ключа в бинарный формат (по 8 бит на символ)
    key_bits = "".join(format(ord(c), '08b') for c in secret_key)

    # Общий объем полезных бит: 16 бит для хранения длины + биты самого числа
    total_len = 16 + bit_length

    # Растягивание ключа и одноразового номера до общего объема бит
    extended_key = "".join(key_bits[i % len(key_bits)] for i in range(total_len))
    extended_nonce = "".join(nonce_bin[i % len(nonce_bin)] for i in range(total_len))

    # Создание шифрующей маски с помощью операции XOR
    mask = "".join(str(int(k) ^ int(n)) for k, n in zip(extended_key, extended_nonce))

    # Шифрование размера данных (используем для этого первые 16 бит маски)
    len_bin = format(bit_length, '016b')
    encrypted_len = "".join(str(int(m) ^ int(k)) for m, k in zip(len_bin, mask[:16]))

    # Шифрование самого числа (используем остальные биты маски)
    encrypted_bits = "".join(str(int(d) ^ int(k)) for d, k in zip(target_bin, mask[16:]))

    # Итоговый бинарный поток и счетчики позиций
    payload_bits = ""
    data_idx = 0
    nonce_idx = 0

    # Смешиваем биты зашифрованного числа и одноразового номера
    # последовательность: 3 бита данных/шума -> 1 инвертированный бит одноразового номера/шума
    while data_idx < len(encrypted_bits) or nonce_idx < 16:
        # Запись 3 бит данных (или случайного шума, если данные закончились)
        for _ in range(3):
            if data_idx < len(encrypted_bits):
                payload_bits += encrypted_bits[data_idx]
                data_idx += 1
            else:
                payload_bits += random.choice("01")

        # Запись 1 инвертированного бита одноразового номера (или шума)
        if nonce_idx < 16:
            if nonce_bin[nonce_idx] == '1':
                payload_bits += '0'
            else:
                payload_bits += '1'
            nonce_idx += 1
        else:
            payload_bits += random.choice("01")

    # Добавление случайного количества шума в конец (дополнительная защита от расшифровки)
    extra_noise_length = random.randint(30, 150)
    extra_noise = "".join(random.choice("01") for _ in range(extra_noise_length))
    payload_bits += extra_noise
    return payload_bits, encrypted_len


# Функция визуализирует зашифрованный битовый поток в виде двумерной матрицы
# Строит защитные рамки, маркер ориентации и область метаданных
def draw_2d_cipher(payload_bits, encrypted_len):
    # Визуальные представления битов (1 - закрашено, 0 - пусто)
    on = "██"
    off = "  "

    # Габариты центральной зоны для хранения зашифрованной длины
    meta_w = 14
    meta_h = 8

    # Размер квадратного маркера ориентации в левом верхнем углу
    marker_zone = 4

    # Расчет площади и габаритов внутренней рабочей области
    total_cells = len(payload_bits) + (meta_w * meta_h) + (marker_zone ** 2)
    core_n = max(20, math.ceil(math.sqrt(total_cells)))

    # Итоговый размер матрицы с учетом внешней рамки (толщиной в 2 пикселя)
    n = core_n + 4
    core_offset = 2

    # Координаты начала центральной зоны метаданных
    cx = core_offset + (core_n - meta_w) // 2
    cy = core_offset + (core_n - meta_h) // 2

    # Создание пустой двумерной сетки
    grid = [[' ' for _ in range(n)] for _ in range(n)]

    # Отрисовка внешней двойной рамки
    for y in range(n):
        for x in range(n):
            if x in (0, n - 1) or y in (0, n - 1):
                grid[y][x] = on
            elif x in (1, n - 2) or y in (1, n - 2):
                grid[y][x] = off

    # Отрисовка углового маркера ориентации
    for y in range(marker_zone):
        for x in range(marker_zone):
            gx = core_offset + x
            gy = core_offset + y
            if x < 3 and y < 3 and not (x == 1 and y == 1):
                grid[gy][gx] = on
            else:
                grid[gy][gx] = off

    # Отрисовка зоны метаданных (защитный контур и биты зашифрованной длины числа внутри)
    for y in range(meta_h):
        for x in range(meta_w):
            gx = cx + x
            gy = cy + y
            if x in (0, meta_w - 1) or y in (0, meta_h - 1):
                grid[gy][gx] = off
            elif x in (1, meta_w - 2) or y in (1, meta_h - 2):
                grid[gy][gx] = on
            elif x in (2, meta_w - 3) or y in (2, meta_h - 3):
                grid[gy][gx] = off
            else:
                # Извлечение бит из строки encrypted_len для заполнения центра
                bit_idx = (y - 3) * 8 + (x - 3)
                if encrypted_len[bit_idx] == '1':
                    grid[gy][gx] = on
                else:
                    grid[gy][gx] = off

    # Индексы для чтения основного потока данных
    enc_idx = 0
    enc_len = len(payload_bits)

    # Заполнение пустого пространства матрицы по столбцам (делаем вертикальную укладку для дополнительной защиты от ии)
    for x in range(core_offset, n - core_offset):
        for y in range(core_offset, n - core_offset):
            if grid[y][x] == ' ':
                # Чтение бита из данных или генерация шума, если данные кончились
                if enc_idx < enc_len:
                    bit = payload_bits[enc_idx]
                    enc_idx += 1
                else:
                    bit = random.choice("01")
                if bit == '1':
                    grid[y][x] = on
                else:
                    grid[y][x] = off

    # Построчный вывод итоговой матрицы в консоль
    for row in grid:
        print("  " + "".join(row) + "  ")


if __name__ == "__main__":
    target_number = int(input("Введите число для шифрования: ").strip())
    secret_key = input("Введите секретный ключ: ").strip()
    payload, enc_length = encrypt(target_number, secret_key)
    draw_2d_cipher(payload, enc_length)