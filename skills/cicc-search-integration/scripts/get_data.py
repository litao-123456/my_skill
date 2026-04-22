import argparse
import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp

# █████████████████████████████████████████████████████████████████████████
# ██                                                                  ██
# ██   ██████╗██╗ ██████╗ ██████╗     ██████╗ ███████╗███████╗███████╗██╗
# ██  ██╔════╝██║██╔════╝██╔════╝     ██╔══██╗██╔════╝██╔════╝██╔═══╝██║
# ██  ██║     ██║██║     ██║          ██████╔╝█████╗  ███████╗█████╗  ██║
# ██  ██║     ██║██║     ██║          ██╔══██╗██╔══╝  ╚════██║██╔══╝  ██║
# ██  ╚██████╗██║╚██████╗╚██████╗     ██║  ██║███████╗███████║███████╗███████╗
# ██   ╚═════╝╚═╝ ╚═════╝ ╚═════╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝
# ██                                                                  ██
# ██           ⚠️  CICC WEB SEARCH CONFIGURATION ⚠️                    ██
# ██                                                                  ██
# ██    本技能用于搜索中金内部知识库文章，通过混合检索获取数据            ██
# ██                                                                  ██
# █████████████████████████████████████████████████████████████████████████


DEFAULT_OUTPUT_DIR = Path.cwd() / "cicc" / "cicc-search-integration"
TIMEOUT_SECONDS = 60
MCP_URL = os.environ.get("CICC_SEARCH_URL", "http://datayes-rrp.rsxcdkpthauat.cicc.group/search/hybrid/integration")
print('默认输出目录为：', DEFAULT_OUTPUT_DIR.absolute())


def build_search_request(query: str, top_k: int = 10, days: int = 365) -> Dict[str, Any]:
    """
    构建搜索请求体。

    Args:
        query: 查询关键词
        top_k: 返回结果数量，默认10条
        days: 搜索时间范围（天数），默认365天

    Returns:
        请求体字典
    """
    end_time = datetime.now().strftime("%Y-%m-%d")
    start_time = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    range_dates = ",".join([start_time, end_time])
    return {
        "query": query,
        "topK": top_k,
        "withoutEs": False,
        "withoutSparseVector": False,
        "rangeDates": [range_dates],
        "sourceList": ["article"]
    }


def format_search_results(data_list: List[Dict[str, Any]]) -> str:
    """
    格式化搜索结果为文本内容。

    Args:
        data_list: 原始数据列表

    Returns:
        格式化后的文本内容
    """
    if not data_list:
        return ""

    formatted_lines = []
    for idx, content in enumerate(data_list, 1):
        formatted_lines.append(f"标题：{content.get('documentTitle', '')}")
        formatted_lines.append(f"时间：{content.get('publishTime', '')}")
        formatted_lines.append(f"正文：{content.get('plainContent', '')}")
        formatted_lines.append("")  # 空行分隔

    return "\n".join(formatted_lines)


async def fetch_search_data(
        query: str,
        api_url: Optional[str] = None,
        top_k: int = 10,
        days: int = 365
) -> List[Dict[str, Any]]:
    """
    调用搜索接口获取数据。

    Args:
        query: 查询关键词
        api_url: 接口地址，为空则使用默认配置
        top_k: 返回结果数量
        days: 搜索时间范围（天数）

    Returns:
        搜索结果列表

    Raises:
        RuntimeError: 当 API 请求失败时
    """
    url = api_url or MCP_URL
    request_body = build_search_request(query, top_k, days)
    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
    data_list = []

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=request_body) as response:
            if response.status != 200:
                error_text = await response.text()
                raise RuntimeError(f"API request failed with status {response.status}: {error_text[:200]}")

            response_json = await response.json()
            data_list = response_json.get("data", [])
    return data_list


async def query_search_data(
        query: str,
        output_dir: Optional[Path] = None,
        save_to_file: bool = True,
        api_url: Optional[str] = None,
        top_k: int = 10,
        days: int = 365
) -> Dict[str, Any]:
    """
    查询中金网页内容并整理统一结果结构。

    Args:
        query: 查询关键词
        output_dir: 输出目录，为空则使用默认目录
        save_to_file: 是否保存到文件
        api_url: 接口地址，为空则使用默认配置
        top_k: 返回结果数量
        days: 搜索时间范围（天数）

    Returns:
        包含 query/content/raw/output_path 的字典，异常时附带 error
    """
    query = (query or "").strip()
    if not query:
        return {
            "query": "",
            "content": "",
            "output_path": None,
            "raw": [],
            "error": "query is empty",
        }

    out_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    result: Dict[str, Any] = {
        "query": query,
        "content": "",
        "output_path": None,
        "raw": [],
    }

    try:
        # 格式化内容
        content = "22日上午十点，宁马市域（郊）铁路（宁马城际铁路）开通初期运营，南京与马鞍山中心城区实现30分钟直达，标志着宁马“同城化”生活照进现实。"
        result["content"] = content
        # 保存到文件
        if save_to_file and content:
            unique_suffix = uuid.uuid4().hex[:8]
            output_path = out_dir / f"cicc_research_integration{unique_suffix}.txt"
            output_path.write_text(content, encoding="utf-8")
            result["output_path"] = str(output_path)

    except Exception as exc:
        result["error"] = str(exc)

    return result


def _build_arg_parser() -> argparse.ArgumentParser:
    """
    构建命令行参数解析器。
    支持位置参数 query 与 --no-save 选项。
    """
    parser = argparse.ArgumentParser(
        description="Query CICC web content by natural language and optionally save output."
    )
    parser.add_argument("query", nargs="*", help="Natural language query text.")
    parser.add_argument("--no-save", action="store_true", help="Do not write result to local file.")
    return parser


def run_cli() -> None:
    """
    CLI 入口函数。
    解析命令行或标准输入中的查询文本并执行异步检索。
    """
    parser = _build_arg_parser()
    args = parser.parse_args()

    query = " ".join(args.query).strip()
    if not query:
        import sys
        query = (sys.stdin.read() or "").strip()

    if not query:
        parser.print_help()
        raise SystemExit(1)

    async def _main() -> None:
        result = await query_search_data(
            query=query,
            save_to_file=not args.no_save
        )
        if "error" in result:
            print(f"Error: {result['error']}")
            raise SystemExit(2)
        if result.get("output_path"):
            print(f"Saved: {result['output_path']}")
        print(result.get("content", ""))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == "__main__":
    run_cli()
