---
name: dajiu-multiplication-table
description: 生成九九乘法表（大九九 81 句完整网格 / 小九九 45 句三角表）的 A4 打印版图片、可打印 HTML、Excel 表格，以及口算练习题与答案页，并保证中文口诀读法规范（小数在前、「得」字的用法、二五一十等特例）。当用户提出做九九乘法表、大九九、小九九、乘法口诀表、口诀卡片、打印张贴版、乘法表 Excel/Word/PDF、口算练习、口诀填空练习、给孩子打印的乘法表，或要求核对口诀读法对错时使用。
license: MIT
---

# 九九乘法表生成

## 一、先确定四件事

| 维度 | 取值 | 默认 |
|---|---|---|
| 范围 | 大九九（81 句，完整 9×9 网格）／小九九（45 句，三角表） | 大九九 |
| 内容 | 口诀／算式／两者 | 两者 |
| 格式 | PNG（A4 300dpi 打印图）／HTML（浏览器打印）／XLSX | PNG |
| 用途 | 张贴背诵／查表／口算练习 | 张贴背诵 |

用户没说是哪种，按默认做，交付时用一句话说明可切换。只有「提到乘法表但明显要做海报、插画、手抄报、贴纸」时才不属于本技能，改用 `doubao-creative-design`。

## 二、生成表格

在 `scripts/` 目录下执行，`--outdir` 指向用户主项目目录（或在其下新建的 `九九乘法表/` 子目录）。

```bash
python make_table.py --mode dajiu --format png --outdir "<输出目录>"
python make_table.py --mode xiaojiu --content koujue --format png html --outdir "<输出目录>"
python make_table.py --mode dajiu --format png html xlsx --outdir "<输出目录>"
```

参数：

- `--mode dajiu|xiaojiu`：`dajiu` 完整 81 句，`xiaojiu` 三角 45 句。
- `--content koujue|shizi|both`：只要口诀、只要算式、或两行都显示。
- `--format png html xlsx`：可多选，一次生成多份。
- `--no-headers`：去掉乘数表头（只要 9×9 净网格）。
- `--max-factor 2..9`：只做 1 到 N 的乘法表，启蒙阶段可做 1-5。
- `--title`：自定义标题，如「二年级（3）班 乘法口诀表」。

脚本把每个产出文件的绝对路径打到 stdout，按行读取，不要自己拼路径。

HTML 版是 A4 打印稿，交付时提示「浏览器 Ctrl/Cmd + P，A4、缩放 100%、关掉页眉页脚」。PNG 版按 A4 300dpi（2480×3508）出图，可直接送打印店。

## 三、生成练习题

```bash
python make_worksheet.py --count 24 --outdir "<输出目录>"
python make_worksheet.py --count 20 --style koujue --seed 2026 --format html --outdir "<输出目录>"
```

- `--count`：题量。4 列布局下 PNG 单页上限约 30 题，更多要拆页或调 `--columns`。
- `--style calc`：`3 × 7 = ____`；`--style koujue`：`三七（　　　　）`，练口诀补全。
- `--seed`：固定种子可复现同一套题，方便重印；要 A/B 卷用两个不同 seed。
- 默认同时产出题面与答案页，两张都要交付，不要只给题面。

## 四、交付

- PNG 走 `<RichMediaCard>`，用绝对路径；同组图片放一个标签，最多 6 张。
- HTML、XLSX 走 `present_files`。
- 交付时补一句：大九九 81 句、小九九 45 句，口诀按「小数在前」排列。

## 五、口诀校对（必做）

写口诀前先看 [references/koujue-rules.md](references/koujue-rules.md) 的规则与 45 句基准表。脚本已内置正确读法，人工抽查即可：

1. 大九九 81 格、小九九 45 格；
2. 对角线为「一一得一 … 九九八十一」；
3. 积小于 10 的格子必须带「得」，其余不带；
4. 2×5 必须是「二五一十」，不是「二五得十」；
5. 20 读「二十」、12 读「十二」、81 读「八十一」。

发现输出有错，改 `scripts/mulcore.py` 里的 `koujue()` 与 `cn_number()`，不要只在图上手改文字。

## 六、边界

- 只覆盖 1-9 整数乘法口诀。十以上、小数、除法口诀不在范围内，用户要这些内容时自行编排，不要套脚本。
- 需要 Word 正式排版或 PDF 精修，用 HTML 打印或转 `word`／`pdf` 技能；需要卡通插画、彩色海报、手抄报版式，转 `doubao-creative-design`。
- 练习题上的「姓名、日期、用时、得分」是空白手写栏，不预填、不采集任何学生信息。
