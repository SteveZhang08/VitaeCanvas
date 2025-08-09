# === VitaeCanvas ===
# ./vitae_system/vitae_math.py
# by SteveZhang08
# Helpers: None

import math

def sigmoid(x, k=1, x0=0):
    """标准Sigmoid函数
    :param x: 输入值
    :param k: 曲线陡峭度（默认1）
    :param x0: 中心点偏移（默认0）
    :return: 输出值
    """
    return 1 / (1 + math.exp(-k * (x - x0)))

def inverted_sigmoid(x, k=1, x0=0):
    """Sigmoid函数的翻转
    :param x: 输入值
    :param k: 曲线陡峭度（默认1）
    :param x0: 中心点偏移（默认0）
    :return: 输出值
    """
    return 1 / (1 + math.exp(k * (x - x0)))  # 指数项符号反向

def vac_curve(x, k=0.01, x0=200):
    # by SteveZhang08
    """生命适应曲线（Vitae Adaption Curve）
    :param x: 输入值
    :param k: 曲线陡峭度（默认0.01）
    :param x0: 中心点偏移（默认200）
    :return: 输出值
    """
    return 3 - 6/(2 + math.exp(-(k * (x - x0))**2))


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    x = [i for i in range(0, 401)]
    y = [vac_curve(i) for i in x]

    plt.plot(x, y, label='Vitae Adaption Curve')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Vitae Adaption Curve')
    plt.grid(True)
    plt.xlim(0, 400)
    plt.ylim(-0.1, 1.1)
    plt.axhline(1, color='r', linestyle='--', label='y=1')
    plt.axvline(200, color='g', linestyle='--', label='x=200')

    plt.show()
