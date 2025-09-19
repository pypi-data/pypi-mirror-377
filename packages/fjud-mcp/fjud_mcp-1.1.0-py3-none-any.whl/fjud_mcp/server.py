# -*- coding: utf-8 -*-
"""
FJUD MCP Server - 台灣司法院判決查詢 MCP 伺服器
基於 fastMCP 實現，提供判決書搜尋、解析、文字處理等功能
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 導入原有的判決爬蟲功能
from .crawler import (
    QueryOptions,
    crawl,
    _fetch_court_menu,
    _post_keyword,
    _parse_list_html,
    _parse_detail,
    _sentence_split_chinese,
    _extract_snippets_from_sections,
    _reflow_text,
    _clean_text,
    BASE
)
import requests

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 建立 MCP 伺服器
mcp = FastMCP("FJUD Judgment Crawler")

# ===== 資料模型 =====

class SearchRequest(BaseModel):
    """判決搜尋請求"""
    keyword: str = Field(description="搜尋關鍵字")
    max_items: int = Field(default=3, description="最大結果數量")
    court_code: Optional[str] = Field(default=None, description="法院代碼 (如 TPS, TPH, TPD)")
    mode: str = Field(default="summary", description="搜尋模式: summary(摘要), snippet(片段), full(完整)")
    section_scope: str = Field(default="all", description="搜尋範圍: all, reason, main")
    timeout: int = Field(default=25, description="請求超時時間")
    max_content_length: int = Field(default=2000, description="單個判決內容最大字數")
    include_full_text: bool = Field(default=False, description="是否包含完整內文")

class SnippetRequest(BaseModel):
    """片段擷取請求"""
    keyword: str = Field(description="關鍵字")
    max_items: int = Field(default=3, description="最大結果數量")
    snippet_after: bool = Field(default=False, description="只返回關鍵詞後的內容")
    window: int = Field(default=0, description="前後文窗格大小")
    snippets_per_doc: int = Field(default=5, description="每份判決的最大片段數")
    section_scope: str = Field(default="all", description="搜尋範圍")
    court_code: Optional[str] = Field(default=None, description="法院代碼")

class JudgmentDetailRequest(BaseModel):
    """判決詳情請求"""
    judgment_id: str = Field(description="判決書 ID")
    timeout: int = Field(default=25, description="請求超時時間")

class TextProcessRequest(BaseModel):
    """文字處理請求"""
    text: str = Field(description="要處理的文字")
    operation: str = Field(description="操作類型: clean, reflow, split_sentences")

# ===== 輔助函數 =====

def _truncate_content(content: str, max_length: int) -> str:
    """截斷內容到指定長度"""
    if not content or len(content) <= max_length:
        return content

    # 嘗試在句子邊界截斷
    truncated = content[:max_length]
    last_period = truncated.rfind('。')
    if last_period > max_length * 0.7:  # 如果句號位置合理
        return truncated[:last_period + 1] + "...(內容已截斷)"

    return truncated + "...(內容已截斷)"

def _create_summary_result(detail: Dict[str, Any], max_content_length: int, include_full_text: bool) -> Dict[str, Any]:
    """建立摘要格式的結果"""
    summary = {
        "meta": detail["meta"],
        "list_entry": detail.get("list_entry"),
        "related_laws": detail.get("related_laws", []),
        "history_count": len(detail.get("history_list", [])),
    }

    # 處理章節內容
    sections = detail.get("sections", {})
    if sections and isinstance(sections, dict):
        summary_sections = {}

        # 優先顯示主文
        if "主文" in sections:
            summary_sections["主文"] = _truncate_content(sections["主文"], min(max_content_length, 500))

        # 顯示理由的開頭部分
        for key in ["理由", "事實及理由"]:
            if key in sections:
                summary_sections[key] = _truncate_content(sections[key], max_content_length)
                break

        summary["sections"] = summary_sections

    # 根據設定決定是否包含完整內文
    if include_full_text:
        summary["full_sections"] = detail.get("sections")
        summary["full_content_warning"] = "完整內文已包含，可能消耗較多 token"

    return summary

# ===== MCP 工具定義 =====

@mcp.tool()
def search_judgments(request: SearchRequest) -> Dict[str, Any]:
    """
    搜尋台灣司法院判決書

    根據關鍵字搜尋判決書，支援多種模式：
    - summary: 只返回摘要信息（推薦，節省 token）
    - snippet: 返回關鍵字片段
    - full: 返回完整內容（消耗較多 token）
    """
    try:
        # 根據模式調整查詢選項
        if request.mode == "summary":
            # 摘要模式：使用 full 模式查詢但只返回摘要
            opts = QueryOptions(
                keyword=request.keyword,
                max_items=request.max_items,
                court_code=request.court_code,
                mode="full",
                section_scope=request.section_scope,
                timeout=request.timeout,
                debug_dump_html=False,
            )
        else:
            # 其他模式保持原樣
            opts = QueryOptions(
                keyword=request.keyword,
                max_items=request.max_items,
                court_code=request.court_code,
                mode=request.mode if request.mode in ["full", "snippet"] else "full",
                section_scope=request.section_scope,
                timeout=request.timeout,
                debug_dump_html=False,
            )

        result = crawl(opts)

        # 如果是摘要模式，處理結果
        if request.mode == "summary":
            summary_items = []
            for item in result.get("items", []):
                if "error" in item:
                    summary_items.append(item)  # 保留錯誤項目
                else:
                    summary_item = _create_summary_result(
                        item,
                        request.max_content_length,
                        request.include_full_text
                    )
                    summary_items.append(summary_item)

            result["items"] = summary_items
            result["mode"] = "summary"
            result["token_optimized"] = True

        return {
            "success": True,
            "data": result,
            "message": f"成功搜尋到 {result['total_parsed']} 筆判決 (模式: {request.mode})",
            "token_usage_hint": "summary 模式可節省 token，如需完整內容請使用 get_judgment_detail"
        }

    except Exception as e:
        logger.exception("搜尋判決時發生錯誤")
        return {
            "success": False,
            "error": str(e),
            "message": "搜尋判決失敗"
        }

@mcp.tool()
def extract_snippets(request: SnippetRequest) -> Dict[str, Any]:
    """
    擷取判決書中包含關鍵字的片段

    專門用於片段模式搜尋，提取包含特定關鍵字的句子片段
    """
    try:
        opts = QueryOptions(
            keyword=request.keyword,
            max_items=request.max_items,
            court_code=request.court_code,
            mode="snippet",
            snippet_after=request.snippet_after,
            window=request.window,
            snippets_per_doc=request.snippets_per_doc,
            section_scope=request.section_scope,
            debug_dump_html=False,
        )

        result = crawl(opts)
        return {
            "success": True,
            "data": result,
            "message": f"成功擷取 {result['total_parsed']} 筆判決的片段"
        }

    except Exception as e:
        logger.exception("擷取片段時發生錯誤")
        return {
            "success": False,
            "error": str(e),
            "message": "擷取片段失敗"
        }

@mcp.tool()
def get_judgment_detail(request: JudgmentDetailRequest) -> Dict[str, Any]:
    """
    取得特定判決書的詳細內容

    根據判決書 ID 取得完整的判決書內容，包含元資料、章節、歷審、相關法條等
    """
    try:
        sess = requests.Session()
        sess.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36")
        })

        opts = QueryOptions(
            keyword="",  # 不需要關鍵字
            timeout=request.timeout,
            debug_dump_html=False,
        )

        detail = _parse_detail(sess, request.judgment_id, opts)

        return {
            "success": True,
            "data": detail,
            "message": f"成功取得判決書 {request.judgment_id} 的詳細內容"
        }

    except Exception as e:
        logger.exception("取得判決詳情時發生錯誤")
        return {
            "success": False,
            "error": str(e),
            "message": "取得判決詳情失敗"
        }

@mcp.tool()
def get_court_list() -> Dict[str, Any]:
    """
    取得可用的法院列表

    返回系統支援的法院代碼和名稱列表
    """
    try:
        # 建立臨時 session 來取得法院列表
        sess = requests.Session()
        sess.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36")
        })

        # 使用臨時關鍵字來取得法院選單
        opts = QueryOptions(keyword="test", debug_dump_html=False)
        q = _post_keyword(sess, opts)
        court_menu = _fetch_court_menu(sess, q, opts)

        courts = [
            {
                "code": code,
                "name": name,
                "count": count
            }
            for code, name, count in court_menu
        ]

        return {
            "success": True,
            "data": courts,
            "message": f"成功取得 {len(courts)} 個法院資訊"
        }

    except Exception as e:
        logger.exception("取得法院列表時發生錯誤")
        return {
            "success": False,
            "error": str(e),
            "message": "取得法院列表失敗"
        }

@mcp.tool()
def process_text(request: TextProcessRequest) -> Dict[str, Any]:
    """
    處理中文法律文本

    支援多種文字處理操作：清理、重排、斷句等
    """
    try:
        if request.operation == "clean":
            result = _clean_text(request.text)
            operation_name = "清理"
        elif request.operation == "reflow":
            result = _reflow_text(request.text)
            operation_name = "重排"
        elif request.operation == "split_sentences":
            result = _sentence_split_chinese(request.text)
            operation_name = "斷句"
        else:
            return {
                "success": False,
                "error": "不支援的操作類型",
                "message": "支援的操作: clean, reflow, split_sentences"
            }

        return {
            "success": True,
            "data": result,
            "message": f"成功執行文字{operation_name}操作"
        }

    except Exception as e:
        logger.exception("處理文字時發生錯誤")
        return {
            "success": False,
            "error": str(e),
            "message": "文字處理失敗"
        }

@mcp.tool()
def quick_search(keyword: str, max_items: int = 5) -> Dict[str, Any]:
    """
    快速搜尋判決書（僅返回基本資訊，節省 token）

    專為快速查詢設計，只返回判決的基本元資料和案件摘要，
    不包含完整內文，適合初步瀏覽使用。
    """
    try:
        # 使用 summary 模式進行查詢
        opts = QueryOptions(
            keyword=keyword,
            max_items=max_items,
            mode="full",
            debug_dump_html=False,
        )

        result = crawl(opts)

        # 建立極簡版本的結果
        quick_items = []
        for item in result.get("items", []):
            if "error" in item:
                quick_items.append(item)
                continue

            quick_item = {
                "id": item["meta"]["id"],
                "title": item["meta"]["title"],
                "court": item["meta"]["court"],
                "date": item["meta"]["date_iso"],
                "cause": item["meta"]["cause"],
                "url": item["meta"]["source_url"],
                "laws_count": len(item.get("related_laws", [])),
                "history_count": len(item.get("history_list", [])),
            }

            # 只包含主文的前 200 字
            sections = item.get("sections", {})
            if "主文" in sections:
                quick_item["main_text_preview"] = _truncate_content(sections["主文"], 200)

            quick_items.append(quick_item)

        return {
            "success": True,
            "data": {
                "query": result["query"],
                "total_listed": result["total_listed"],
                "total_parsed": result["total_parsed"],
                "items": quick_items
            },
            "message": f"快速搜尋找到 {len(quick_items)} 筆判決",
            "usage_hint": "這是快速搜尋結果，如需完整內容請使用 get_judgment_detail 取得特定判決詳情"
        }

    except Exception as e:
        logger.exception("快速搜尋時發生錯誤")
        return {
            "success": False,
            "error": str(e),
            "message": "快速搜尋失敗"
        }

@mcp.tool()
def search_by_case_number(case_number: str, max_items: int = 3) -> Dict[str, Any]:
    """
    根據案號搜尋判決書

    輸入完整案號或部分案號來搜尋相關判決，使用摘要模式節省 token
    """
    try:
        opts = QueryOptions(
            keyword=case_number,
            max_items=max_items,
            mode="full",
            debug_dump_html=False,
        )

        result = crawl(opts)

        # 轉換為摘要模式
        summary_items = []
        for item in result.get("items", []):
            if "error" in item:
                summary_items.append(item)
            else:
                summary_item = _create_summary_result(item, 1000, False)
                summary_items.append(summary_item)

        result["items"] = summary_items
        result["mode"] = "summary"

        return {
            "success": True,
            "data": result,
            "message": f"根據案號 '{case_number}' 找到 {result['total_parsed']} 筆判決 (摘要模式)"
        }

    except Exception as e:
        logger.exception("根據案號搜尋時發生錯誤")
        return {
            "success": False,
            "error": str(e),
            "message": "案號搜尋失敗"
        }

@mcp.tool()
def get_judgment_summary(judgment_id: str) -> Dict[str, Any]:
    """
    取得判決書摘要資訊

    返回判決書的基本元資料，不包含完整內文
    """
    try:
        sess = requests.Session()
        sess.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36")
        })

        opts = QueryOptions(keyword="", debug_dump_html=False)
        detail = _parse_detail(sess, judgment_id, opts)

        # 只返回摘要資訊
        summary = {
            "meta": detail["meta"],
            "related_laws": detail["related_laws"],
            "history_count": len(detail["history_list"])
        }

        return {
            "success": True,
            "data": summary,
            "message": f"成功取得判決書 {judgment_id} 的摘要"
        }

    except Exception as e:
        logger.exception("取得判決摘要時發生錯誤")
        return {
            "success": False,
            "error": str(e),
            "message": "取得判決摘要失敗"
        }

# ===== 程式進入點 =====

def main():
    """主函數，啟動 MCP 伺服器"""
    mcp.run()

if __name__ == "__main__":
    main()