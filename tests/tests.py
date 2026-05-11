import math
import random


def generate_keystream(secret_key, nonce, bit_length):
    prng = random.Random()
    prng.seed(f"{secret_key}_{nonce}")
    return "".join(str(prng.randint(0, 1)) for _ in range(bit_length))


def encrypt(number, secret_key):
    target_bin = bin(number)[2:]
    bit_length = len(target_bin)
    nonce = random.randint(100000, 4294967295)
    keystream = generate_keystream(secret_key, nonce, 16 + bit_length)
    len_bin = format(bit_length, '016b')
    encrypted_len = "".join(str(int(m) ^ int(k)) for m, k in zip(len_bin, keystream[:16]))
    encrypted_bits = "".join(str(int(m) ^ int(k)) for m, k in zip(target_bin, keystream[16:]))
    return encrypted_bits, nonce, encrypted_len


# Вспомогательная функция для поворота шифра на угол, кратный 90
def rotate_grid(grid, angle):
    rotated = grid
    rotations = (angle % 360) // 90
    for _ in range(rotations):
        rotated = [list(row) for row in zip(*rotated[::-1])]
    return rotated


# Для поворота шифра добавляем в функцию вывода параметр угла поворота (кратный 90)
def draw_2d_cipher(encrypted_bits, nonce, encrypted_len, rotation=0):
    on = "██"
    off = "  "
    meta_w = 14
    meta_h = 12
    marker_zone = 4
    meta_bits = encrypted_len + format(nonce, '032b')
    total_cells = len(encrypted_bits) + (meta_w * meta_h) + (marker_zone * marker_zone)
    core_n = max(20, math.ceil(math.sqrt(total_cells)))
    n = core_n + 4
    core_offset = 2
    cx = core_offset + (core_n - meta_w) // 2
    cy = core_offset + (core_n - meta_h) // 2
    grid = [[' ' for _ in range(n)] for _ in range(n)]
    for y in range(n):
        for x in range(n):
            if x == 0 or x == n - 1 or y == 0 or y == n - 1:
                grid[y][x] = on
            elif x == 1 or x == n - 2 or y == 1 or y == n - 2:
                grid[y][x] = off

    for y in range(marker_zone):
        for x in range(marker_zone):
            gx, gy = core_offset + x, core_offset + y
            if x < 3 and y < 3 and not (x == 1 and y == 1):
                grid[gy][gx] = on
            else:
                grid[gy][gx] = off

    for y in range(meta_h):
        for x in range(meta_w):
            gx, gy = cx + x, cy + y
            if x == 0 or x == meta_w - 1 or y == 0 or y == meta_h - 1:
                grid[gy][gx] = off
            elif x == 1 or x == meta_w - 2 or y == 1 or y == meta_h - 2:
                grid[gy][gx] = on
            elif x == 2 or x == meta_w - 3 or y == 2 or y == meta_h - 3:
                grid[gy][gx] = off
            else:
                bit_idx = (y - 3) * 8 + (x - 3)
                grid[gy][gx] = on if meta_bits[bit_idx] == '1' else off

    enc_idx = 0
    enc_len = len(encrypted_bits)
    for y in range(core_offset, n - core_offset):
        for x in range(core_offset, n - core_offset):
            if grid[y][x] == ' ':
                if enc_idx < enc_len:
                    bit = encrypted_bits[enc_idx]
                    enc_idx += 1
                else:
                    bit = str(random.randint(0, 1))
                grid[y][x] = on if bit == '1' else off

    # Поворот шифра на угол не равный 0
    if rotation != 0:
        grid = rotate_grid(grid, rotation)

    for row in grid:
        print("  " + "".join(row) + "  ")


if __name__ == "__main__":
    SECRET_KEY = "key" # Ключ шифрования для всех тестов
    test_numbers = [1, 10, 42, 256, 1024, 65535, 999999, 123456789] # Тестовые числа по умолчанию
    # Генерация 100 случайных тестовых чисел
    for _ in range(100):
        length = random.randint(3, 60)
        num = random.randint(10 ** (length - 1), 10 ** length - 1)
        test_numbers.append(num)

    # Вывод тестов
    print(f"ГЕНЕРАЦИЯ {len(test_numbers)} ТЕСТОВ (КЛЮЧ: {SECRET_KEY})\n")
    for i, target_num in enumerate(test_numbers, 1):
        print(f"ТЕСТ {i}")
        print(f"ЧИСЛО: {target_num}")
        enc_bits, current_nonce, enc_len = encrypt(target_num, SECRET_KEY)
        draw_2d_cipher(enc_bits, current_nonce, enc_len)
        print("\n" + "-" * 50 + "\n")

    # Генерация тестов с поворотом
    print(f"ГЕНЕРАЦИЯ ТЕСТОВ С ПОВОРОТОМ МАТРИЦЫ (КЛЮЧ: {SECRET_KEY})\n")
    rotated_tests = [(777, 90), (8888, 180), (99999, 270)] # Задаем тестовые значения и угол поворота шифра
    # Вывод тестов с поворотом
    for i, (target_num, angle) in enumerate(rotated_tests, len(test_numbers) + 1):
        print(f"ТЕСТ {i} [ПОВЕРНУТ НА {angle} ГРАДУСОВ]")
        print(f"ЧИСЛО: {target_num}")
        enc_bits, current_nonce, enc_len = encrypt(target_num, SECRET_KEY)
        draw_2d_cipher(enc_bits, current_nonce, enc_len, rotation=angle)
        print("\n" + "-" * 50 + "\n")