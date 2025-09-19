# FJUD MCP Server - 台灣司法院判決查詢 MCP 伺服器

[![PyPI version](https://badge.fury.io/py/fjud-mcp.svg)](https://badge.fury.io/py/fjud-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/fjud-mcp.svg)](https://pypi.org/project/fjud-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基於 fastMCP 實現的台灣司法院判決書查詢與解析工具，提供完整的 MCP (Model Context Protocol) 支援。

## 功能特色

### 🔍 判決搜尋
- **關鍵字搜尋**: 支援全文搜尋判決書內容
- **法院篩選**: 可指定特定法院或搜尋全部法院
- **案號搜尋**: 根據完整或部分案號查找判決

### 📄 內容解析
- **完整模式**: 取得判決書完整內容、元資料、歷審資訊
- **片段模式**: 擷取包含關鍵字的句子片段
- **文字處理**: 中文文本清理、重排、斷句等功能

### 🏛️ 法院資訊
- **法院列表**: 取得所有支援的法院代碼和名稱
- **分類搜尋**: 支援按法院類型進行搜尋

## MCP 工具列表

### 1. `search_judgments` - 搜尋判決書
根據關鍵字搜尋判決書，支援多種參數設定。

**參數:**
```json
{
  "keyword": "關鍵字",
  "max_items": 3,
  "court_code": "TPS",
  "mode": "full",
  "section_scope": "all",
  "timeout": 25
}
```

### 2. `extract_snippets` - 擷取片段
專門用於片段模式搜尋，提取包含特定關鍵字的句子。

**參數:**
```json
{
  "keyword": "關鍵字",
  "max_items": 3,
  "snippet_after": false,
  "window": 0,
  "snippets_per_doc": 5,
  "section_scope": "all",
  "court_code": null
}
```

### 3. `get_judgment_detail` - 取得判決詳情
根據判決書 ID 取得完整內容。

**參數:**
```json
{
  "judgment_id": "TPSV_103_2434_20141119",
  "timeout": 25
}
```

### 4. `get_court_list` - 取得法院列表
返回系統支援的法院代碼和名稱。

**參數:** 無

### 5. `process_text` - 文字處理
處理中文法律文本，支援清理、重排、斷句。

**參數:**
```json
{
  "text": "要處理的文字",
  "operation": "clean"
}
```

### 6. `search_by_case_number` - 案號搜尋
根據案號搜尋相關判決。

**參數:**
```json
{
  "case_number": "114年度上字第123號",
  "max_items": 3
}
```

### 7. `get_judgment_summary` - 取得判決摘要
返回判決書基本元資料，不包含完整內文。

**參數:**
```json
{
  "judgment_id": "TPSV_103_2434_20141119"
}
```

## 快速開始

### 方法一：使用 uv/uvx (推薦)

```bash
# 直接執行，無需安裝
uvx fjud-mcp

# 或者安裝後使用
uv add fjud-mcp
```

### 方法二：使用 pip

```bash
# 安裝套件
pip install fjud-mcp

# 啟動 MCP 伺服器
fjud-mcp
```

### 方法三：從原始碼安裝

```bash
# 克隆專案
git clone https://github.com/your-username/fjud-mcp.git
cd fjud-mcp

# 使用 uv 安裝
uv install

# 或使用 pip
pip install -e .

# 啟動伺服器
fjud-mcp
```

## Claude Desktop 設定

將以下設定加入到 Claude Desktop 的 `claude_desktop_config.json` 檔案中：

```json
{
  "mcpServers": {
    "fjud-mcp": {
      "command": "uvx",
      "args": ["fjud-mcp"]
    }
  }
}
```

或者如果您使用 pip 安裝：

```json
{
  "mcpServers": {
    "fjud-mcp": {
      "command": "fjud-mcp"
    }
  }
}
```

## 使用範例

### 搜尋包含特定關鍵字的判決
```python
# 使用 MCP 工具
search_judgments({
    "keyword": "不當得利",
    "max_items": 5,
    "mode": "full"
})
```

### 擷取關鍵字片段
```python
# 擷取包含關鍵字的句子片段
extract_snippets({
    "keyword": "侵權行為",
    "snippet_after": true,
    "window": 1,
    "section_scope": "reason"
})
```

### 取得法院列表
```python
# 取得所有支援的法院
get_court_list()
```

## 支援的法院代碼

- `TPS`: 台灣高等法院
- `TPH`: 台北高等法院
- `TPD`: 台北地方法院
- `TCH`: 台中高等法院
- `KSD`: 高雄地方法院
- 等等...

## 開發與貢獻

### 開發環境設定

```bash
# 克隆專案
git clone https://github.com/your-username/fjud-mcp.git
cd fjud-mcp

# 使用 uv 建立開發環境
uv venv
uv install --dev

# 執行測試
uv run pytest

# 格式化程式碼
uv run black .
uv run isort .
```

### 發布到 PyPI

專案包含自動化 PyPI 上傳腳本：

```bash
# 執行上傳腳本
python upload_to_pypi.py
```

腳本功能：
- ✅ 自動檢查必要工具 (build, twine)
- 🧹 清理舊的建置檔案
- 📦 建置套件
- 🔍 檢查套件完整性
- 🧪 上傳到 Test PyPI 並測試安裝
- 🚀 上傳到正式 PyPI

## 注意事項

1. **網路連線**: 需要穩定的網路連線存取司法院網站
2. **請求頻率**: 內建延遲機制避免過於頻繁的請求
3. **資料時效**: 判決書資料來源為司法院官方網站
4. **編碼處理**: 自動處理繁體中文編碼和格式

## 授權條款

本專案採用 MIT 授權條款。僅供學術研究和合法用途使用。使用者應遵守相關法律法規和司法院網站使用條款。