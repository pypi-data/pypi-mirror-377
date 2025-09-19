# -*- coding: utf-8 -*-
"""
FJUD judgments crawler (雙模式整合版)
- full：抓整份（meta/sections/history/related_laws）
- snippet：只回傳「包含關鍵詞的句子片段」，以中文標點切句
  * --snippet-after：回傳句中「關鍵詞之後」的語句；若該句之後無內容，回傳下一句
  * --window：回傳前後 N 句的窗格（不指定或 0 則只回傳命中句）
  * --section-scope：搜尋範圍（all/reason/main），預設 all
"""
import re
import os
import io
import json
import time
import logging
import argparse
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

BASE = "https://judgment.judicial.gov.tw/FJUD/"

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
LOG = logging.getLogger("FJUDCrawler")


@dataclass
class QueryOptions:
    keyword: str
    max_items: int = 10
    timeout: int = 25
    sleep_sec: float = 0.8
    # 法院選擇
    choose_court: bool = False
    court_code: Optional[str] = None
    # 偵錯
    debug_dump_html: bool = True
    dump_dir: str = "dump"
    # 模式
    mode: str = "full"  # "full" | "snippet"
    snippet_after: bool = False
    window: int = 0
    snippets_per_doc: int = 5
    section_scope: str = "all"  # "all" | "reason" | "main"


# ---------- 小工具 ----------
def _ensure_dump_dir(path: str):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _dump_html(name: str, text: str, opts: QueryOptions):
    if not opts.debug_dump_html:
        return
    _ensure_dump_dir(opts.dump_dir)
    p = os.path.join(opts.dump_dir, name)
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(text)
    LOG.info("Dumped HTML -> %s", p)


def _clean_text(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\u3000", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\r?\n[ \t]*\r?\n+", "\n", s)
    return s.strip()


def _iso_from_minguo(s: str) -> Optional[str]:
    m = re.search(r"民國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日", s)
    if not m:
        m2 = re.search(r"(\d{2,3})\.(\d{1,2})\.(\d{1,2})", s)
        if m2:
            y = int(m2.group(1)) + 1911
            return f"{y:04d}-{int(m2.group(2)):02d}-{int(m2.group(3)):02d}"
        return None
    y = int(m.group(1)) + 1911
    return f"{y:04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"


# ---------- CJK reflow 與斷句 ----------
CJK = r"\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f"
_END_PUNCS = "。！？；：…．.!?;:,…」』）】〉》)"

_HEADING_PREFIXES = (
    "壹、","貳、","參、","肆、","伍、","陸、","柒、","捌、","玖、","拾、",
    "一、","二、","三、","四、","五、","六、","七、","八、","九、","十、",
    "㈠","㈡","㈢","㈣","㈤","㈥","㈦","㈧","㈨","㈩",
    "(一)","(二)","(三)","(四)","(五)","(六)","(七)","(八)","(九)","(十)",
    "主文","理由","事實及理由","據上論結","程序方面","實體方面",
)

def _strip_cjk_gaps(s: str) -> str:
    s = re.sub(fr"(?<=[{CJK}])\s+(?=[{CJK}])", "", s)
    s = re.sub(fr"\s+(?=[」』）】〉》、，。！？；：…\)])", "", s)
    s = re.sub(fr"(?<=[（(])\s+", "", s)
    return s

def _looks_like_heading(line: str) -> bool:
    t = line.strip()
    if not t:
        return False
    for p in _HEADING_PREFIXES:
        if t.startswith(p):
            return True
    if re.match(r"^第[一二三四五六七八九十百千0-9]+[條款項點]\b", t):
        return True
    if len(t) <= 12 and re.match(fr"^[{CJK}0-9A-Za-z（）()《》〈〉「」『』、，。；：…\-\s]+$", t) and t.endswith(("：", "： ")):
        return True
    return False

def _should_join(prev: str, nxt: str) -> bool:
    p = prev.rstrip()
    n = nxt.lstrip()
    if not p or not n:
        return False
    if p[-1] in _END_PUNCS:
        return False
    if _looks_like_heading(n):
        return False
    if n[0] in "、，。：；）」』》〉)":
        return True
    if re.match(fr"^[{CJK}A-Za-z0-9（(]", n):
        return True
    return False

def _reflow_text(raw: str) -> str:
    if not raw:
        return raw
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_strip_cjk_gaps(re.sub(r"[ \t]+", " ", ln.strip())) for ln in raw.split("\n")]

    out, buf = [], ""
    for ln in lines:
        if not ln:
            if buf:
                out.append(buf); buf = ""
            continue
        if not buf:
            buf = ln; continue
        if _should_join(buf, ln):
            if not (ln.startswith(("、","，","。","：","；","）","」","』","》","〉",")"))):
                if buf[-1].isascii() and ln[0].isascii():
                    buf += " "
            buf += ln
        else:
            out.append(buf); buf = ln
    if buf: out.append(buf)

    out = [_strip_cjk_gaps(p) for p in out if p.strip()]
    text = "\n\n".join(out)
    text = re.sub(r"^(主文|理由|事實及理由|程序方面|實體方面)(\S)", r"\1\n\2", text, flags=re.M)
    text = re.sub(r"^([壹一]\s*、?\s*程序方面[:：]?)\s*(\S)", r"\1\n\2", text, flags=re.M)
    text = re.sub(r"^([貳二]\s*、?\s*實體方面[:：]?)\s*(\S)", r"\1\n\2", text, flags=re.M)
    return text

def _sentence_split_chinese(text: str) -> List[str]:
    """
    以中文標點切句；保留終止標點與緊隨的右引號/右括號。
    """
    if not text:
        return []
    text = text.strip()
    parts = re.split(r'([。！？；](?:[」』）】〉》"]?) )', text)  # 注意結尾空格
    # 上面 regex 在某些 python 版本會吞空格，這裡做更穩妥的手法
    parts = re.split(r'([。！？；](?:[」』）】〉》"]?) )', text.replace(" ", " "))  # no-op 但保守
    parts = re.split(r'([。！？；](?:[」』）】〉》"]?))', text)
    sents = []
    for i in range(0, len(parts), 2):
        seg = parts[i].strip()
        if not seg:
            continue
        punc = parts[i+1] if i+1 < len(parts) else ""
        sents.append(seg + punc)
    return sents


# ---------- 第一步：提交關鍵字，取得 q ----------
def _get_state(sess: requests.Session, opts: QueryOptions) -> Dict[str, str]:
    url = urljoin(BASE, "default.aspx")
    LOG.info("GET default.aspx 以取得 VIEWSTATE/EVENTVALIDATION")
    r = sess.get(url, timeout=opts.timeout)
    r.raise_for_status()
    _dump_html("default.html", r.text, opts)
    soup = BeautifulSoup(r.text, "lxml")
    vs = soup.select_one("#__VIEWSTATE")
    ev = soup.select_one("#__EVENTVALIDATION")
    vsg = soup.select_one("#__VIEWSTATEGENERATOR")
    if not (vs and ev):
        _dump_html("default_no_state.html", r.text, opts)
        raise RuntimeError("抓不到 __VIEWSTATE / __EVENTVALIDATION")
    return {
        "__VIEWSTATE": vs["value"],
        "__EVENTVALIDATION": ev["value"],
        "__VIEWSTATEGENERATOR": vsg["value"] if vsg else "",
    }


def _post_keyword(sess: requests.Session, opts: QueryOptions) -> str:
    form = _get_state(sess, opts)
    form.update({
        "txtKW": opts.keyword,
        "judtype": "JUDBOOK",
        "whosub": "0",
        "ctl00$cp_content$btnSimpleQry": "送出查詢",
        "__VIEWSTATEENCRYPTED": ""
    })
    url = urljoin(BASE, "default.aspx")
    LOG.info("POST default.aspx 送出關鍵字查詢 keyword=%r", opts.keyword)
    r = sess.post(url, data=form, timeout=opts.timeout, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })
    r.raise_for_status()
    _dump_html("after_simple_query.html", r.text, opts)
    soup = BeautifulSoup(r.text, "lxml")
    a = soup.select_one("#result-count a[href*='qryresultlst.aspx']") or soup.select_one("a[href*='qryresultlst.aspx']")
    if not a:
        LOG.error("查無 qryresultlst 入口，可能無結果或被風控")
        raise RuntimeError("查無查詢結果入口")
    parsed = urlparse(urljoin(BASE, a.get("href")))
    q = parse_qs(parsed.query).get("q", [None])[0]
    if not q:
        LOG.error("結果連結無 q 參數: %s", a.get("href"))
        raise RuntimeError("查無 q 參數")
    LOG.info("取得 q=%s", q)
    return q


# ---------- 法院選單 ----------
def _fetch_court_menu(sess: requests.Session, q: str, opts: QueryOptions) -> List[Tuple[str, str, int]]:
    url = urljoin(BASE, f"qryresultlst.aspx?ty=JUDBOOK&q={q}")
    LOG.info("GET 結果主頁（取法院群組面板） %s", url)
    r = sess.get(url, timeout=opts.timeout)
    r.raise_for_status()
    _dump_html("result_home.html", r.text, opts)
    soup = BeautifulSoup(r.text, "lxml")

    panel = soup.select_one(".panel-body[data-group='jcourt']")
    if not panel:
        LOG.warning("找不到法院群組面板 data-group='jcourt'")
        return []

    items = []
    for li in panel.select("li"):
        a = li.select_one("a[href*='qryresultlst.aspx']")
        if not a:
            continue
        code = a.get("data-groupid") or ""
        label = a.get_text(" ", strip=True)
        badge = a.select_one(".badge")
        count = int(badge.get_text()) if badge and badge.get_text().isdigit() else -1
        if " " in label:
            label = label.rsplit(" ", 1)[0]
        items.append((code, label, count))
    return items


def _prompt_court_choice(menu: List[Tuple[str, str, int]]) -> Optional[str]:
    print("\n=== 法院選單（輸入數字選擇；0=全部，不分法院）===")
    print("0) 全部（不分法院）")
    for i, (code, label, count) in enumerate(menu, start=1):
        cnt = f"{count}" if count >= 0 else "?"
        print(f"{i}) {label} ({code}) - {cnt} 筆")

    while True:
        choice = input("請輸入選擇（預設 0）: ").strip()
        if choice == "" or choice == "0":
            return None
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(menu):
                return menu[idx - 1][0]
        print("無效的輸入，請重試。")


# ---------- 列表抓取 ----------
def _parse_list_html(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table#jud") or soup.find("table", class_="jub-table")
    if not table:
        LOG.error("找不到列表 table（可能 0 筆或模板改版）")
        return []

    rows = table.find_all("tr")
    if len(rows) <= 1:
        LOG.warning("列表無資料列 (rows=%d)", len(rows))
        return []

    items = []
    for tr in rows[1:]:
        a = tr.select_one("a.hlTitle_scroll, a[href*='data.aspx?ty=JD']")
        if not a:
            continue
        href = urljoin(BASE, a.get("href", ""))
        parsed = urlparse(href)
        jid = parse_qs(parsed.query).get("id", [None])[0]
        tds = tr.find_all("td")
        date_str = _clean_text(tds[2].get_text()) if len(tds) >= 3 else ""
        cause = _clean_text(tds[3].get_text()) if len(tds) >= 4 else ""
        title = _clean_text(a.get_text())
        items.append({
            "id": jid,
            "title": title,
            "date_display": date_str,
            "date_iso": _iso_from_minguo(date_str),
            "cause": cause,
            "href": href
        })
    LOG.info("列表擷取 %d 筆", len(items))
    return items


def _fetch_list_all(sess: requests.Session, q: str, opts: QueryOptions) -> List[Dict[str, Any]]:
    url = urljoin(BASE, f"qryresultlst.aspx?ty=JUDBOOK&q={q}")
    LOG.info("GET 列表頁（全部法院） %s", url)
    r = sess.get(url, timeout=opts.timeout)
    r.raise_for_status()
    _dump_html("list_all.html", r.text, opts)
    return _parse_list_html(r.text)


def _fetch_list_by_court(sess: requests.Session, q: str, court_code: str, opts: QueryOptions) -> List[Dict[str, Any]]:
    url = urljoin(BASE, f"qryresultlst.aspx?ty=JUDBOOK&q={q}&gy=jcourt&gc={court_code}")
    LOG.info("GET 列表頁（指定法院 %s） %s", court_code, url)
    r = sess.get(url, timeout=opts.timeout)
    r.raise_for_status()
    _dump_html(f"list_{court_code}.html", r.text, opts)
    return _parse_list_html(r.text)


# ---------- 內文擷取 ----------
def _extract_fulltext(soup: BeautifulSoup, opts: QueryOptions) -> str:
    candidates = [
        ".jud_content .text-pre.text-pre-in",
        ".jud_content pre",
        "#jud .text-pre.text-pre-in",
        "#jud pre",
        ".text-pre",
        "#jud",
    ]
    for sel in candidates:
        node = soup.select_one(sel)
        if node:
            text = _clean_text(node.get_text("\n"))
            if text and len(text) > 30:
                LOG.info("抓到內文容器: %s", sel)
                return text

    node = soup.select_one(".htmlcontent")
    if node:
        text = _clean_text(node.get_text("\n"))
        if text and len(text) > 30:
            LOG.info("抓到內文容器: .htmlcontent")
            return text

    LOG.warning("內文容器未命中，嘗試以全文 fallback")
    body = soup.select_one("body")
    if body:
        text = _clean_text(body.get_text("\n"))
        return text
    return ""


def _split_sections(full_text: str) -> Dict[str, str]:
    if not full_text:
        return {"content_raw": ""}

    marks = [
        ("主文", r"^\s*主\s*文\s*$"),
        ("事實及理由", r"^\s*事\s*實\s*及\s*理\s*由\s*$"),
        ("理由", r"^\s*理\s*由\s*$"),
        ("程序方面", r"^\s*([壹一]\s*、)?\s*程\s*序\s*方\s*面\s*[:：]?\s*$"),
        ("實體方面", r"^\s*([貳二]\s*、)?\s*實\s*體\s*方\s*面\s*[:：]?\s*$"),
        ("關於廢棄發回部分", r"^\s*關於廢棄發回部分\s*[:：]?\s*$"),
        ("關於駁回上訴部分", r"^\s*關於駁回上訴部分\s*[:：]?\s*$"),
        ("據上論結", r"^\s*據\s*上\s*論\s*結\s*[:：]?\s*$"),
    ]

    lines = [ln.rstrip() for ln in full_text.splitlines()]
    found = []
    for name, pat in marks:
        for i, ln in enumerate(lines):
            if re.match(pat, ln):
                found.append((i, name))
                break

    if not found:
        return {"content_raw": full_text}

    found.sort(key=lambda x: x[0])
    sections: Dict[str, str] = {}

    first_idx = found[0][0]
    preface = "\n".join(lines[:first_idx]).strip()
    if preface:
        sections["前置"] = preface

    for idx, (start, name) in enumerate(found):
        end = found[idx + 1][0] if idx + 1 < len(found) else len(lines)
        body = "\n".join(lines[start + 1:end]).strip()
        sections[name] = body

    return sections


def _sanitize_preface(preface: str) -> str:
    if not preface:
        return preface
    bad_prefixes = ("裁判字號：", "裁判日期：", "裁判案由：")
    keep = []
    for raw in preface.replace("\r\n", "\n").split("\n"):
        ln = raw.strip()
        if not ln:
            continue
        if any(ln.startswith(p) for p in bad_prefixes):
            continue
        keep.append(ln)
    out = "\n\n".join(keep).strip()
    return out


# ---------- 內頁解析 ----------
def _parse_detail(sess: requests.Session, jid: str, opts: QueryOptions) -> Dict[str, Any]:
    url = urljoin(BASE, f"data.aspx?ty=JD&id={jid}&ot=in")
    LOG.info("GET 內頁 %s", url)
    r = sess.get(url, timeout=opts.timeout)
    r.raise_for_status()
    safe_id = re.sub(r'[^0-9A-Za-z_]+','_', jid)
    _dump_html(f"detail_{safe_id}.html", r.text, opts)

    soup = BeautifulSoup(r.text, "lxml")

    def get_field(label: str) -> str:
        for row in soup.select("#jud .row"):
            th = row.select_one(".col-th")
            td = row.select_one(".col-td")
            if th and td and label in th.get_text():
                return _clean_text(td.get_text())
        return ""

    title = get_field("裁判字號")
    date_minguo = get_field("裁判日期")
    cause = get_field("裁判案由")
    date_iso = _iso_from_minguo(date_minguo)

    full_text = _extract_fulltext(soup, opts)
    full_text = _reflow_text(full_text)

    if not full_text:
        LOG.warning("full_text 空白，嘗試備援 URL（不帶 ot）")
        alt_url = urljoin(BASE, f"data.aspx?ty=JD&id={jid}")
        try:
            r2 = sess.get(alt_url, timeout=opts.timeout)
            r2.raise_for_status()
            _dump_html(f"detail_alt_{safe_id}.html", r2.text, opts)
            soup2 = BeautifulSoup(r2.text, "lxml")
            full_text = _reflow_text(_extract_fulltext(soup2, opts))
            if not title:
                def gf2(label: str) -> str:
                    for row in soup2.select("#jud .row"):
                        th = row.select_one(".col-th")
                        td = row.select_one(".col-td")
                        if th and td and label in th.get_text():
                            return _clean_text(td.get_text())
                    return ""
                title = title or gf2("裁判字號")
                date_minguo = date_minguo or gf2("裁判日期")
                cause = cause or gf2("裁判案由")
                date_iso = date_iso or _iso_from_minguo(date_minguo)
                soup = soup2
        except Exception as e:
            LOG.warning("備援 URL 仍失敗: %s", e)

    sections = _split_sections(full_text)

    if "前置" in sections:
        sections["前置"] = _sanitize_preface(_reflow_text(sections["前置"]))
    for k in list(sections.keys()):
        if k != "前置" and isinstance(sections[k], str) and sections[k]:
            sections[k] = _reflow_text(sections[k])

    # 歷審
    history: List[Dict[str, Any]] = []
    his_root = soup.select_one("#JudHis ul") or soup.select_one(".panel #JudHis ul")
    lis = []
    if his_root:
        lis = his_root.select("li")
    else:
        LOG.warning("找不到 #JudHis，啟用 fallback 擷取歷審連結")
        lis = soup.select(".rela-area a[href*='data.aspx?ty=JD']") or soup.select("a[href*='data.aspx?ty=JD']")

    for li in lis:
        a = li if li.name == "a" else li.select_one("a")
        if not a:
            continue
        txt = _clean_text(a.get_text())
        href = urljoin(BASE, a.get("href", ""))
        parsed = urlparse(href)
        hid = parse_qs(parsed.query).get("id", [None])[0]
        m = re.search(r"\((\d{2,3}\.\d{1,2}\.\d{1,2})\)$", txt)
        date_disp = m.group(1) if m else ""
        history.append({
            "id": hid,
            "display": txt,
            "date_display": date_disp,
            "date_iso": _iso_from_minguo(date_disp) if date_disp else None,
            "href": href
        })

    # 相關法條
    related_laws = [_clean_text(li.get_text()) for li in soup.select("#JudrelaLaw ul.rela-law li")]
    if not related_laws:
        LOG.warning("找不到 #JudrelaLaw，啟用 fallback 擷取相關法條")
        for panel in soup.select(".panel"):
            title_el = panel.select_one(".panel-title")
            if title_el and "相關法條" in title_el.get_text():
                related_laws = [_clean_text(li.get_text()) for li in panel.select("li")]
                if related_laws:
                    break

    court = None
    judgment_type = None
    case_no = None
    if title:
        m = re.search(r"^(?P<court>\S+法院)\s+(?P<year>\d+)\s*年度\s*(?P<chars>\S+)\s*字第\s*(?P<num>\d+)\s*號(?P<jtype>\S+判決|\S+裁定)?", title)
        if m:
            court = m.group("court")
            case_no = f"{m.group('year')}年度{m.group('chars')}字第{m.group('num')}號"
            judgment_type = m.group("jtype")

    return {
        "meta": {
            "id": jid,
            "title": title,
            "court": court,
            "case_no": case_no,
            "judgment_type": judgment_type,
            "date_minguo": date_minguo,
            "date_iso": date_iso,
            "cause": cause,
            "source_url": url
        },
        "sections": sections if sections else {"content_raw": full_text or ""},
        "history_list": history,
        "related_laws": related_laws,
        "content_raw": sections.get("content_raw") if isinstance(sections, dict) else None
    }


# ---------- snippet 模式：從章節抓句子 ----------
_REASON_KEYS = {
    "理由","事實及理由","程序方面","實體方面",
    "關於廢棄發回部分","關於駁回上訴部分","據上論結"
}

def _scope_sections(sections: Dict[str, str], scope: str) -> List[Tuple[str, str]]:
    if not isinstance(sections, dict):
        return [("全文", sections or "")]
    if scope == "main":
        texts = [(k, v) for k, v in sections.items() if k == "主文"]
        if texts: return texts
    if scope == "reason":
        texts = [(k, v) for k, v in sections.items() if k in _REASON_KEYS]
        if texts: return texts
    # all
    return list(sections.items())

def _extract_snippets_from_text(text: str, keyword: str, after_only: bool, window: int, max_snips: int) -> List[Dict[str, Any]]:
    sents = _sentence_split_chinese(text)
    out = []
    for i, s in enumerate(sents):
        pos = s.find(keyword)
        if pos == -1:
            continue
        if after_only:
            tail = s[pos+len(keyword):].lstrip()
            snippet = tail if tail else (sents[i+1] if i+1 < len(sents) else s)
        elif window and window > 0:
            start = max(0, i - window)
            end = min(len(sents), i + 1 + window)
            snippet = "".join(sents[start:end])
        else:
            snippet = s

        out.append({
            "sentence": s,
            "snippet": snippet,
            "keyword": keyword,
            "sentence_index": i,
            "offset": pos,
        })
        if len(out) >= max_snips:
            break
    return out

def _extract_snippets_from_sections(sections: Dict[str, str], keyword: str, after_only: bool, window: int, max_snips: int, scope: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for sec_name, sec_text in _scope_sections(sections, scope):
        if not isinstance(sec_text, str) or not sec_text.strip():
            continue
        snips = _extract_snippets_from_text(sec_text, keyword, after_only, window, max_snips)
        for sn in snips:
            sn["section"] = sec_name
            results.append(sn)
        if len(results) >= max_snips:
            break
    return results[:max_snips]


# ---------- 主流程 ----------
def crawl(opts: QueryOptions) -> Dict[str, Any]:
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36")
    })

    q = _post_keyword(sess, opts)
    time.sleep(opts.sleep_sec)

    chosen_code: Optional[str] = None
    if opts.court_code:
        chosen_code = opts.court_code.strip().upper()
        LOG.info("使用指定法院代碼：%s", chosen_code)
        lst = _fetch_list_by_court(sess, q, chosen_code, opts)
    elif opts.choose_court:
        menu = _fetch_court_menu(sess, q, opts)
        if not menu:
            LOG.warning("取不到法院選單，改抓全部")
            lst = _fetch_list_all(sess, q, opts)
        else:
            chosen_code = _prompt_court_choice(menu)
            lst = _fetch_list_by_court(sess, q, chosen_code, opts) if chosen_code else _fetch_list_all(sess, q, opts)
    else:
        LOG.info("未指定法院且未要求互動選擇 → 抓全部法院")
        lst = _fetch_list_all(sess, q, opts)

    out_items = []
    for it in lst[:opts.max_items]:
        try:
            time.sleep(opts.sleep_sec)
            detail = _parse_detail(sess, it["id"], opts)
            detail["list_entry"] = it

            if opts.mode == "snippet":
                # 只保留必要欄位 + snippets
                sections = detail.get("sections") or {}
                snippets = _extract_snippets_from_sections(
                    sections=sections,
                    keyword=opts.keyword,
                    after_only=opts.snippet_after,
                    window=opts.window,
                    max_snips=opts.snippets_per_doc,
                    scope=opts.section_scope
                )
                out_items.append({
                    "meta": detail["meta"],
                    "list_entry": it,
                    "snippets": snippets
                })
            else:
                out_items.append(detail)

        except Exception as e:
            LOG.exception("解析內頁失敗 id=%s", it.get("id"))
            stub = {
                "meta": {"id": it.get("id"), "title": it.get("title")},
                "list_entry": it,
                "error": f"{type(e).__name__}: {e}"
            }
            if opts.mode == "snippet":
                stub["snippets"] = []
            out_items.append(stub)

    return {
        "query": {
            "keyword": opts.keyword,
            "court_code": chosen_code or "ALL",
            "max_items": opts.max_items,
            "mode": opts.mode,
            "snippet_after": opts.snippet_after if opts.mode == "snippet" else None,
            "window": opts.window if opts.mode == "snippet" else None,
            "section_scope": opts.section_scope if opts.mode == "snippet" else None,
        },
        "total_listed": len(lst),
        "total_parsed": len(out_items),
        "items": out_items
    }


# ---------- CLI ----------
def parse_args() -> QueryOptions:
    ap = argparse.ArgumentParser(description="Judicial judgment crawler (FJUD)")
    ap.add_argument("keyword", help="關鍵字（例：所謂適當處分）")
    ap.add_argument("--max-items", type=int, default=3, help="解析內頁筆數上限（預設: 3）")
    ap.add_argument("--choose-court", action="store_true", help="互動式選單選法院（0=全部）")
    ap.add_argument("--court-code", help="指定法院代碼（如 TPS/TPH/TPD/TCH/KSD/...）")
    ap.add_argument("--timeout", type=int, default=25)
    ap.add_argument("--sleep-sec", type=float, default=0.8)
    ap.add_argument("--no-dump-html", action="store_true", help="不要輸出 HTML dump")
    ap.add_argument("--dump-dir", default="dump")

    # 模式
    ap.add_argument("--mode", choices=["full", "snippet"], default="full", help="輸出模式（full/snippet）")
    ap.add_argument("--snippet-after", action="store_true", help="snippet 模式：只回傳關鍵詞之後的語句")
    ap.add_argument("--window", type=int, default=0, help="snippet 模式：前後窗格（句數），0=只命中句")
    ap.add_argument("--snippets-per-doc", type=int, default=5, help="每份判決最多回傳片段數")
    ap.add_argument("--section-scope", choices=["all","reason","main"], default="all", help="搜尋範圍：all/reason/main")

    args = ap.parse_args()

    return QueryOptions(
        keyword=args.keyword,
        max_items=args.max_items,
        choose_court=args.choose_court,
        court_code=args.court_code,
        timeout=args.timeout,
        sleep_sec=args.sleep_sec,
        debug_dump_html=(not args.no_dump_html),
        dump_dir=args.dump_dir,
        mode=args.mode,
        snippet_after=args.snippet_after,
        window=args.window,
        snippets_per_doc=args.snippets_per_doc,
        section_scope=args.section_scope,
    )


if __name__ == "__main__":
    opts = parse_args()
    data = crawl(opts)
    print(json.dumps(data, ensure_ascii=False, indent=2))
