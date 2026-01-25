# AI 代码审查回写 PR 评论区

## 目标
实现 AI 自动代码审查，并将审查结果回写到 PR 评论区。

## 背景
在 PR 创建后，自动触发 AI 代码审查，将审查结果以评论形式添加到 PR 中，帮助开发者及时发现代码问题。

## 验收标准
- [x] 支持根据配置的 `git_provider` 自动识别并使用对应平台的 API
- [x] 支持 GitHub 和 Gitee 两个平台
- [x] 审查维度：代码质量、安全性、类型检查、规范遵从
- [x] 审查结果以评论形式回写到 PR
- [x] 支持配置审查结果的展示格式

## 实现方案

### 1. 代码结构
```
cortex-backend/cli/
├── ai/
│   ├── __init__.py
│   ├── service.py              # AI 服务基类
│   └── code_reviewer.py        # AI 代码审查器
└── providers/
    ├── __init__.py
    ├── base.py                 # Git Provider 基类
    ├── github.py               # GitHub Provider
    ├── gitlab.py               # GitLab Provider
    └── pr_comment/
        ├── __init__.py
        ├── base.py             # PR Comment Provider 基类
        ├── github.py           # GitHub PR 评论实现
        └── gitee.py            # Gitee PR 评论实现
```

### 2. Provider 接口

#### PRCommentProvider 基类
```python
class PRCommentProvider(ABC):
    """PR 评论 Provider 抽象基类"""

    def create_review_comment(self, pr_number: int, body: str,
                               path: Optional[str] = None,
                               line: Optional[int] = None) -> str:
        """创建 PR 评论"""

    def create_review_comments_batch(self, pr_number: int,
                                      comments: List[ReviewComment]) -> List[str]:
        """批量创建评论"""

    def delete_comment(self, comment_id: str) -> bool:
        """删除评论"""
```

#### ReviewComment 数据类
```python
@dataclass
class ReviewComment:
    path: str           # 文件路径
    line: int           # 行号
    body: str           # 评论内容
    severity: str       # info, warning, error
```

### 3. 配置项
```python
# 在 ~/.cortex/config.json 中配置
{
    "ai_review_enabled": true,
    "ai_review_dimensions": ["quality", "security", "type", "convention"],
    "git_provider": "github",  # github | gitlab
    "github_token": "xxx",
    "gitlab_token": "xxx"
}
```

### 4. 使用方式

#### CLI 命令
```bash
# 审查 PR #4（不发布到 PR）
ctx review 4

# 审查 PR #4 并发布到 PR 评论区
ctx review 4 --publish

# 查看/配置 AI 审查设置
ctx review-config --show
ctx review-config --enable
ctx review-config --disable
```

#### 审查结果示例
```
评分: 85/100

| 文件 | 行号 | 问题 | 类别 | 严重程度 |
|------|------|------|------|----------|
| cli/main.py | 15 | 未使用的导入 | quality | info |

✅ 已发布 3 条审查评论到 PR #4
```

## 依赖
- PyGithub - GitHub API 客户端
- requests - Gitee API 调用
- OpenAI/Anthropic SDK - AI 服务

## 任务拆分
1. [x] 创建代码审查分析器 (`cli/ai/code_reviewer.py`)
2. [x] 实现 GitHub PR 评论 provider (`cli/providers/pr_comment/github.py`)
3. [x] 实现 Gitee PR 评论 provider (`cli/providers/pr_comment/gitee.py`)
4. [x] 添加配置项 (`cli/config.py`)
5. [x] 添加 CLI 命令 (`cli/commands/review.py`)
6. [ ] 集成到 ctx hooks（可选，后续迭代）
