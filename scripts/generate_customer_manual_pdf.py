from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "Word_Report_QA_Assistant_客户说明书.pdf"
FONT_REGULAR = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\simhei.ttf")


def register_fonts() -> tuple[str, str]:
    regular = "NotoSansSC"
    bold = "SimHei"
    pdfmetrics.registerFont(TTFont(regular, str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont(bold, str(FONT_BOLD)))
    return regular, bold


def build_pdf() -> Path:
    regular, bold = register_fonts()
    styles = build_styles(regular, bold)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=16 * mm,
        title="Word Report QA Assistant 客户说明书",
        author="Word Report QA Assistant",
    )

    story = []
    story += cover(styles)
    story += section_product_intro(styles)
    story += section_usage(styles)
    story += section_features(styles)
    story += section_rules(styles)
    story += section_limitations(styles)
    story += section_recommendations(styles)
    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    return OUTPUT


def build_styles(regular: str, bold: str):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ManualTitle",
            parent=styles["Title"],
            fontName=bold,
            fontSize=25,
            leading=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ManualSubtitle",
            parent=styles["Normal"],
            fontName=regular,
            fontSize=11,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ManualH1",
            parent=styles["Heading1"],
            fontName=bold,
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#1F2937"),
            spaceBefore=14,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ManualH2",
            parent=styles["Heading2"],
            fontName=bold,
            fontSize=12,
            leading=18,
            textColor=colors.HexColor("#2563EB"),
            spaceBefore=10,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ManualBody",
            parent=styles["BodyText"],
            fontName=regular,
            fontSize=9.7,
            leading=16,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#374151"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ManualBullet",
            parent=styles["BodyText"],
            fontName=regular,
            fontSize=9.4,
            leading=15,
            leftIndent=8,
            textColor=colors.HexColor("#374151"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName=regular,
            fontSize=8.8,
            leading=13,
            textColor=colors.HexColor("#6B7280"),
        )
    )
    return styles


def cover(styles):
    story = [
        Spacer(1, 40 * mm),
        Paragraph("Word Report QA Assistant", styles["ManualTitle"]),
        Paragraph("客户说明书 | MVP v1.0 | 2026-06-02", styles["ManualSubtitle"]),
        Spacer(1, 10 * mm),
        note_box(
            "本系统用于自动发现 IND/医学报告 Word 文件中的细节错误，包括文字、数字、表格、引用、编号、术语、缩写、页眉页脚版本、残留批注和修订痕迹等问题。"
        ),
        Spacer(1, 8 * mm),
        note_box("本系统不做药政法规合规判断，不判断 IND 是否满足 FDA、NMPA、EMA 或其他监管机构要求。"),
        PageBreak(),
    ]
    return story


def section_product_intro(styles):
    return [
        h1("1. 产品简介", styles),
        p(
            "Word Report QA Assistant 是一个面向医学写作、临床、注册、CMC、非临床报告团队的 Word 文档质量检查工具。用户上传一个或多个 .docx 文件后，系统解析文档结构，运行确定性 QA 检查规则，生成问题清单，并支持导出 Excel QA log。",
            styles,
        ),
        h2("适用对象", styles),
        bullets(
            [
                "文档作者：在交付前自查 Word 报告。",
                "QA Reviewer：查看问题、确认问题、标记误报、补充 reviewer comment。",
                "项目管理员：管理项目、上传多份 Word 文件、查看整体 QA 状态。",
            ],
            styles,
        ),
    ]


def section_usage(styles):
    return [
        h1("2. 基本使用流程", styles),
        bullets(
            [
                "创建项目，例如 ABC-123 IND Word QA。",
                "进入项目详情页，上传 .docx Word 文件。",
                "点击 Parse 解析 Word 文档结构。",
                "点击 Run QA 运行规则检查。",
                "进入 View issues 查看 QA issue list。",
                "按 Severity、Category、Document、Status 筛选问题。",
                "打开 issue 详情，查看 source text、description、suggestion 和 location。",
                "修改 issue 状态，填写 reviewer comment。",
                "点击 Export Excel 导出 QA log。",
            ],
            styles,
        ),
    ]


def section_features(styles):
    rows = [
        ["功能", "说明"],
        ["项目管理", "创建项目，在项目下管理多份 Word 文档，查看文档数量和 issue 统计。"],
        ["文档上传", "支持 .docx，不支持 .doc；MVP 单文件大小限制为 50MB。"],
        ["Word 解析", "解析正文段落、标题、表格、页眉页脚、comments、tracked changes、隐藏文字和 metadata。"],
        ["QA 检查", "运行确定性规则，生成结构化 issue；单条规则失败不会中断整体 QA。"],
        ["Issue Dashboard", "查看、筛选、打开详情、修改状态、填写 reviewer comment。"],
        ["Excel 导出", "导出当前筛选结果，供人工 review 和项目归档。"],
    ]
    return [
        h1("3. 主要功能说明", styles),
        make_table(rows, [36 * mm, 120 * mm]),
    ]


def section_rules(styles):
    rows = [
        ["类别", "当前支持的检查"],
        ["Text", "重复英文单词；多余连续空格。"],
        ["Numeric", "n/N 百分比计算错误，例如 3/20 (20.0%)。"],
        ["Table", "简单表格合计错误；空表格单元格；N/A 写法不统一。"],
        ["Reference", "Table/Figure 引用不存在。"],
        ["Heading", "标题编号跳号。"],
        ["Word Metadata", "页眉页脚版本号不一致；残留批注；残留修订痕迹。"],
        ["Abbreviation", "缩写首次出现未定义；同一缩写多重定义。"],
        ["Terminology", "简单术语写法不一致，例如 ABC-123 / ABC123 / ABC 123。"],
    ]
    return [
        h1("4. QA 检查范围", styles),
        make_table(rows, [36 * mm, 120 * mm]),
        h2("Severity 说明", styles),
        bullets(
            [
                "High：明显影响报告准确性或提交质量的问题，例如百分比计算错误、表格合计错误、版本不一致、残留批注、残留修订痕迹。",
                "Medium：影响一致性、专业性或可读性的问题，例如引用不存在、标题编号跳号、缩写问题、术语写法不一致。",
                "Low：文字、格式和风格类问题，例如重复单词、多余空格、N/A 写法不统一。",
                "Critical：MVP 默认不主动使用，除非未来扩展到极高风险文档问题。",
            ],
            styles,
        ),
    ]


def section_limitations(styles):
    limitations = [
        "不支持 PDF 文件检查。",
        "不支持扫描件和 OCR。",
        "不支持 .doc 老格式文件。",
        "不做 FDA、NMPA、EMA 或其他药政法规合规判断。",
        "不判断 IND 是否满足申报要求。",
        "不判断医学结论、临床结论、统计分析结论是否正确。",
        "不自动修改 Word 原文。",
        "不生成最终申报文件。",
        "不支持 eCTD。",
        "不支持电子签名。",
        "不支持复杂多用户权限系统、SSO 和复杂审计追踪。",
        "不提供云部署能力，MVP 以本地运行和本地文件存储为主。",
        "不保证识别所有复杂表格错误，当前表格合计检查主要面向简单数字表格。",
        "不保证识别所有语义矛盾，当前以确定性规则为主。",
        "不替代人工 QA review。",
    ]
    return [h1("5. 系统做不到哪些事", styles), p("本系统是 Word 文档质量 QA 工具，不是法规、医学或统计判断系统。", styles), bullets(limitations, styles)]


def section_recommendations(styles):
    return [
        h1("6. 推荐使用方式", styles),
        bullets(
            [
                "在 Word 文档交付给 QA reviewer 前先运行一次系统检查。",
                "对 High issue 优先人工确认。",
                "对 Medium issue 重点关注一致性和引用问题。",
                "对 Low issue 可作为文档清理和格式统一参考。",
                "导出 Excel QA log 后，建议由人工 reviewer 填写最终处理意见。",
            ],
            styles,
        ),
        h1("7. 一句话总结", styles),
        p(
            "Word Report QA Assistant 用于帮助团队更快发现 Word 报告中的文字、数字、表格、引用、编号、缩写、术语和 Word metadata 问题，但最终判断仍应由人工 reviewer 完成。",
            styles,
        ),
    ]


def h1(text, styles):
    return Paragraph(text, styles["ManualH1"])


def h2(text, styles):
    return Paragraph(text, styles["ManualH2"])


def p(text, styles):
    return Paragraph(text, styles["ManualBody"])


def bullets(items, styles):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["ManualBullet"]), leftIndent=10) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=14,
        bulletFontName=styles["ManualBody"].fontName,
        bulletFontSize=7,
    )


def make_table(rows, col_widths):
    table = Table(rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "NotoSansSC"),
                ("FONTNAME", (0, 0), (-1, 0), "SimHei"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.6),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def note_box(text: str):
    table = Table([[Paragraph(text, ParagraphStyle(name="Note", fontName="NotoSansSC", fontSize=10.5, leading=17, textColor=colors.HexColor("#1F2937")))]], colWidths=[155 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#93C5FD")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("NotoSansSC", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(18 * mm, 9 * mm, "Word Report QA Assistant 客户说明书")
    canvas.drawRightString(192 * mm, 9 * mm, f"第 {doc.page} 页")
    canvas.restoreState()


if __name__ == "__main__":
    output = build_pdf()
    print(output)
