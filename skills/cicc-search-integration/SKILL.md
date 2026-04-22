---
name: cicc-search-integration
description: 中金网页内容搜索，支持通过自然语言搜索中金内部知识库的文章内容，获取文章标题、发布时间、正文等信息。适用于查找中金内部文档、研究报告、资讯文章等场景。Search CICC internal web content and articles, supporting natural language queries to retrieve article titles, publish time, and content.
metadata:
  {
    "openclaw": {
      "requires": {
        "bins": ["python3", "pip3"]
      }
    }
  }
---

# 中金网页内容搜索

通过**自然语言查询**检索中金内部知识库的文章内容，支持获取文章标题、发布时间、正文摘要等信息。

## 适用场景

- **内部文档检索**：查找中金内部知识库中的相关文档
- **资讯文章搜索**：获取特定主题的文章列表和摘要
- **研究资料查找**：搜索与研究相关的内部文章
- **热点追踪**：查询特定热点主题的相关文章

## 密钥来源与安全说明

- 本技能使用环境变量：`CICC_SEARCH_URL` 配置接口地址
- 禁止在代码、提示词、日志或输出文件中硬编码/明文暴露密钥

## 功能范围

### 基础检索能力
- 检索中金内部知识库的文章内容
- 提取文章标题、发布时间、正文摘要
- 返回结构化文本内容
- 支持将结果保存为本地 `.txt` 文件，便于追溯与复盘
- 默认搜索最近一年的文章

### 输入要求
- **query**（必填）：查询关键词，建议包含明确的目标（主题、关键词等）

- 示例查询：
  - "人工智能发展趋势"
  - "新能源行业分析"
  - "宏观经济政策解读"
  - "投资策略建议"

### 查询示例

| 类型 | query 示例 |
|---|---|
| 行业分析 | 半导体行业、医药板块分析 |
| 主题热点 | 人工智能、新能源、碳中和 |
| 宏观政策 | 货币政策、财政政策解读 |
| 投资策略 | 资产配置、投资组合建议 |

## 快速开始

### 1. 命令行调用

```bash
python3 -m {baseDir}/scripts/get_data.py "<用户输入的查询问题>"
```

**输出示例**
```text
Saved: /path/to/workspace/cicc/cicc-web-search/cicc_research_integration_f7261c14.txt
（随后输出文章列表内容）
```

**参数说明：**

| 参数 | 说明 | 必填 |
|---|---|---|
| `query`（位置参数） | 自然语言查询文本 | ✅（位置参数或 stdin 二选一） |
| `--no-save` | 仅输出结果，不写入本地文件 | 否 |

### 2. 代码调用

```python
import asyncio
from pathlib import Path
from script.get_data import query_search_data

async def main():
    result = await query_search_data(
        query="人工智能发展趋势",
        output_dir=Path("workspace/cicc-search-integration"),
        save_to_file=True,
    )
    if "error" in result:
        print(result["error"])
    else:
        print(result["content"])
        if result.get("output_path"):
            print("已保存至:", result["output_path"])

asyncio.run(main())
```

## 输出文件说明

| 文件 | 说明 |
|---|---|
| `cicc_research_integration_<ID>.txt` | 搜索结果文本（包含文章标题、时间、正文） |

## 返回字段说明

- `query`：原始查询语句
- `content`：格式化后的搜索结果文本
- `output_path`：当 `save_to_file=True` 且有内容时，返回保存路径
- `raw`：原始接口返回的完整数据列表，便于调试或二次处理
- `error`：检索失败时返回错误信息

## 常见问题

**没有传 query 时为什么直接退出？**  
→ 命令行会先读取位置参数 `query`，若为空再读取 stdin；两者都为空时打印帮助并退出。

**如何只看输出，不落盘？**
```bash
python3 -m scripts/get_data.py --no-save "人工智能发展趋势"
```

## 合规说明

- 禁止在代码或提示词中硬编码账号 ID、会话 ID 或 token。
- 环境变量按敏感信息处理，不在日志或回复中泄露。
- 检索失败时不得编造事实，应返回明确错误或不确定性说明。
- 输出应保持可追溯、可审计。
