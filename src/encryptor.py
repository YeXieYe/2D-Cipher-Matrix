import math
import random


# Генератор псевдослучайной последовательности битов
# Генерирует псевдослучайное число длиной bit_length на основе сида (ключ шифрования + вектор инициализации)
# Служит источником потокового ключа для операции XOR
def generate_keystream(secret_key, nonce, bit_length):
    prng = random.Random()
    prng.seed(f"{secret_key}_{nonce}")
    return "".join(str(prng.randint(0, 1)) for _ in range(bit_length))


# Функция симметричного шифрования двоичной формы исходного числа и его длины
# Шифрует число с помощью сгенерированного потокового ключа и операции XOR
def encrypt(number, secret_key):
    target_bin = bin(number)[2:] # Шифруемое число в двоичной форме
    bit_length = len(target_bin) # Длина числа
    nonce = random.randint(100000, 4294967295)
    keystream = generate_keystream(secret_key, nonce, 16 + bit_length) # Генерируем последовательность для XOR
    len_bin = format(bit_length, '016b')
    # Шифрование числа и его длины с помощью XOR
    encrypted_len = "".join(str(int(m) ^ int(k)) for m, k in zip(len_bin, keystream[:16]))
    encrypted_bits = "".join(str(int(m) ^ int(k)) for m, k in zip(target_bin, keystream[16:]))
    return encrypted_bits, nonce, encrypted_len


# Функция для формирования двухмерной матрицы (для визуального представления шифра)
def draw_2d_cipher(encrypted_bits, nonce, encrypted_len):
    # Визуальное представление 1 и 0
    on = "██"
    off = "  "
    # Ширина и высота центрального блока с метаданными, а также размер углового маркера
    meta_w = 14
    meta_h = 12
    marker_zone = 4
    # Расчет площади и габаритов матрицы
    meta_bits = encrypted_len + format(nonce, '032b')
    total_cells = len(encrypted_bits) + (meta_w * meta_h) + (marker_zone * marker_zone)
    core_n = max(20, math.ceil(math.sqrt(total_cells)))
    n = core_n + 4
    core_offset = 2
    # Вычисление глобальных координат левого верхнего угла центрального блока метаданных
    cx = core_offset + (core_n - meta_w) // 2
    cy = core_offset + (core_n - meta_h) // 2
    grid = [[' ' for _ in range(n)] for _ in range(n)] # Матрица хранения двухмерного отображения шифра
    # СЛОЙ 1: Защитный отступ и внешняя граница
    for y in range(n):
        for x in range(n):
            if x == 0 or x == n - 1 or y == 0 or y == n - 1:
                grid[y][x] = on
            elif x == 1 or x == n - 2 or y == 1 or y == n - 2:
                grid[y][x] = off

    # СЛОЙ 2: Угловой маркер позиционирования и ориентации
    for y in range(marker_zone):
        for x in range(marker_zone):
            gx, gy = core_offset + x, core_offset + y
            if x < 3 and y < 3 and not (x == 1 and y == 1):
                grid[gy][gx] = on
            else:
                grid[gy][gx] = off

    # СЛОЙ 3: Блок метаданных (структурированная запись Nonce и длины)
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

    # СЛОЙ 4: Зашифрованное число и криптографический шум для заполнения пустот
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

    # Вывод результата в консоль
    for row in grid:
        print("  " + "".join(row) + "  ")


if __name__ == "__main__":
    target_number = int(input("Введите число для шифрования: ").strip())
    secret_key = input("Введите секретный ключ: ").strip()
    enc_bits, current_nonce, enc_length = encrypt(target_number, secret_key)
    draw_2d_cipher(enc_bits, current_nonce, enc_length)
