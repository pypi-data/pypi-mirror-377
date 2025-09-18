import numpy as np
import matplotlib.pyplot as plt
import math


def gcd(a, b):
    """
    Euclidean Algorithm to compute gcd(a, b).
    Parameters
    ----------
    a : int First integer.
    b : int Second integer.

    """
    A, B = a, b  # เก็บค่าเดิมไว้เพื่อใช้ตอนสรุป
    print(f"gcd({A}, {B})")
    while b:
        q = a // b 
        r = a % b   
        print(f"{a} = {b} * {q} + {r}")
        a, b = b, r
    print(f"gcd({A}, {B}) = {a}")
    return a



def extended_gcd_steps(a, b):
    A, B = a, b
    print(f"{A}x + {B}y = gcd({A}, {B})")

    # Euclidean Algorithm
    steps = []
    print("By Euclidean Algorithm")
    while b:
        q = a // b
        r = a % b
        steps.append((a, b, q, r))
        print(f"{a} = {q}*{b} + {r}")
        a, b = b, r
    g = a
    print(f"gcd({A}, {B}) = {g}\n")

    # Back substitution
    print("Output Example")
    # ใช้ dictionary เก็บการแสดงออกของ remainder
    expr = {steps[-1][3]: str(steps[-1][3])}  # gcd เริ่มจาก r สุดท้าย (72 ในตัวอย่าง)

    # ไล่ย้อนจาก steps ท้ายไปต้น
    for a, b, q, r in reversed(steps):
        if r == 0:
            continue
        # r = a - q*b
        expr[r] = f"{a} - {q}*{b}"
        # ถ้ามี expr ของ a หรือ b แทนค่าเข้าไป
        if a in expr:
            expr[r] = expr[r].replace(str(a), f"({expr[a]})")
        if b in expr:
            expr[r] = expr[r].replace(str(b), f"({expr[b]})")
        print(f"{r} = {expr[r]}")

    # หาค่า x, y จริง
    def egcd(a, b):
        if b == 0:
            return a, 1, 0
        g, x1, y1 = egcd(b, a % b)
        x, y = y1, x1 - (a // b) * y1
        return g, x, y

    g, x, y = egcd(A, B)
    print(f"Therefore we see that x = {x} and y = {y} is a solution to equation")
    return g, x, y


def sieve_steps(n):
    numbers = np.arange(1, n+1)
    is_prime = np.ones(n+1, dtype=bool)
    is_prime[0:2] = False  # 0,1 ไม่ใช่ prime

    rows = int(math.ceil(math.sqrt(n)))
    cols = int(math.ceil(n / rows))
    padded = np.pad(numbers, (0, rows*cols - n), constant_values=0).reshape(rows, cols)

    # วาดฟังก์ชันช่วย
    def plot(mask, title):
        plt.imshow(mask, cmap='Wistia', vmin=0, vmax=1)
        for i in range(rows):
            for j in range(cols):
                num = padded[i, j]
                if num != 0:
                    plt.text(j, i, str(num), ha='center', va='center',
                             color='black' if mask[i, j] else 'gray')
        plt.xticks([]); plt.yticks([])
        plt.title(title)
        plt.show()

    # Step 1: เริ่มแสดงเลขทั้งหมด
    mask = np.ones_like(padded, dtype=bool)
    plot(mask, f"Step 1: Numbers from 1..{n}")

    # Step 2+ : ลบตัวประกอบทีละ prime
    for p in range(2, int(math.sqrt(n)) + 1):
        if is_prime[p]:
            is_prime[p*2::p] = False
            mask = np.zeros_like(padded, dtype=bool)
            mask[padded <= n] = is_prime[padded[padded <= n]]
            plot(mask, f"Step: Eliminate multiples of {p}")

    # Step สุดท้าย
    plot(mask, "Step: Remaining are prime")
