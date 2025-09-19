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
    mode: str = Field(default="full", description="搜尋模式: full 或 snippet")
    section_scope: str = Field(default="all", description="搜尋範圍: all, reason, main")
    timeout: int = Field(default=25, description="請求超時時間")

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

# ===== MCP 工具定義 =====

@mcp.tool()
def search_judgments(request: SearchRequest) -> Dict[str, Any]:
    """
    搜尋台灣司法院判決書

    根據關鍵字搜尋判決書，支援指定法院、搜尋模式等選項
    """
    try:
        opts = QueryOptions(
            keyword=request.keyword,
            max_items=request.max_items,
            court_code=request.court_code,
            mode=request.mode,
            section_scope=request.section_scope,
            timeout=request.timeout,
            debug_dump_html=False,  # MCP 模式下不輸出 HTML
        )

        result = crawl(opts)
        return {
            "success": True,
            "data": result,
            "message": f"成功搜尋到 {result['total_parsed']} 筆判決"
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
def search_by_case_number(case_number: str, max_items: int = 3) -> Dict[str, Any]:
    """
    根據案號搜尋判決書

    輸入完整案號或部分案號來搜尋相關判決
    """
    try:
        opts = QueryOptions(
            keyword=case_number,
            max_items=max_items,
            mode="full",
            debug_dump_html=False,
        )

        result = crawl(opts)
        return {
            "success": True,
            "data": result,
            "message": f"根據案號 '{case_number}' 找到 {result['total_parsed']} 筆判決"
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