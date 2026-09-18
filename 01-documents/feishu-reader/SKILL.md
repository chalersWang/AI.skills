---
name: feishu-reader
description: 读取和操作飞书（Lark）文档与知识库。当用户要求读取/查询飞书文档、知识库（wiki）、云文档内容，列出知识库文件树、读取文档正文、下载云盘文件、读取电子表格，或移动/整理知识库节点时使用此skill。需自行配置企业自建应用凭据（本文件已脱敏），通过 tenant_access_token 调用飞书开放平台 API。触发场景包括：(1)读取某个飞书文档/知识库内容 (2)列出知识库的文件/目录树 (3)查询"Upgrade"等已授权知识库的文件 (4)读取飞书文档正文原文 (5)下载飞书云盘里的文件(file) (6)读取飞书电子表格(sheet) (7)移动知识库节点
---

# 飞书（Feishu/Lark）文档读取

## Overview

通过飞书开放平台企业自建应用，以 `tenant_access_token`（应用身份）调用 API 读取文档和知识库内容。

## 应用凭据（已脱敏，请自行填写）

- **app_id**: `YOUR_APP_ID`
- **app_secret**: `YOUR_APP_SECRET`
- 企业：`YOUR_TENANT.feishu.cn`

> ⚠️ 安全提示：本仓库版本已脱敏（真实 app_id / app_secret / open_id / 手机号 / space_id 已替换为占位符）。使用前请填入你自己的飞书应用凭据，推荐改用环境变量 `FEISHU_APP_SECRET` 存储（下文的 token 获取命令可用 `$FEISHU_APP_SECRET` 替换）。原始本地版本若曾同步或分享，请到飞书开放平台「凭证与基础信息」重置 App Secret。

## 关键资源（已知）

| 资源 | ID |
|------|-----|
| Upgrade 知识库 space_id | `YOUR_SPACE_ID` |
| 用户本人 open_id | `YOUR_OPEN_ID` |
| 用户手机号 | `YOUR_PHONE` |

## 已开通的权限 scope

- `wiki:wiki:readonly` — 读取 wiki 节点（get_node）
- `wiki:space:retrieve` — 列出知识库文件树（spaces/{id}/nodes）
- `wiki:wiki` — 编辑 wiki 节点（移动节点 move）
- `docx:document:readonly` — 读取文档正文（raw_content）
- `drive:drive:readonly` — 下载云盘文件（drive/v1/files/{token}/download）
- `sheets:spreadsheet:readonly` — 读取电子表格（sheets/v2、sheets/v3）
- `im:message` / `im:message:send_as_bot` — 发送消息
- `contact:user.id:readonly` — 查询用户

> ⚠️ **权限生效前提**：scope 开通后，必须**创建并发布一个包含该 scope 的应用版本**才会真正生效（只开通不发布 = `99991672`）。其中 `drive`、`sheets` 等「敏感权限」在发布后还可能需要**企业管理员审批**，审批通过前调用仍会报 `99991672`（"permission not enabled"）。

## Windows 注意事项

- 必须用 `curl.exe` 且加 `--ssl-no-revoke`（否则报 `CRYPT_E_REVOCATION_OFFLINE`）
- 在 Git Bash（Bash 工具）里执行，避免 PowerShell 中文编码问题
- token 有 2 小时有效期，失效就重新获取

## 核心流程

### Step 1: 获取 tenant_access_token

```bash
TOKEN=$(curl -s --ssl-no-revoke -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"YOUR_APP_ID","app_secret":"YOUR_APP_SECRET"}' \
  | grep -oE '"tenant_access_token":"[^"]*"' | sed 's/"tenant_access_token":"//;s/"//')
echo "$TOKEN" > /tmp/feishu_token.txt   # 缓存，后续命令复用
```

### Step 2: 列出所有知识库（wiki spaces）

```bash
curl -s --ssl-no-revoke -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/wiki/v2/spaces?page_size=50"
```

> 返回的 `items` 里每个 space 有 `space_id` 和 `name`。若 items 为空，说明应用未被授权访问任何知识库——需把应用加为该知识库的管理员/成员。

### Step 3: 列出某个知识库的文件树（顶层节点）

```bash
SPACE_ID=YOUR_SPACE_ID   # 或从 Step 2 得到
curl -s --ssl-no-revoke -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/wiki/v2/spaces/$SPACE_ID/nodes?page_size=50"
```

- 返回的 `items` 里每个节点含：`node_token`、`obj_token`、`obj_type`、`title`、`has_child`、`parent_node_token`。
- `has_child: true` 表示还有子文档，可继续用 `spaces/{space_id}/nodes?parent_node_token={node_token}` 递归展开。
- **权限要求**：`spaces/{id}/nodes` 需要 `wiki:space:retrieve` 且应用是该知识库的**管理员/成员**。若报 `131006 permission denied`，说明应用权限级别不够（只读协作者不够），需在知识库设置里把应用提升为「管理员」。

### Step 4: 读取文档正文（docx）

```bash
# document_id = 节点里的 obj_token（当 obj_type 为 docx 时）
DOC_ID=IoSWdtcmIoJnG2xdXbDczDR7nXf
curl -s --ssl-no-revoke -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_ID/raw_content"
```

- `raw_content` 返回纯文本正文（`data.content` 字段）。
- 需要 `docx:document:readonly` 权限。
- **导出为 markdown 文件时的换行处理**：`data.content` 里的换行是转义后的字面量 `\n`（反斜杠+n），在这个 mingw 环境下 `sed 's/\\n/\n/g'` 和 `perl -pe 's/\\n/\n/g'` **都无效**。必须用 bash 内建 `printf '%b'` 转换（`%b` 会解析 `\n` 等转义序列）：

```bash
# 提取 content 字段 → 转义还原 → 写入 .md 文件
content=$(curl -s --ssl-no-revoke -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_ID/raw_content" \
  | sed -n 's/.*"content":"\([^"]*\)".*/\1/p')
printf '%b' "$content" > /tmp/exported.md
```

### Step 5: 获取节点信息（由节点链接反查）

```bash
# 从 wiki 链接里取 node_token（形如 .../wiki/XXXXX）
curl -s --ssl-no-revoke -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={node_token}"
```

返回节点元信息，含 `obj_token`（用于读正文）、`space_id`、`title`。

### Step 6: 移动节点（整理知识库目录结构）

```bash
# SRC = 要移动的节点的 node_token；DST = 目标父节点的 node_token
curl -s --ssl-no-revoke -X POST \
  "https://open.feishu.cn/open-apis/wiki/v2/spaces/$SPACE_ID/nodes/$SRC/move" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"target_parent_token\":\"$DST\",\"target_space_id\":\"$SPACE_ID\"}"
```

- 需要 `wiki:wiki`（编辑）scope，且应用必须是该知识库的**「可编辑」或「可管理」**角色（仅「可阅读」会报 `131006 no source parent node permission`）。
- 成功返回 `code:0`；移动后原节点的 `parent_node_token` 会变为 `$DST`。

### Step 7: 下载云盘文件（obj_type 为 file）

```bash
# file_token = 节点里的 obj_token（当 obj_type 为 file 时）
curl -s --ssl-no-revoke -L \
  -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/drive/v1/files/$FILE_TOKEN/download" \
  -o /tmp/out.bin    # 按实际扩展名命名，如 out.xlsx / out.pdf
```

- 需要 `drive:drive:readonly` 权限。
- `-L` 跟随重定向（飞书会 302 到真实下载地址）。
- 下载成功返回二进制内容（HTTP 200）；文件大小可用 `ls -l /tmp/out.bin` 或 `wc -c` 确认。

### Step 8: 读取电子表格（obj_type 为 sheet）

```bash
# spreadsheet_token = 节点里的 obj_token（当 obj_type 为 sheet 时）

# (1) 表元信息：标题、sheet 列表
curl -s --ssl-no-revoke -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/$SHEET_TOKEN"

# (2) 子表列表（sheet_id 等）
curl -s --ssl-no-revoke -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/$SHEET_TOKEN/sheets/query"

# (3) 读取单元格值（A1 记法 + 范围）
curl -s --ssl-no-revoke -H "Authorization: Bearer $TOKEN" \
  "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/$SHEET_TOKEN/values/${SHEET_ID}!A1:E11"
```

- 需要 `sheets:spreadsheet:readonly` 权限。
- 注意：元信息/子表列表走 **v3**，单元格值走 **v2**，路径不同别混用。
- 单元格值返回 `data.valueRange.values`（二维数组）。
- 单元格里的**图片/附件不会包含在 values 里**，需要额外的媒体接口单独导出。

## 字段速查

| 字段 | 含义 |
|------|------|
| `space_id` | 知识库 ID |
| `node_token` | wiki 节点 token（用于 get_node / 展开子节点） |
| `obj_token` | 实际文档 token（docx 的 document_id，用于 raw_content） |
| `obj_type` | 节点类型：`docx`（文档）/ `sheet`（电子表格）/ `file`（云盘文件）/ 其他 |
| `has_child` | 是否有子文档 |
| `parent_node_token` | 父节点 token（空字符串 = 顶层节点） |

> `obj_token` 的用途随 `obj_type` 不同而不同：`docx` → 当作 `document_id` 读 `raw_content`；`file` → 当作 `file_token` 下载（drive）；`sheet` → 当作 `spreadsheet_token` 读表（sheets）。

## 错误码速查

| 错误 | 原因 | 解决 |
|------|------|------|
| `99991672` | scope 未开通 / 未发布 / 敏感权限未审批 | 到开放平台开通 scope 并**发布版本**；drive/sheets 等敏感权限需**企业管理员审批** |
| `131006` | 应用非知识库管理员/成员，或权限级别不够 | 知识库设置里把应用提升为「管理员」（移动节点还需「可编辑」+`wiki:wiki`） |
| `CRYPT_E_REVOCATION_OFFLINE` | Windows curl 证书问题 | 加 `--ssl-no-revoke` |

## 附：发送消息（如需要）

```bash
curl -s --ssl-no-revoke -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"receive_id":"YOUR_OPEN_ID","msg_type":"text","content":"{\"text\":\"hello\"}"}'
```
