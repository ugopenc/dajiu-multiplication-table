"""生成九九乘法表：A4 打印版 PNG / 可打印 HTML / Excel 表格。

用法示例：
    python make_table.py --mode dajiu --format png html --outdir ./out
    python make_table.py --mode xiaojiu --content koujue --format png
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

import mulcore

A4_300 = (2480, 3508)

FONT_KJ_CANDIDATES = [r"C:\Windows\Fonts\simkai.ttf", r"C:\Windows\Fonts\simhei.ttf"]
FONT_UI_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
FONT_UI_BOLD_CANDIDATES = [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"]

INK = "#1F2937"
MUTED = "#64748B"
BORDER = "#CBD5E1"
HEADER_BG = "#EEF2F7"


def _first_existing(paths: List[str]) -> str:
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("未找到可用中文字体：" + "、".join(paths))


KJ_FONT = _first_existing(FONT_KJ_CANDIDATES)
UI_FONT = _first_existing(FONT_UI_CANDIDATES)
UI_BOLD = _first_existing(FONT_UI_BOLD_CANDIDATES)


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(path, size, index=0)


def _text_w(draw, text, font) -> float:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _fit(draw, text: str, path: str, size_max: int, max_w: float, size_min: int = 12):
    size = size_max
    while size > size_min:
        f = _font(path, size)
        if _text_w(draw, text, f) <= max_w:
            return f
        size -= 2
    return _font(path, size_min)


def _center(draw, box, text, font, fill):
    x0, y0, x1, y1 = box
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (x0 + (x1 - x0 - w) / 2 - bbox[0], y0 + (y1 - y0 - h) / 2 - bbox[1]),
        text,
        font=font,
        fill=fill,
    )


def _cells(mode: str, max_factor: int) -> List[List[Tuple[int, int]]]:
    if mode == "xiajiu":
        return [[(a, b) for b in range(1, a + 1)] for a in range(1, max_factor + 1)]
    return [[(a, b) for b in range(1, max_factor + 1)] for a in range(1, max_factor + 1)]


def render_png(
    out_path: Path,
    mode: str = "dajiu",
    content: str = "both",
    headers: bool = True,
    title: str | None = None,
    max_factor: int = 9,
) -> Path:
    img = Image.new("RGB", A4_300, "white")
    draw = ImageDraw.Draw(img)
    page_w = A4_300[0]
    x0, grid_w = 150, page_w - 300

    mode_cn = "大九九" if mode == "dajiu" else "小九九"
    total = max_factor * max_factor if mode == "dajiu" else max_factor * (max_factor + 1) // 2
    title_text = title or f"{mode_cn}乘法表"
    _center(draw, (0, 110, page_w, 250), title_text, _font(UI_BOLD, 96), INK)
    _center(
        draw,
        (0, 260, page_w, 330),
        f"共 {total} 句　·　{1}×{1} 到 {max_factor}×{max_factor}　·　小数在前，大数在后",
        _font(UI_FONT, 36),
        MUTED,
    )

    rows = _cells(mode, max_factor)
    ncols = max_factor
    with_headers = mode == "dajiu" and headers
    spans = ncols + (1 if with_headers else 0)
    cw = grid_w // spans
    band = cw
    grid_left = x0 + (cw if with_headers else 0)
    header_h = band if with_headers else 0
    grid_h = len(rows) * band
    area_top, area_bottom = 380, A4_300[1] - 200
    extra = max(0, (area_bottom - area_top) - (grid_h + header_h))
    top = area_top + header_h + extra // 4

    for r_idx, row in enumerate(rows):
        for c_idx, (a, b) in enumerate(row):
            cx0 = grid_left + c_idx * cw
            cy0 = top + r_idx * band
            cx1, cy1 = cx0 + cw, cy0 + band
            draw.rectangle([cx0, cy0, cx1, cy1], outline=BORDER, width=3)
            kj, fz = mulcore.grid_cell(a, b, content)
            if fz:
                _center(
                    draw,
                    (cx0, cy0 + band * 0.10, cx1, cy0 + band * 0.62),
                    kj,
                    _fit(draw, kj, KJ_FONT, 58, cw - 16),
                    INK,
                )
                _center(
                    draw,
                    (cx0, cy0 + band * 0.60, cx1, cy0 + band * 0.94),
                    fz,
                    _fit(draw, fz, UI_FONT, 32, cw - 16),
                    MUTED,
                )
            else:
                _center(
                    draw,
                    (cx0, cy0, cx1, cy1),
                    kj,
                    _fit(draw, kj, KJ_FONT, 62, cw - 16),
                    INK,
                )

    if with_headers:
        # 表头行列
        hy0, hy1 = top - band, top
        for c_idx in range(ncols):
            cx0 = grid_left + c_idx * cw
            draw.rectangle([cx0, hy0, cx0 + cw, hy1], fill=HEADER_BG, outline=BORDER, width=3)
            _center(draw, (cx0, hy0, cx0 + cw, hy1), str(c_idx + 1), _font(UI_BOLD, 56), INK)
        for r_idx in range(max_factor):
            cy0 = top + r_idx * band
            draw.rectangle([x0, cy0, x0 + cw, cy0 + band], fill=HEADER_BG, outline=BORDER, width=3)
            _center(draw, (x0, cy0, x0 + cw, cy0 + band), str(r_idx + 1), _font(UI_BOLD, 56), INK)
        # 左上角装饰
        draw.rectangle([x0, hy0, x0 + cw, hy1], fill="#E2E8F0", outline=BORDER, width=3)
        _center(draw, (x0, hy0, x0 + cw, hy1), "×", _font(UI_BOLD, 50), MUTED)

    foot_y = top + grid_h + 70
    _center(
        draw,
        (0, foot_y, page_w, foot_y + 60),
        "横读为被乘数，竖读为乘数；两向交叉即为口诀",
        _font(UI_FONT, 34),
        MUTED,
    )

    img.save(out_path, "PNG", dpi=(300, 300))
    return out_path


def render_html(
    out_path: Path,
    mode: str = "dajiu",
    content: str = "both",
    headers: bool = True,
    title: str | None = None,
    max_factor: int = 9,
) -> Path:
    mode_cn = "大九九" if mode == "dajiu" else "小九九"
    total = max_factor * max_factor if mode == "dajiu" else max_factor * (max_factor + 1) // 2
    title_text = title or f"{mode_cn}乘法表"

    html = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        f"<title>{title_text}</title>",
        "<style>",
        "@page { size: A4 portrait; margin: 12mm; }",
        "* { box-sizing: border-box; }",
        "body { margin: 0; font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; color: #1F2937; }",
        ".sheet { width: 186mm; margin: 0 auto; }",
        "h1 { text-align: center; font-size: 30pt; margin: 6mm 0 2mm; letter-spacing: 2px; }",
        ".sub { text-align: center; color: #64748B; font-size: 10.5pt; margin-bottom: 5mm; }",
        "table { border-collapse: collapse; width: 100%; table-layout: fixed; }",
        "td { border: 1.2px solid #CBD5E1; text-align: center; height: 15.5mm; vertical-align: middle; }",
        ".kj { font-family: 'KaiTi', 'STKaiti', 'KaiTi_GB2312', serif; font-size: 15.5pt; }",
        ".fz { font-size: 9pt; color: #64748B; margin-top: 1mm; }",
        "th { background: #EEF2F7; font-size: 13pt; border: 1.2px solid #CBD5E1; height: 15.5mm; }",
        ".note { text-align: center; color: #64748B; font-size: 9.5pt; margin-top: 4mm; }",
        "@media print { .tip { display: none; } }",
        "</style></head><body><div class='sheet'>",
        f"<h1>{title_text}</h1>",
        f"<div class='sub'>共 {total} 句　·　1×1 到 {max_factor}×{max_factor}　·　小数在前，大数在后</div>",
    ]

    ncols = max_factor
    html.append("<table>")
    if mode == "dajiu" and headers:
        html.append("<tr><th style='width:11.1%'>×</th>" + "".join(f"<th>{i}</th>" for i in range(1, ncols + 1)) + "</tr>")

    for r_idx, row in enumerate(_cells(mode, max_factor)):
        html.append("<tr>")
        if mode == "dajiu" and headers:
            html.append(f"<th>{r_idx + 1}</th>")
        for (a, b) in row:
            kj, fz = mulcore.grid_cell(a, b, content)
            inner = f"<div class='kj'>{kj}</div>"
            if fz:
                inner += f"<div class='fz'>{fz}</div>"
            html.append(f"<td>{inner}</td>")
        for _ in range(ncols - len(row)):
            html.append("<td style='border:none'></td>")
        html.append("</tr>")
    html.append("</table>")
    html.append("<div class='note'>横读为被乘数，竖读为乘数；两向交叉即为口诀</div>")
    html.append("<div class='note tip' style='margin-top:6mm'>浏览器打印：Ctrl/Cmd + P，纸张 A4，缩放 100%，关闭页眉页脚。</div>")
    html.append("</div></body></html>")
    out_path.write_text("\n".join(html), encoding="utf-8")
    return out_path


def render_xlsx(
    out_path: Path,
    mode: str = "dajiu",
    max_factor: int = 9,
    title: str | None = None,
) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    thin = Side(style="thin", color="CBD5E1")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center")
    fill = PatternFill("solid", fgColor="EEF2F7")

    wb = Workbook()
    ws = wb.active
    ws.title = "口诀表" if mode == "dajiu" else "小九九口诀"

    offset = 2  # 标题占两行
    ws.cell(row=1, column=1, value=title or ("大九九乘法表" if mode == "dajiu" else "小九九乘法表")).font = Font(
        size=16, bold=True
    )

    for c in range(1, max_factor + 2):
        cell = ws.cell(row=offset, column=c, value="×" if c == 1 else c - 1)
        cell.font = Font(bold=True)
        cell.alignment = center
        cell.border = border
        cell.fill = fill

    for a in range(1, max_factor + 1):
        r = offset + a
        head = ws.cell(row=r, column=1, value=a)
        head.font = Font(bold=True)
        head.alignment = center
        head.border = border
        head.fill = fill
        for b in range(1, max_factor + 1):
            cell = ws.cell(row=r, column=b + 1, value=mulcore.koujue(a, b))
            cell.alignment = center
            cell.border = border

    for c in range(2, max_factor + 2):
        ws.column_dimensions[ws.cell(row=offset, column=c).column_letter].width = 12
    ws.column_dimensions["A"].width = 6

    ws2 = wb.create_sheet("算式表")
    ws2.cell(row=1, column=1, value="算式表").font = Font(size=14, bold=True)
    for a in range(1, max_factor + 1):
        for b in range(1, max_factor + 1):
            cell = ws2.cell(row=a + 2, column=b, value=mulcore.formula(a, b))
            cell.alignment = center
            cell.border = border
    for b in range(1, max_factor + 1):
        ws2.column_dimensions[ws2.cell(row=3, column=b).column_letter].width = 11

    wb.save(out_path)
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="生成九九乘法表（大九九 81 句 / 小九九 45 句）")
    ap.add_argument("--mode", choices=["dajiu", "xiaojiu"], default="dajiu")
    ap.add_argument("--content", choices=["koujue", "shizi", "both"], default="both")
    ap.add_argument("--format", nargs="+", choices=["png", "html", "xlsx"], default=["png"])
    ap.add_argument("--no-headers", action="store_true", help="不显示乘数表头")
    ap.add_argument("--title", default=None)
    ap.add_argument("--max-factor", type=int, default=9, choices=range(2, 10))
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    base = ("大九九" if args.mode == "dajiu" else "小九九") + "乘法表"
    headers = not args.no_headers

    produced = []
    if "png" in args.format:
        p = outdir / f"{base}.png"
        render_png(p, args.mode, args.content, headers, args.title, args.max_factor)
        produced.append(p)
    if "html" in args.format:
        p = outdir / f"{base}.html"
        render_html(p, args.mode, args.content, headers, args.title, args.max_factor)
        produced.append(p)
    if "xlsx" in args.format:
        p = outdir / f"{base}.xlsx"
        render_xlsx(p, args.mode, args.max_factor, args.title)
        produced.append(p)

    for p in produced:
        print(p)


if __name__ == "__main__":
    main()
