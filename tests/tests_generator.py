import math
import random


def encrypt(number, secret_key):
    target_bin = format(number, 'b')
    bit_length = len(target_bin)

    nonce = random.randint(0, 65535)
    nonce_bin = format(nonce, '016b')
    key_bits = "".join(format(ord(c), '08b') for c in secret_key)

    total_len = 16 + bit_length
    extended_key = "".join(key_bits[i % len(key_bits)] for i in range(total_len))
    extended_nonce = "".join(nonce_bin[i % len(nonce_bin)] for i in range(total_len))
    mask = "".join(str(int(k) ^ int(n)) for k, n in zip(extended_key, extended_nonce))

    len_bin = format(bit_length, '016b')
    encrypted_len = "".join(str(int(m) ^ int(k)) for m, k in zip(len_bin, mask[:16]))
    encrypted_bits = "".join(str(int(d) ^ int(k)) for d, k in zip(target_bin, mask[16:]))

    payload_bits = ""
    data_idx = 0
    nonce_idx = 0
    while data_idx < len(encrypted_bits) or nonce_idx < 16:
        for _ in range(3):
            if data_idx < len(encrypted_bits):
                payload_bits += encrypted_bits[data_idx]
                data_idx += 1
            else:
                payload_bits += random.choice("01")

        if nonce_idx < 16:
            payload_bits += '0' if nonce_bin[nonce_idx] == '1' else '1'
            nonce_idx += 1
        else:
            payload_bits += random.choice("01")

    extra_noise_length = random.randint(30, 150)
    extra_noise = "".join(random.choice("01") for _ in range(extra_noise_length))
    payload_bits += extra_noise
    return payload_bits, encrypted_len


# Функция поворачивает двумерную матрицу на заданный угол (кратный 90 градусам)
def rotate_grid(grid, angle):
    rotated = grid
    rotations = (angle % 360) // 90
    for _ in range(rotations):
        rotated = [list(row) for row in zip(*rotated[::-1])]
    return rotated


# Добавлен параметр rotation для имитации повернутого изображения
def draw_2d_cipher(payload_bits, encrypted_len, rotation=0):
    on = "██"
    off = "  "

    meta_w = 14
    meta_h = 8
    marker_zone = 4

    total_cells = len(payload_bits) + (meta_w * meta_h) + (marker_zone ** 2)
    core_n = max(20, math.ceil(math.sqrt(total_cells)))
    n = core_n + 4

    core_offset = 2
    cx = core_offset + (core_n - meta_w) // 2
    cy = core_offset + (core_n - meta_h) // 2

    grid = [[' ' for _ in range(n)] for _ in range(n)]

    for y in range(n):
        for x in range(n):
            if x in (0, n - 1) or y in (0, n - 1):
                grid[y][x] = on
            elif x in (1, n - 2) or y in (1, n - 2):
                grid[y][x] = off

    for y in range(marker_zone):
        for x in range(marker_zone):
            gx = core_offset + x
            gy = core_offset + y
            if x < 3 and y < 3 and not (x == 1 and y == 1):
                grid[gy][gx] = on
            else:
                grid[gy][gx] = off

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
                bit_idx = (y - 3) * 8 + (x - 3)
                grid[gy][gx] = on if encrypted_len[bit_idx] == '1' else off

    enc_idx = 0
    enc_len = len(payload_bits)

    for x in range(core_offset, n - core_offset):
        for y in range(core_offset, n - core_offset):
            if grid[y][x] == ' ':
                if enc_idx < enc_len:
                    bit = payload_bits[enc_idx]
                    enc_idx += 1
                else:
                    bit = random.choice("01")
                grid[y][x] = on if bit == '1' else off

    # Применение поворота матрицы перед выводом (для тестов)
    if rotation != 0:
        grid = rotate_grid(grid, rotation)

    for row in grid:
        print("  " + "".join(row) + "  ")


if __name__ == "__main__":
    # Единый секретный ключ для генерации всех тестовых матриц
    SECRET_KEY = "key"

    # Базовый набор контрольных чисел (от простых до больших)
    test_numbers = [1, 10, 42, 256, 1024, 65535, 999999, 123456789]

    # Генерация 100 случайных чисел различной размерности
    for _ in range(100):
        length = random.randint(3, 60)
        num = random.randint(10 ** (length - 1), 10 ** length - 1)
        test_numbers.append(num)

    # Вывод обычный тестов
    print(f"ГЕНЕРАЦИЯ {len(test_numbers)} ТЕСТОВ (КЛЮЧ: {SECRET_KEY})\n")
    for i, target_num in enumerate(test_numbers, 1):
        print("```")
        print(f"ТЕСТ {i}")
        print(f"ЧИСЛО: {target_num}")
        payload, enc_length = encrypt(target_num, SECRET_KEY)
        draw_2d_cipher(payload, enc_length)
        print("\n" + "-" * 50)
        print("```\n")

    # Вывод тестов троек одинаковых чисел
    print(f"ГЕНЕРАЦИЯ ТЕСТОВ С ТРОЙКАМИ ОДИНАКОВЫХ ЧИСЕЛ (КЛЮЧ: {SECRET_KEY})\n")

    # Задаем 4 размера чисел для тестирования
    triplet_lengths = [1, 10, 25, 50]
    triplet_test_idx = 1

    for length in triplet_lengths:
        # Генерируем одно случайное число заданной длины
        target_num = random.randint(10 ** (length - 1) if length > 1 else 0, 10 ** length - 1)

        print(f"=== ГРУППА: 3 одинаковых теста для числа длиной {length} цифр ===")
        for _ in range(3):
            print("```")
            print(f"ТЕСТ {triplet_test_idx} [ТРОЙКИ ОДИНАКОВЫХ]")
            print(f"ЧИСЛО: {target_num}")
            payload, enc_length = encrypt(target_num, SECRET_KEY)
            draw_2d_cipher(payload, enc_length)
            print("\n" + "-" * 50)
            print("```\n")
            triplet_test_idx += 1

    # Вывод тестов с поворотом
    print(f"ГЕНЕРАЦИЯ ТЕСТОВ С ПОВОРОТОМ МАТРИЦЫ (КЛЮЧ: {SECRET_KEY})\n")

    # Кортежи формата: (зашифрованное число, угол поворота)
    rotated_tests = [(777, 90), (8888, 180), (99999, 270)]

    # Вывод тестов с поворотом итоговой матрицы
    for i, (target_num, angle) in enumerate(rotated_tests, triplet_test_idx):
        print("```")
        print(f"ТЕСТ {i} [ПОВЕРНУТ НА {angle} ГРАДУСОВ]")
        print(f"ЧИСЛО: {target_num}")
        payload, enc_length = encrypt(target_num, SECRET_KEY)
        draw_2d_cipher(payload, enc_length, rotation=angle)
        print("\n" + "-" * 50)
        print("```\n")