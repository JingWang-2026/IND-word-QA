# Word Report QA Assistant 客户说明书

版本：MVP v1.0  
日期：2026-06-02

## 1. 产品简介

Word Report QA Assistant 是一个面向医学写作、临床、注册、CMC、非临床报告团队的 Word 文档质量检查工具。

系统仅支持 `.docx` Word 文件。用户上传一个或多个 Word 文档后，系统会解析文档结构，运行确定性 QA 检查规则，生成问题清单，并支持导出 Excel QA log，供人工 review 和项目归档。

本系统不做药政法规合规判断，不判断 IND 是否满足 FDA、NMPA、EMA 或其他监管机构要求。它的目标是帮助团队更早发现 Word 报告中的细节错误和一致性问题。

## 2. 适用对象

- 文档作者：在交付前自查 Word 报告。
- QA Reviewer：查看系统生成的问题、确认问题、标记误报、补充 reviewer comment。
- 项目管理员：管理项目、上传多份 Word 文件、查看整体 QA 状态。

## 3. 基本使用流程

1. 打开系统前端页面。
2. 创建一个项目，例如 `ABC-123 IND Word QA`。
3. 进入项目详情页。
4. 上传 `.docx` Word 文件。
5. 点击 `Parse`，解析 Word 文档结构。
6. 点击 `Run QA`，运行规则检查。
7. 进入 `View issues` 查看 QA issue list。
8. 使用 Severity、Category、Document、Status 筛选问题。
9. 打开 issue 详情，查看 source text、description、suggestion 和 location。
10. 根据人工判断修改 issue 状态，并填写 reviewer comment。
11. 点击 `Export Excel` 导出 QA log。

## 4. 主要功能说明

### 4.1 项目管理

用户可以创建项目，并在项目下管理多份 Word 文档。

项目详情页会展示：

- 项目名称和描述
- 已上传文档数量
- QA issue 总数
- High issue 数量
- 文档列表和解析状态

### 4.2 Word 文档上传

系统支持上传 `.docx` 文件。

上传规则：

- 支持 `.docx`
- 不支持 `.doc`
- MVP 单文件大小限制为 50MB
- 上传后原始文件会保存在本地项目存储目录

上传后需要点击 `Parse` 解析文档，再运行 QA。

### 4.3 Word 文档解析

系统会解析 Word 文档中的结构化内容，包括：

- 正文段落
- 标题
- 表格
- 页眉
- 页脚
- Word comments
- tracked changes
- 隐藏文字
- 文档 metadata

如果文档解析失败，系统会把文档状态标记为 `failed`，并保存错误信息。

### 4.4 QA 规则检查

系统目前实现的是确定性规则检查。每条规则独立运行，单条规则失败不会中断整个 QA 流程。

当前支持的检查包括：

- 重复英文单词
- 多余连续空格
- n/N 百分比计算错误
- 简单表格合计错误
- 空表格单元格
- N/A 写法不统一
- Table/Figure 引用不存在
- 标题编号跳号
- 页眉页脚版本号不一致
- 残留 Word 批注
- 残留修订痕迹
- 缩写首次出现未定义
- 同一缩写多重定义
- 简单术语写法不一致

### 4.5 Issue Dashboard

QA 完成后，系统生成 issue list。

每条 issue 包含：

- Severity
- Category
- Rule ID
- Title
- Description
- Source Text
- Suggestion
- Location
- Status
- Reviewer Comment

支持按以下条件筛选：

- Severity
- Category
- Document
- Status

### 4.6 Issue 状态管理

Reviewer 可以把 issue 标记为：

- Open
- Confirmed
- False Positive
- Resolved

Reviewer 也可以填写 reviewer comment，用于记录人工判断和处理意见。

### 4.7 Excel QA Log 导出

系统支持导出当前筛选结果为 Excel 文件。

Excel 包含：

- Issue ID
- Severity
- Category
- Rule ID
- Document Name
- Section Number
- Section Title
- Location
- Source Text
- Description
- Suggestion
- Status
- Reviewer Comment
- Created At

导出文件适合用于人工 review、项目归档和后续跟踪。

## 5. Severity 说明

- High：明显影响报告准确性或提交质量的问题，例如百分比计算错误、表格合计错误、页眉页脚版本不一致、残留批注、残留修订痕迹。
- Medium：影响一致性、专业性或可读性的问题，例如引用不存在、标题编号跳号、缩写问题、术语写法不一致。
- Low：文字、格式和风格类问题，例如重复单词、多余空格、N/A 写法不统一。
- Critical：MVP 默认不主动使用，除非未来扩展到极高风险文档问题。

## 6. 系统做不到哪些事

本系统是 Word 文档质量 QA 工具，不是法规、医学或统计判断系统。

当前不支持或不承诺以下能力：

1. 不支持 PDF 文件检查。
2. 不支持扫描件和 OCR。
3. 不支持 `.doc` 老格式文件。
4. 不做 FDA、NMPA、EMA 或其他药政法规合规判断。
5. 不判断 IND 是否满足申报要求。
6. 不判断医学结论、临床结论、统计分析结论是否正确。
7. 不自动修改 Word 原文。
8. 不生成最终申报文件。
9. 不支持 eCTD。
10. 不支持电子签名。
11. 不支持复杂多用户权限系统。
12. 不支持 SSO。
13. 不支持复杂审计追踪。
14. 不提供云部署能力，MVP 以本地运行和本地文件存储为主。
15. 不保证识别所有复杂表格错误，当前表格合计检查主要面向简单数字表格。
16. 不保证识别所有语义矛盾，当前以确定性规则为主。
17. 不替代人工 QA review。

## 7. 推荐使用方式

- 在 Word 文档交付给 QA reviewer 前先运行一次系统检查。
- 对 High issue 优先人工确认。
- 对 Medium issue 重点关注一致性和引用问题。
- 对 Low issue 可作为文档清理和格式统一参考。
- 导出 Excel QA log 后，建议由人工 reviewer 填写最终处理意见。

## 8. 客户验收建议

建议客户使用一份已知存在问题的 `.docx` 文档进行试运行，确认以下流程可完成：

1. 创建项目。
2. 上传 Word 文件。
3. 解析成功。
4. 运行 QA。
5. 查看 issue list。
6. 打开 issue 详情。
7. 修改 issue 状态。
8. 填写 reviewer comment。
9. 导出 Excel QA log。

## 9. 一句话总结

Word Report QA Assistant 用于帮助团队更快发现 Word 报告中的文字、数字、表格、引用、编号、缩写、术语和 Word metadata 问题，但最终判断仍应由人工 reviewer 完成。
