import json
from pathlib import Path

from pydantic import Field, BaseModel, ConfigDict


class GiteaUser(BaseModel):
    id: int = Field(..., description="User ID", examples=[751])
    login: str = Field(..., description="Login username", examples=["srv_dvc_tma001"])
    login_name: str = Field(..., description="Login name", examples=[""])
    source_id: int = Field(..., description="Source ID", examples=[0])
    full_name: str = Field(..., description="Full name", examples=["dvc_tma"])
    email: str = Field(..., description="Email address", examples=["srv_dvc_tma001@mediatek.com"])
    avatar_url: str = Field(
        ...,
        description="Avatar URL",
        examples=["https://gitea.mediatek.inc/avatars/98c40407bd1ff511262c4ef2bd0ac81e"],
    )
    html_url: str = Field(
        ..., description="HTML URL", examples=["https://gitea.mediatek.inc/srv_dvc_tma001"]
    )
    language: str = Field(..., description="Language", examples=[""])
    is_admin: bool = Field(..., description="Is admin", examples=[False])
    last_login: str = Field(..., description="Last login time", examples=["0001-01-01T00:00:00Z"])
    created: str = Field(..., description="Creation time", examples=["2025-03-26T04:07:34Z"])
    restricted: bool = Field(..., description="Is restricted", examples=[False])
    active: bool = Field(..., description="Is active", examples=[False])
    prohibit_login: bool = Field(..., description="Prohibit login", examples=[False])
    location: str = Field(..., description="Location", examples=[""])
    website: str = Field(..., description="Website", examples=[""])
    description: str = Field(..., description="Description", examples=[""])
    visibility: str = Field(..., description="Visibility", examples=["public"])
    followers_count: int = Field(..., description="Followers count", examples=[0])
    following_count: int = Field(..., description="Following count", examples=[0])
    starred_repos_count: int = Field(..., description="Starred repos count", examples=[0])
    username: str = Field(..., description="Username", examples=["srv_dvc_tma001"])


class GiteaLabel(BaseModel):
    id: int = Field(..., description="Label ID", examples=[2198])
    name: str = Field(..., description="Label name", examples=["Priority/Low"])
    exclusive: bool = Field(..., description="Is exclusive", examples=[True])
    is_archived: bool = Field(..., description="Is archived", examples=[False])
    color: str = Field(..., description="Color", examples=["4caf50"])
    description: str = Field(..., description="Description", examples=["The priority is low"])
    url: str = Field(
        ...,
        description="URL",
        examples=["https://gitea.mediatek.inc/api/v1/orgs/MCTS_research/labels/2198"],
    )


class GiteaPermissions(BaseModel):
    admin: bool = Field(..., description="Admin permission", examples=[True])
    push: bool = Field(..., description="Push permission", examples=[True])
    pull: bool = Field(..., description="Pull permission", examples=[True])


class GiteaInternalTracker(BaseModel):
    enable_time_tracker: bool = Field(..., description="Enable time tracker", examples=[True])
    allow_only_contributors_to_track_time: bool = Field(
        ..., description="Allow only contributors to track time", examples=[True]
    )
    enable_issue_dependencies: bool = Field(
        ..., description="Enable issue dependencies", examples=[True]
    )


class GiteaExternalWiki(BaseModel):
    external_wiki_url: str = Field(
        ..., description="External wiki URL", examples=["https://tma.mediatek.inc/docs"]
    )


class GiteaIssuePullRequest(BaseModel):
    """Simplified pull request info within issue context."""

    merged: bool = Field(..., description="Is merged", examples=[False])
    merged_at: str | None = Field(..., description="Merged at", examples=[None])
    draft: bool = Field(..., description="Is draft", examples=[False])
    html_url: str = Field(
        ...,
        description="HTML URL",
        examples=["https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk/pulls/14"],
    )


class GiteaRepository(BaseModel):
    id: int = Field(..., description="Repository ID", examples=[1478])
    name: str = Field(..., description="Repository name", examples=["mtkllm_sdk"])
    owner: GiteaUser | str = Field(
        ..., description="Repository owner object", examples=["MCTS_research"]
    )
    full_name: str = Field(..., description="Full name", examples=["MCTS_research/mtkllm_sdk"])
    description: str = Field(default="", description="Repository description", examples=[""])
    empty: bool = Field(default=False, description="Is empty repository", examples=[False])
    private: bool = Field(default=False, description="Is private repository", examples=[False])
    fork: bool = Field(default=False, description="Is fork", examples=[False])
    template: bool = Field(default=False, description="Is template", examples=[False])
    mirror: bool = Field(default=False, description="Is mirror", examples=[False])
    size: int = Field(default=0, description="Repository size", examples=[26551])
    language: str = Field(default="", description="Primary language", examples=[""])
    languages_url: str = Field(
        default="",
        description="Languages API URL",
        examples=["https://gitea.mediatek.inc/api/v1/repos/MCTS_research/mtkllm_sdk/languages"],
    )
    html_url: str = Field(
        default="",
        description="HTML URL",
        examples=["https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk"],
    )
    url: str = Field(
        default="",
        description="API URL",
        examples=["https://gitea.mediatek.inc/api/v1/repos/MCTS_research/mtkllm_sdk"],
    )
    link: str = Field(default="", description="Link", examples=[""])
    ssh_url: str = Field(
        default="",
        description="SSH URL",
        examples=["git@git.mediatek.inc:MCTS_research/mtkllm_sdk.git"],
    )
    clone_url: str = Field(
        default="",
        description="Clone URL",
        examples=["https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk.git"],
    )
    original_url: str = Field(default="", description="Original URL", examples=[""])
    website: str = Field(
        default="", description="Website", examples=["https://tma.mediatek.inc/docs"]
    )
    stars_count: int = Field(default=0, description="Stars count", examples=[0])
    forks_count: int = Field(default=0, description="Forks count", examples=[0])
    watchers_count: int = Field(default=0, description="Watchers count", examples=[10])
    open_issues_count: int = Field(default=0, description="Open issues count", examples=[2])
    open_pr_counter: int = Field(default=0, description="Open PR counter", examples=[1])
    release_counter: int = Field(default=0, description="Release counter", examples=[24])
    default_branch: str = Field(
        default="master", description="Default branch", examples=["master"]
    )
    archived: bool = Field(default=False, description="Is archived", examples=[False])
    created_at: str = Field(
        default="", description="Created at", examples=["2024-11-06T07:31:03Z"]
    )
    updated_at: str = Field(
        default="", description="Updated at", examples=["2025-09-16T07:27:38Z"]
    )
    archived_at: str = Field(
        default="1970-01-01T00:00:00Z",
        description="Archived at",
        examples=["1970-01-01T00:00:00Z"],
    )
    permissions: GiteaPermissions | None = Field(
        default=None, description="Repository permissions"
    )
    has_issues: bool = Field(default=True, description="Has issues", examples=[True])
    internal_tracker: GiteaInternalTracker | None = Field(
        default=None, description="Internal tracker settings"
    )
    has_wiki: bool = Field(default=True, description="Has wiki", examples=[True])
    external_wiki: GiteaExternalWiki | None = Field(
        default=None, description="External wiki settings"
    )
    has_pull_requests: bool = Field(default=True, description="Has pull requests", examples=[True])
    has_projects: bool = Field(default=False, description="Has projects", examples=[False])
    projects_mode: str = Field(default="all", description="Projects mode", examples=["all"])
    has_releases: bool = Field(default=True, description="Has releases", examples=[True])
    has_packages: bool = Field(default=True, description="Has packages", examples=[True])
    has_actions: bool = Field(default=True, description="Has actions", examples=[True])
    ignore_whitespace_conflicts: bool = Field(
        default=True, description="Ignore whitespace conflicts", examples=[True]
    )
    allow_merge_commits: bool = Field(
        default=True, description="Allow merge commits", examples=[True]
    )
    allow_rebase: bool = Field(default=True, description="Allow rebase", examples=[True])
    allow_rebase_explicit: bool = Field(
        default=True, description="Allow rebase explicit", examples=[True]
    )
    allow_squash_merge: bool = Field(
        default=True, description="Allow squash merge", examples=[True]
    )
    allow_fast_forward_only_merge: bool = Field(
        default=True, description="Allow fast forward only merge", examples=[True]
    )
    allow_rebase_update: bool = Field(
        default=True, description="Allow rebase update", examples=[True]
    )
    default_delete_branch_after_merge: bool = Field(
        default=True, description="Default delete branch after merge", examples=[True]
    )
    default_merge_style: str = Field(
        default="squash", description="Default merge style", examples=["squash"]
    )
    default_allow_maintainer_edit: bool = Field(
        default=True, description="Default allow maintainer edit", examples=[True]
    )
    avatar_url: str = Field(default="", description="Avatar URL", examples=[""])
    internal: bool = Field(default=True, description="Is internal", examples=[True])
    mirror_interval: str = Field(default="", description="Mirror interval", examples=[""])
    object_format_name: str = Field(
        default="sha1", description="Object format name", examples=["sha1"]
    )
    mirror_updated: str = Field(
        default="0001-01-01T00:00:00Z",
        description="Mirror updated",
        examples=["0001-01-01T00:00:00Z"],
    )
    topics: list[str] = Field(default_factory=list, description="Topics", examples=[[]])
    licenses: list[str] = Field(default_factory=list, description="Licenses", examples=[["MIT"]])


class GiteaBranch(BaseModel):
    label: str = Field(..., description="Branch label", examples=["master"])
    ref: str = Field(..., description="Branch ref", examples=["master"])
    sha: str = Field(
        ..., description="Branch SHA", examples=["55e1ecd483b8a4ea878f72cadadc0531c7b1df34"]
    )
    repo_id: int = Field(..., description="Repository ID", examples=[1478])
    repo: GiteaRepository


class GiteaIssue(BaseModel):
    id: int = Field(..., description="Issue ID", examples=[76942])
    url: str = Field(
        ...,
        description="URL",
        examples=["https://gitea.mediatek.inc/api/v1/repos/MCTS_research/mtkllm_sdk/issues/14"],
    )
    html_url: str = Field(
        ...,
        description="HTML URL",
        examples=["https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk/pulls/14"],
    )
    number: int = Field(..., description="Number", examples=[14])
    user: GiteaUser = Field(..., description="User")
    original_author: str = Field(..., description="Original author", examples=[""])
    original_author_id: int = Field(..., description="Original author ID", examples=[0])
    title: str = Field(..., description="Title", examples=["chore: Update pre-commit hooks"])
    body: str = Field(
        ...,
        description="Body",
        examples=["Update versions of pre-commit hooks to latest version."],
    )
    ref: str = Field(..., description="Ref", examples=[""])
    assets: list = Field(..., description="Assets", examples=[[]])
    labels: list[GiteaLabel] = Field(..., description="Labels", examples=[[]])
    assignee: GiteaUser | None = Field(..., description="Assignee")
    assignees: list[GiteaUser] = Field(..., description="Assignees", examples=[[]])
    state: str = Field(..., description="State", examples=["open"])
    is_locked: bool = Field(..., description="Is locked", examples=[False])
    comments: int = Field(..., description="Comments count", examples=[6])
    created_at: str = Field(..., description="Created at", examples=["2025-09-13T00:03:51Z"])
    updated_at: str = Field(..., description="Updated at", examples=["2025-09-16T08:35:15Z"])
    closed_at: str | None = Field(..., description="Closed at", examples=[None])
    due_date: str | None = Field(..., description="Due date", examples=[None])
    pull_request: GiteaIssuePullRequest | None = Field(..., description="Pull request info")
    repository: GiteaRepository = Field(..., description="Repository (summary)")
    pin_order: int = Field(..., description="Pin order", examples=[0])


class GiteaPullRequest(BaseModel):
    id: int = Field(..., description="Pull request ID", examples=[72637])
    url: str = Field(
        ...,
        description="URL",
        examples=["https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk/pulls/14"],
    )
    number: int = Field(..., description="Number", examples=[14])
    user: GiteaUser = Field(..., description="User")
    title: str = Field(..., description="Title", examples=["chore: Update pre-commit hooks"])
    body: str = Field(
        ...,
        description="Body",
        examples=["Update versions of pre-commit hooks to latest version."],
    )
    labels: list[GiteaLabel] = Field(..., description="Labels", examples=[[]])
    assignee: GiteaUser | None = Field(..., description="Assignee")
    assignees: list[GiteaUser] = Field(..., description="Assignees", examples=[[]])
    requested_reviewers: list[GiteaUser] = Field(
        ..., description="Requested reviewers", examples=[[]]
    )
    requested_reviewers_teams: list = Field(
        ..., description="Requested reviewers teams", examples=[[]]
    )
    state: str = Field(..., description="State", examples=["open"])
    draft: bool = Field(..., description="Is draft", examples=[False])
    is_locked: bool = Field(..., description="Is locked", examples=[False])
    comments: int = Field(..., description="Comments count", examples=[6])
    additions: int = Field(..., description="Additions", examples=[1])
    deletions: int = Field(..., description="Deletions", examples=[1])
    changed_files: int = Field(..., description="Changed files", examples=[1])
    html_url: str = Field(
        ...,
        description="HTML URL",
        examples=["https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk/pulls/14"],
    )
    diff_url: str = Field(
        ...,
        description="Diff URL",
        examples=["https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk/pulls/14.diff"],
    )
    patch_url: str = Field(
        ...,
        description="Patch URL",
        examples=["https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk/pulls/14.patch"],
    )
    mergeable: bool = Field(..., description="Is mergeable", examples=[True])
    merged: bool = Field(..., description="Is merged", examples=[False])
    merged_at: str | None = Field(..., description="Merged at", examples=[None])
    merge_commit_sha: str | None = Field(..., description="Merge commit SHA", examples=[None])
    merged_by: GiteaUser | None = Field(..., description="Merged by", examples=[None])
    allow_maintainer_edit: bool = Field(..., description="Allow maintainer edit", examples=[False])
    base: GiteaBranch = Field(..., description="Base branch")
    head: GiteaBranch = Field(..., description="Head branch")
    merge_base: str = Field(
        ..., description="Merge base", examples=["55e1ecd483b8a4ea878f72cadadc0531c7b1df34"]
    )
    due_date: str | None = Field(..., description="Due date", examples=[None])
    created_at: str = Field(..., description="Created at", examples=["2025-09-13T00:03:51Z"])
    updated_at: str = Field(..., description="Updated at", examples=["2025-09-16T08:35:15Z"])
    closed_at: str | None = Field(..., description="Closed at", examples=[None])
    pin_order: int = Field(..., description="Pin order", examples=[0])


class GiteaComment(BaseModel):
    id: int = Field(..., description="Comment ID", examples=[1177058])
    html_url: str = Field(
        ...,
        description="HTML URL",
        examples=[
            "https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk/pulls/14#issuecomment-1177058"
        ],
    )
    pull_request_url: str = Field(
        ...,
        description="Pull request URL",
        examples=["https://gitea.mediatek.inc/MCTS_research/mtkllm_sdk/pulls/14"],
    )
    issue_url: str = Field(..., description="Issue URL", examples=[""])
    user: GiteaUser = Field(..., description="GiteaUser")
    original_author: str = Field(..., description="Original author", examples=[""])
    original_author_id: int = Field(..., description="Original author ID", examples=[0])
    body: str = Field(
        ...,
        description="Body",
        examples=[
            "@DS906659 看一下\r\n![image.png](/attachments/85a5b961-0bf1-4080-a5d1-364e6945ccdc)"
        ],
    )
    assets: list = Field(..., description="Assets", examples=[[]])
    created_at: str = Field(..., description="Created at", examples=["2025-09-16T08:35:15Z"])
    updated_at: str = Field(..., description="Updated at", examples=["2025-09-16T08:35:15Z"])


class GiteaWebhookPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    action: str | None = Field(default=None, description="Action type", examples=["created"])
    issue: GiteaIssue | None = Field(default=None, description="Issue object")
    pull_request: GiteaPullRequest | None = Field(default=None, description="Pull request object")
    comment: GiteaComment | None = Field(default=None, description="Comment object")
    repository: GiteaRepository = Field(..., description="Repository object")
    sender: GiteaUser = Field(..., description="Sender user")
    is_pull: bool = Field(default=False, description="Is pull request", examples=[True])

    def save(self, filename: str) -> None:
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.model_dump(exclude_unset=True, exclude_defaults=True), f, indent=4)
