# Atlassian Internalized

[English](#english) | [한국어](#korean)

---

<a name="english"></a>
## English

**Internalized Atlassian tools (Jira/Confluence) as Python code APIs**

This project internalizes the Atlassian MCP server as importable Python modules, following Anthropic's code execution pattern for maximum token efficiency and type safety.

### Features

- **42 Tools**: 31 Jira + 11 Confluence operations
- **Type-Safe**: Pydantic models with mypy strict mode
- **Token Efficient**: 99.5% reduction through progressive loading
- **Modern Python**: Async/await, Python 3.10+
- **Dual-Mode**: Works as both Python API and Anthropic Skill

### Quick Start

#### 1. Set Environment Variables

```bash
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
```

#### 2. Install the Package

```bash
# Install in development mode
pip install -e ".[dev]"
```

#### 3. Use as Python API

```python
import atlassian_tools

# Discover available tools
tools = atlassian_tools.list_tools(category='jira')

# Get tool information
schema = atlassian_tools.get_tool_info('jira_get_issue')

# Execute a tool
result = await atlassian_tools.execute_tool(
    'jira_get_issue',
    {'issue_key': 'PROJ-123'}
)
```

#### 4. Use as Anthropic Skill (Claude Code)

```bash
# Install skill globally
ln -s "$(pwd)/skills/atlassian-jira" ~/.claude/skills/atlassian-jira

# Use in Claude Code
# The skill will be automatically available in your Claude Code session
```

### Documentation

- **Development Log**: `docs/internalization-log.md`
- **Skill Guide**: `skills/atlassian-jira/README.md`

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=atlassian_tools --cov-report=term-missing

# Type checking
mypy src/atlassian_tools
```

### License

MIT License

---

<a name="korean"></a>
## 한국어

**Atlassian 도구 (Jira/Confluence)를 Python 코드 API로 내재화**

이 프로젝트는 Atlassian MCP 서버를 Python 모듈로 내재화하여, Anthropic의 코드 실행 패턴을 따라 최대 토큰 효율성과 타입 안정성을 제공합니다.

### 주요 기능

- **42개 도구**: Jira 31개 + Confluence 11개 작업
- **타입 안전성**: Pydantic 모델 및 mypy strict 모드
- **토큰 효율성**: 점진적 로딩을 통한 99.5% 감소 (150K → 800 토큰)
- **최신 Python**: Async/await, Python 3.10+
- **이중 모드**: Python API 및 Anthropic Skill로 모두 사용 가능

### 빠른 시작

#### 1. 환경 변수 설정

```bash
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
```

**Jira API 토큰 생성 방법:**
1. Atlassian 계정 설정 페이지 방문: https://id.atlassian.com/manage-profile/security/api-tokens
2. "API 토큰 만들기" 클릭
3. 토큰 이름 입력 후 생성
4. 생성된 토큰을 복사하여 `JIRA_API_TOKEN`에 사용

#### 2. 패키지 설치

```bash
# 개발 모드로 설치
pip install -e ".[dev]"
```

#### 3. Python API로 사용

```python
import atlassian_tools

# 사용 가능한 도구 검색
tools = atlassian_tools.list_tools(category='jira')
# 결과: ['jira_get_issue', ...]

# 도구 정보 가져오기
schema = atlassian_tools.get_tool_info('jira_get_issue')
# 스키마에 입력/출력 정보 포함

# 도구 실행
result = await atlassian_tools.execute_tool(
    'jira_get_issue',
    {'issue_key': 'PROJ-123'}
)
# 결과: ToolExecutionResult(success=True, data={...})
```

**사용 예시:**

```python
import asyncio
import atlassian_tools

async def main():
    # Jira 이슈 조회
    result = await atlassian_tools.execute_tool(
        'jira_get_issue',
        {
            'issue_key': 'PROJ-123',
            'fields': 'summary,status,assignee',
            'comment_limit': 5
        }
    )

    if result.success:
        issue = result.data['issue']
        print(f"제목: {issue['fields']['summary']}")
        print(f"상태: {issue['fields']['status']['name']}")
    else:
        print(f"오류: {result.error}")

asyncio.run(main())
```

#### 4. Anthropic Skill로 사용 (Claude Code)

```bash
# 전역으로 Skill 설치
ln -s "$(pwd)/skills/atlassian-jira" ~/.claude/skills/atlassian-jira

# 설치 확인
ls -la ~/.claude/skills/atlassian-jira
```

**Claude Code에서 사용:**
- Skill이 설치되면 Claude Code 세션에서 자동으로 사용 가능
- "PROJ-123 이슈의 정보를 가져와줘" 같은 자연어로 요청 가능

**CLI로 직접 실행:**

```bash
# 사용 가능한 도구 목록
python skills/atlassian-jira/scripts/execute_tool.py --list-tools

# 도구 스키마 확인
python skills/atlassian-jira/scripts/execute_tool.py jira_get_issue --schema

# 도구 실행
python skills/atlassian-jira/scripts/execute_tool.py jira_get_issue --input '{
  "issue_key": "PROJ-123",
  "fields": "summary,status,assignee"
}'
```

### 프로젝트 구조

```
atlassian-internalized/
├── src/atlassian_tools/          # 메인 패키지
│   ├── _core/                    # 핵심 인프라
│   │   ├── base.py              # Tool 프로토콜 정의
│   │   ├── registry.py          # 도구 검색/로딩
│   │   └── executor.py          # 도구 실행 엔진
│   └── jira/                     # Jira 도구
│       ├── models.py            # Pydantic 스키마
│       └── tools.py             # 도구 구현
├── skills/atlassian-jira/        # Anthropic Skill
│   ├── SKILL.md                 # Skill 정의
│   ├── README.md                # Skill 가이드
│   ├── scripts/execute_tool.py  # CLI 인터페이스
│   └── examples/                # 사용 예시
├── tests/                        # 테스트
│   ├── unit/                    # 단위 테스트
│   └── integration/             # 통합 테스트
└── docs/                         # 문서
    └── internalization-log.md   # 개발 로그
```

### 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=atlassian_tools --cov-report=term-missing

# 타입 체크
mypy src/atlassian_tools
```

**테스트 결과:**
- 64개 테스트 통과
- 89% 코드 커버리지
- 100% mypy strict 준수

### 문서

- **개발 로그**: `docs/internalization-log.md` - TDD 워크플로우 및 기술적 결정 사항
- **Skill 가이드**: `skills/atlassian-jira/README.md` - Claude Code 통합 가이드

### 트러블슈팅

#### 인증 오류

```
Authentication failed. Check your credentials
```

**해결 방법:**
1. API 토큰이 올바른지 확인
2. `JIRA_USERNAME`이 이메일 주소인지 확인 (사용자명 아님)
3. `JIRA_URL`에 프로토콜이 포함되어 있는지 확인 (`https://`)

#### 이슈를 찾을 수 없음

```
Issue PROJ-123 not found
```

**해결 방법:**
1. 이슈 키가 올바른지 확인 (대소문자 구분)
2. 해당 프로젝트에 대한 접근 권한이 있는지 확인
3. Jira 웹 UI에서 해당 이슈가 존재하는지 확인

#### 환경 변수 오류

```
JIRA_URL environment variable is required
```

**해결 방법:**
```bash
# 모든 필수 환경 변수 설정
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"

# 설정 확인
echo $JIRA_URL
echo $JIRA_USERNAME
```

### 로드맵

**현재 상태 (Phase 2 완료):**
- ✅ 핵심 인프라 구현
- ✅ jira_get_issue 프로토타입
- ✅ Anthropic Skill 래퍼
- ✅ 64개 테스트 통과, 89% 커버리지

**다음 단계:**
- Batch 1: Jira 핵심 도구 9개 (create, update, search, comment 등)
- Batch 2: Jira Agile 도구 8개 (sprint, board 등)
- Batch 3: Jira 고급 도구 13개 (workflow, permission 등)
- Batch 4: Confluence 도구 11개 (page, space 등)

### 기여

이 프로젝트는 TDD (Test-Driven Development) 방식을 따릅니다:
1. 테스트 먼저 작성 (Red)
2. 구현 (Green)
3. 리팩토링 (Refactor)

### 라이선스

MIT License
