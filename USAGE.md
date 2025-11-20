# Atlassian Tools Usage Guide

[한국어](#한국어) | [English](#english)

---

## 한국어

### 개요

`atlassian-tools`는 Jira와 Confluence API를 위한 Python 비동기 라이브러리입니다. 서비스 레이어 패턴을 사용하여 깔끔하고 타입 안전한 인터페이스를 제공합니다.

### 설치

```bash
pip install -e .
```

### 환경 설정

`.env` 파일 또는 환경 변수를 설정하세요:

```bash
# Jira 설정
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Confluence 설정
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token
```

### 기본 사용법

#### 도구 목록 조회

```python
import atlassian_tools

# 모든 도구 조회
all_tools = atlassian_tools.list_tools()
print(f"총 {len(all_tools)}개 도구")

# 카테고리별 조회
jira_tools = atlassian_tools.list_tools(category="jira")
confluence_tools = atlassian_tools.list_tools(category="confluence")

# 도구 검색
issue_tools = atlassian_tools.search_tools("issue")
```

#### 도구 정보 조회

```python
info = atlassian_tools.get_tool_info("jira_get_issue")
print(f"이름: {info['name']}")
print(f"설명: {info['description']}")
print(f"입력 스키마: {info['input_schema']}")
```

#### 도구 실행

```python
import asyncio
import atlassian_tools

async def main():
    # Jira 이슈 조회
    result = await atlassian_tools.execute_tool(
        "jira_get_issue",
        {"issue_key": "PROJ-123"}
    )

    if result["success"]:
        issue = result["data"]["issue"]
        print(f"이슈: {issue['summary']}")
        print(f"상태: {issue['status']}")
    else:
        print(f"오류: {result['error']}")

asyncio.run(main())
```

### Jira 도구

| 도구명 | 설명 |
|--------|------|
| `jira_get_issue` | 이슈 상세 조회 |
| `jira_search` | JQL로 이슈 검색 |
| `jira_create_issue` | 이슈 생성 |
| `jira_update_issue` | 이슈 업데이트 |
| `jira_add_comment` | 댓글 추가 |
| `jira_get_transitions` | 전환 목록 조회 |
| `jira_transition_issue` | 이슈 상태 전환 |
| `jira_get_projects` | 프로젝트 목록 조회 |
| `jira_get_user_profile` | 사용자 프로필 조회 |

### Confluence 도구

| 도구명 | 설명 |
|--------|------|
| `confluence_get_page` | 페이지 조회 |
| `confluence_search` | CQL로 검색 |
| `confluence_create_page` | 페이지 생성 |
| `confluence_update_page` | 페이지 업데이트 |
| `confluence_delete_page` | 페이지 삭제 |
| `confluence_get_page_children` | 하위 페이지 조회 |
| `confluence_get_page_ancestors` | 상위 페이지 조회 |
| `confluence_get_labels` | 레이블 조회 |
| `confluence_add_label` | 레이블 추가 |
| `confluence_get_comments` | 댓글 조회 |
| `confluence_add_comment` | 댓글 추가 |

### 예제: JQL 검색

```python
import asyncio
import atlassian_tools

async def search_issues():
    result = await atlassian_tools.execute_tool(
        "jira_search",
        {
            "jql": "project = PROJ AND status = 'In Progress' ORDER BY updated DESC",
            "limit": 20,
            "fields": "summary,status,assignee"
        }
    )

    if result["success"]:
        issues = result["data"]["issues"]
        for issue in issues:
            print(f"{issue['key']}: {issue['summary']}")

asyncio.run(search_issues())
```

### 예제: Confluence 페이지 생성

```python
import asyncio
import atlassian_tools

async def create_page():
    result = await atlassian_tools.execute_tool(
        "confluence_create_page",
        {
            "space_key": "DOCS",
            "title": "새 페이지",
            "body": "<p>페이지 내용입니다.</p>"
        }
    )

    if result["success"]:
        print(f"생성된 페이지 ID: {result['data']['page_id']}")
        print(f"URL: {result['data']['page_url']}")

asyncio.run(create_page())
```

### 에러 처리

모든 도구는 일관된 응답 형식을 반환합니다:

```python
result = await atlassian_tools.execute_tool("jira_get_issue", {"issue_key": "INVALID"})

# result 구조:
# {
#     "success": True/False,  # 실행 성공 여부
#     "data": {               # 도구 결과
#         "success": True/False,  # 도구 내부 성공 여부
#         "issue": {...},         # 성공 시 데이터
#         "error": "..."          # 실패 시 에러 메시지
#     },
#     "error": "...",         # 실행 레벨 에러
#     "tool_name": "..."
# }
```

---

## English

### Overview

`atlassian-tools` is an async Python library for Jira and Confluence APIs. It uses a service layer pattern to provide a clean, type-safe interface.

### Installation

```bash
pip install -e .
```

### Configuration

Set up your `.env` file or environment variables:

```bash
# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Confluence Configuration
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token
```

### Basic Usage

#### List Available Tools

```python
import atlassian_tools

# List all tools
all_tools = atlassian_tools.list_tools()
print(f"Total {len(all_tools)} tools")

# List by category
jira_tools = atlassian_tools.list_tools(category="jira")
confluence_tools = atlassian_tools.list_tools(category="confluence")

# Search tools
issue_tools = atlassian_tools.search_tools("issue")
```

#### Get Tool Information

```python
info = atlassian_tools.get_tool_info("jira_get_issue")
print(f"Name: {info['name']}")
print(f"Description: {info['description']}")
print(f"Input Schema: {info['input_schema']}")
```

#### Execute a Tool

```python
import asyncio
import atlassian_tools

async def main():
    # Get a Jira issue
    result = await atlassian_tools.execute_tool(
        "jira_get_issue",
        {"issue_key": "PROJ-123"}
    )

    if result["success"]:
        issue = result["data"]["issue"]
        print(f"Issue: {issue['summary']}")
        print(f"Status: {issue['status']}")
    else:
        print(f"Error: {result['error']}")

asyncio.run(main())
```

### Jira Tools

| Tool Name | Description |
|-----------|-------------|
| `jira_get_issue` | Get issue details |
| `jira_search` | Search issues with JQL |
| `jira_create_issue` | Create a new issue |
| `jira_update_issue` | Update an existing issue |
| `jira_add_comment` | Add a comment to an issue |
| `jira_get_transitions` | Get available transitions |
| `jira_transition_issue` | Transition issue status |
| `jira_get_projects` | List all projects |
| `jira_get_user_profile` | Get current user profile |

### Confluence Tools

| Tool Name | Description |
|-----------|-------------|
| `confluence_get_page` | Get a page by ID |
| `confluence_search` | Search with CQL |
| `confluence_create_page` | Create a new page |
| `confluence_update_page` | Update a page |
| `confluence_delete_page` | Delete a page |
| `confluence_get_page_children` | Get child pages |
| `confluence_get_page_ancestors` | Get ancestor pages |
| `confluence_get_labels` | Get page labels |
| `confluence_add_label` | Add a label |
| `confluence_get_comments` | Get page comments |
| `confluence_add_comment` | Add a comment |

### Example: JQL Search

```python
import asyncio
import atlassian_tools

async def search_issues():
    result = await atlassian_tools.execute_tool(
        "jira_search",
        {
            "jql": "project = PROJ AND status = 'In Progress' ORDER BY updated DESC",
            "limit": 20,
            "fields": "summary,status,assignee"
        }
    )

    if result["success"]:
        issues = result["data"]["issues"]
        for issue in issues:
            print(f"{issue['key']}: {issue['summary']}")

asyncio.run(search_issues())
```

### Example: Create Confluence Page

```python
import asyncio
import atlassian_tools

async def create_page():
    result = await atlassian_tools.execute_tool(
        "confluence_create_page",
        {
            "space_key": "DOCS",
            "title": "New Page",
            "body": "<p>Page content goes here.</p>"
        }
    )

    if result["success"]:
        print(f"Created page ID: {result['data']['page_id']}")
        print(f"URL: {result['data']['page_url']}")

asyncio.run(create_page())
```

### Error Handling

All tools return a consistent response format:

```python
result = await atlassian_tools.execute_tool("jira_get_issue", {"issue_key": "INVALID"})

# result structure:
# {
#     "success": True/False,  # Execution success
#     "data": {               # Tool result
#         "success": True/False,  # Tool-level success
#         "issue": {...},         # Data on success
#         "error": "..."          # Error message on failure
#     },
#     "error": "...",         # Execution-level error
#     "tool_name": "..."
# }
```

### Architecture

```
atlassian_tools/
├── _core/
│   ├── config.py        # Configuration management (pydantic-settings)
│   ├── exceptions.py    # Typed exception hierarchy
│   ├── http_client.py   # Async HTTP client (httpx)
│   ├── container.py     # Service container / DI
│   ├── registry.py      # Tool registry
│   └── executor.py      # Tool executor
├── jira/
│   ├── service.py       # Jira business logic
│   ├── models.py        # Input/Output schemas
│   └── tools.py         # Tool implementations
└── confluence/
    ├── service.py       # Confluence business logic
    ├── models.py        # Input/Output schemas
    └── tools.py         # Tool implementations
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=atlassian_tools

# Run specific category
pytest tests/unit/jira/
pytest tests/integration/
```
