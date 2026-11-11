"""生成九九乘法表口算练习题（题面 + 答案页），支持 PNG / HTML。

用法示例：
    python make_worksheet.py --count 24 --outdir ./out
    python make_worksheet.py --count 20 --style koujue --seed 2026 --format html
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import mulcore
from make_table import A4_300, INK, MUTED, UI_FONT, UI_BOLD, _center, _fit, _font, _text_w

BORDER = "#CBD5E1"


def _header_block(draw, page_w: int, title: str, subtitle: str) -> int:
    _center(draw, (0, 100, page_w, 230), title, _font(UI_BOLD, 88), INK)
    _center(draw, (0, 240, page_w, 310), subtitle, _font(UI_FONT, 34), MUTED)
    # 姓名 / 日期 / 用时 / 得分 横线
    y = 370
    items = [("姓名", 0.06, 0.30), ("日期", 0.34, 0.56), ("用时", 0.60, 0.76), ("得分", 0.80, 0.94)]
    for label, s, e in items:
        x0, x1 = int(page_w * s), int(page_w * e)
        draw.text((x0, y), label, font=_font(UI_FONT, 32), fill=MUTED)
        lx0 = x0 + _text_w(draw, label, _font(UI_FONT, 32)) + 12
        draw.line([lx0, y + 44, x1, y + 44], fill=BORDER, width=3)
    return y + 130


def _question_png(out_path: Path, pairs, style: str, columns: int, title: str, subtitle: str) -> Path:
    img = Image.new("RGB", A4_300, "white")
    draw = ImageDraw.Draw(img)
    page_w, page_h = A4_300
    y0 = _header_block(draw, page_w, title, subtitle)

    x0 = 150
    grid_w = page_w - 300
    cw = grid_w // columns
    avail_h = page_h - y0 - 220
    rows_needed = max(1, -(-len(pairs) // columns))
    row_h = min(460, max(250, avail_h // rows_needed))
    max_rows = avail_h // 250
    if len(pairs) > columns * max_rows:
        raise ValueError(f"题目过多：单页最多 {columns * max_rows} 题，当前 {len(pairs)} 题，请减少 --count")
    start_y = y0 + 20

    for idx, (a, b) in enumerate(pairs):
        r, c = divmod(idx, columns)
        cx0 = x0 + c * cw
        cy0 = start_y + r * row_h
        text = mulcore.render_question_text(a, b, style)
        f = _fit(draw, text, UI_FONT, 56, cw * 0.62, 28)
        bbox = draw.textbbox((0, 0), text, font=f)
        draw.text((cx0 + 10, cy0 + row_h / 2 - (bbox[3] - bbox[1]) / 2 - bbox[1]), text, font=f, fill=INK)
        # 下划线作答区
        line_x0 = cx0 + 10 + (bbox[2] - bbox[0]) + 24
        draw.line([line_x0, cy0 + row_h / 2 + 26, cx0 + cw - 10, cy0 + row_h / 2 + 26], fill=BORDER, width=3)

    draw.line([x0, page_h - 120, page_w - 150, page_h - 120], fill="#E2E8F0", width=2)
    _center(draw, (0, page_h - 100, page_w, page_h - 40), "认真审题，先想口诀再写得数", _font(UI_FONT, 30), MUTED)
    img.save(out_path, "PNG", dpi=(300, 300))
    return out_path


def _answer_png(out_path: Path, pairs, style: str, columns: int, title: str, subtitle: str) -> Path:
    img = Image.new("RGB", A4_300, "white")
    draw = ImageDraw.Draw(img)
    page_w, page_h = A4_300
    _center(draw, (0, 120, page_w, 240), title, _font(UI_BOLD, 80), INK)
    _center(draw, (0, 250, page_w, 310), subtitle, _font(UI_FONT, 32), MUTED)
    y0 = 400

    x0 = 150
    grid_w = page_w - 300
    cw = grid_w // columns
    row_h = 200
    max_rows = (page_h - y0 - 150) // row_h
    if len(pairs) > columns * max_rows:
        raise ValueError(f"答案过多：单页最多 {columns * max_rows} 条，当前 {len(pairs)} 条")

    for idx, (a, b) in enumerate(pairs):
        r, c = divmod(idx, columns)
        cx0 = x0 + c * cw
        cy0 = y0 + r * row_h
        cy1 = cy0 + row_h
        draw.rectangle([cx0, cy0, cx0 + cw, cy1], outline=BORDER, width=2)
        no = str(idx + 1)
        draw.text((cx0 + 12, cy0 + 10), no, font=_font(UI_FONT, 24), fill=MUTED)
        if style == "koujue":
            head = mulcore.koujue(a, b)[:2]
            body = mulcore.koujue(a, b)[2:]
            label = f"{head}{body}"
        else:
            label = f"{a} × {b} = {a * b}"
        _center(draw, (cx0, cy0 + 40, cx0 + cw, cy1), label, _fit(draw, label, UI_FONT, 44, cw - 16, 20), INK)
    img.save(out_path, "PNG", dpi=(300, 300))
    return out_path


def _questions_html(pairs, style: str, title: str, subtitle: str, answers) -> str:
    cells = []
    for idx, (a, b) in enumerate(pairs):
        text = mulcore.render_question_text(a, b, style)
        cells.append(f"<li><span class='q'>{text}</span><span class='line'></span></li>")
    return "".join(cells)


def render_html(out_path: Path, pairs, style: str, columns: int, title: str, subtitle: str, with_answer: bool) -> Path:
    qs = _questions_html(pairs, style, title, subtitle, with_answer)
    ans_items = []
    for idx, (a, b) in enumerate(pairs):
        if style == "koujue":
            ans_items.append(f"<li>{idx + 1}. {mulcore.koujue(a, b)}</li>")
        else:
            ans_items.append(f"<li>{idx + 1}. {a} × {b} = {a * b}</li>")
    answers = "".join(ans_items) if with_answer else ""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>{title}</title>
<style>
@page {{ size: A4 portrait; margin: 14mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: 'Microsoft YaHei','PingFang SC',sans-serif; color: {INK}; }}
.sheet {{ width: 182mm; margin: 0 auto; }}
h1 {{ text-align: center; font-size: 26pt; margin: 4mm 0 2mm; letter-spacing: 2px; }}
.sub {{ text-align: center; color: {MUTED}; font-size: 10.5pt; margin-bottom: 4mm; }}
.meta {{ display: flex; gap: 14mm; color: {MUTED}; font-size: 11pt; margin: 4mm 0 7mm; }}
.meta span {{ flex: 1; border-bottom: 1px solid {BORDER}; padding-bottom: 1mm; }}
ul.qs {{ list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat({columns}, 1fr); gap: 7mm 6mm; }}
ul.qs li {{ display: flex; align-items: baseline; font-size: 15pt; }}
ul.qs .q {{ white-space: nowrap; }}
ul.qs .line {{ flex: 1; border-bottom: 1px solid {BORDER}; margin-left: 2mm; height: 6mm; }}
.note {{ text-align: center; color: {MUTED}; font-size: 9.5pt; margin-top: 8mm; }}
.page-break {{ page-break-before: always; }}
h2 {{ font-size: 15pt; margin: 4mm 0 3mm; }}
ul.ans {{ list-style: none; padding: 0; margin: 0; columns: 4; font-size: 12pt; line-height: 2.0; }}
</style></head><body>
<div class="sheet">
  <h1>{title}</h1>
  <div class="sub">{subtitle}</div>
  <div class="meta"><span>姓名</span><span>日期</span><span>用时</span><span>得分</span></div>
  <ul class="qs">{qs}</ul>
  <div class="note">认真审题，先想口诀再写得数</div>
</div>
"""
    if with_answer:
        html += f"""
<div class="sheet page-break">
  <h2>参考答案</h2>
  <ul class="ans">{answers}</ul>
</div>
"""
    html += "</body></html>"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="生成九九乘法表口算练习")
    ap.add_argument("--count", type=int, default=24)
    ap.add_argument("--mode", choices=["dajiu", "xiaojiu"], default="dajiu")
    ap.add_argument("--style", choices=["calc", "koujue"], default="calc", help="calc=算式填空，koujue=口诀补全")
    ap.add_argument("--max-factor", type=int, default=9)
    ap.add_argument("--columns", type=int, default=4)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--format", nargs="+", choices=["png", "html"], default=["png"])
    ap.add_argument("--title", default="九九乘法表 口算练习")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    pool_mode = "xiaojiu" if args.style == "koujue" else args.mode
    pairs = mulcore.make_questions(args.count, pool_mode, args.max_factor, args.seed)
    subtitle = f"共 {args.count} 题　·　{'口诀补全' if args.style == 'koujue' else '算式计算'}"
    stem = "口算练习" if args.style == "calc" else "口诀填空练习"

    produced = []
    if "png" in args.format:
        produced.append(_question_png(outdir / f"{stem}_题面.png", pairs, args.style, args.columns, args.title, subtitle))
        produced.append(_answer_png(outdir / f"{stem}_答案.png", pairs, args.style, args.columns, "口算练习 参考答案", subtitle))
    if "html" in args.format:
        produced.append(render_html(outdir / f"{stem}.html", pairs, args.style, args.columns, args.title, subtitle, True))

    for p in produced:
        print(p)


if __name__ == "__main__":
    main()
