"""九九乘法表共享逻辑：中文数字、口诀、题目集合。

口诀口径（与小学数学教材一致）：
- 按「小数在前、大数在后」排列，例如 4×3 写作「三四十二」。
- 积小于 10 用「得」连接：一一得一、二三得六。
- 积等于 10 的只有 2×5，固定读作「二五一十」（不是「二五得十」）。
- 积大于 10 直接连读：三四十二、四五二十、九九八十一。
"""

from __future__ import annotations

import random
from typing import Iterable, List, Tuple

CN_DIGITS = "零一二三四五六七八九"


def cn_number(n: int) -> str:
    """把 1-99 转成中文读法（10 读作「十」，20 读作「二十」）。"""
    if not 1 <= n <= 99:
        raise ValueError(f"只支持 1-99，收到 {n}")
    if n < 10:
        return CN_DIGITS[n]
    if n < 20:
        return "十" + (CN_DIGITS[n % 10] if n % 10 else "")
    tens, ones = divmod(n, 10)
    return CN_DIGITS[tens] + "十" + (CN_DIGITS[ones] if ones else "")


def koujue(a: int, b: int) -> str:
    """返回 a×b 的标准中文口诀。"""
    lo, hi = min(a, b), max(a, b)
    p = lo * hi
    head = CN_DIGITS[lo] + CN_DIGITS[hi]
    if p < 10:
        return head + "得" + CN_DIGITS[p]
    if p == 10:
        return head + "一十"
    return head + cn_number(p)


def formula(a: int, b: int) -> str:
    return f"{a}×{b}={a * b}"


def pairs_dajiu(max_factor: int = 9) -> List[Tuple[int, int]]:
    """大九九：完整 81 条，含两个交换顺序。"""
    return [(a, b) for a in range(1, max_factor + 1) for b in range(1, max_factor + 1)]


def pairs_xiaojiu(max_factor: int = 9) -> List[Tuple[int, int]]:
    """小九九：三角表 45 条，只保留 a≤b。"""
    return [(a, b) for a in range(1, max_factor + 1) for b in range(a, max_factor + 1)]


def grid_cell(a: int, b: int, content: str = "both") -> Tuple[str, str]:
    """返回单元格的两行文本 (口诀, 算式)，按 content 取舍。"""
    kj = koujue(a, b)
    f = formula(a, b)
    if content == "koujue":
        return kj, ""
    if content == "shizi":
        return f, ""
    return kj, f


def make_questions(
    count: int,
    mode: str = "dajiu",
    max_factor: int = 9,
    seed: int | None = None,
    allow_repeat: bool = False,
) -> List[Tuple[int, int]]:
    """生成口算练习题对。seed 固定时结果可复现。"""
    pool = pairs_dajiu(max_factor) if mode == "dajiu" else pairs_xiaojiu(max_factor)
    rng = random.Random(seed)
    if allow_repeat or count > len(pool):
        return [rng.choice(pool) for _ in range(count)]
    return rng.sample(pool, count)


def koujue_blank_answer(a: int, b: int) -> str:
    """口诀填空的答案部分（口诀去掉前两个字后剩下的内容）。"""
    kj = koujue(a, b)
    rest = kj[2:]
    return rest  # 例如「得六」「十二」「二十一」


def render_question_text(a: int, b: int, style: str = "calc") -> str:
    if style == "koujue":
        return koujue(a, b)[:2]
    return f"{a} × {b} ="


def iter_rows(pairs: Iterable[Tuple[int, int]], per_row: int) -> List[List[Tuple[int, int]]]:
    rows, buf = [], []
    for p in pairs:
        buf.append(p)
        if len(buf) == per_row:
            rows.append(buf)
            buf = []
    if buf:
        rows.append(buf)
    return rows
