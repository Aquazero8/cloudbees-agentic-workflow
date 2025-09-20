"""
GitHub API Agent for repository analysis and data retrieval.
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from langchain.tools import BaseTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field


class GitHubRepositoryInfo(BaseModel):
    """Model for GitHub repository information."""
    name: str
    full_name: str
    description: Optional[str]
    language: Optional[str]
    stars: int
    forks: int
    open_issues: int
    last_updated: str
    topics: List[str] = Field(default_factory=list)


class GitHubIssuesInfo(BaseModel):
    """Model for GitHub issues information."""
    total_issues: int
    open_issues: int
    closed_issues: int
    recent_issues: List[Dict[str, Any]] = Field(default_factory=list)


class GitHubAgent:
    """Agent responsible for GitHub API interactions."""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AgenticWorkflowDemo/1.0"
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
    
    async def get_repository_info(self, repo_name: str) -> GitHubRepositoryInfo:
        """Fetch comprehensive repository information."""
        url = f"{self.base_url}/repos/{repo_name}"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return GitHubRepositoryInfo(
                        name=data["name"],
                        full_name=data["full_name"],
                        description=data.get("description"),
                        language=data.get("language"),
                        stars=data["stargazers_count"],
                        forks=data["forks_count"],
                        open_issues=data["open_issues_count"],
                        last_updated=data["updated_at"],
                        topics=data.get("topics", [])
                    )
                else:
                    raise Exception(f"Failed to fetch repository info: {response.status}")
    
    async def get_repository_issues(self, repo_name: str, limit: int = 10) -> GitHubIssuesInfo:
        """Fetch repository issues information."""
        url = f"{self.base_url}/repos/{repo_name}/issues"
        params = {"state": "all", "per_page": limit}
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    issues = await response.json()
                    
                    # Get total counts
                    total_issues = len(issues)
                    open_issues = len([i for i in issues if i["state"] == "open"])
                    closed_issues = total_issues - open_issues
                    
                    # Format recent issues
                    recent_issues = []
                    for issue in issues[:5]:  # Get top 5 recent issues
                        recent_issues.append({
                            "title": issue["title"],
                            "state": issue["state"],
                            "created_at": issue["created_at"],
                            "labels": [label["name"] for label in issue.get("labels", [])]
                        })
                    
                    return GitHubIssuesInfo(
                        total_issues=total_issues,
                        open_issues=open_issues,
                        closed_issues=closed_issues,
                        recent_issues=recent_issues
                    )
                else:
                    raise Exception(f"Failed to fetch issues: {response.status}")
    
    async def search_repositories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for repositories based on query."""
        url = f"{self.base_url}/search/repositories"
        params = {"q": query, "per_page": limit, "sort": "stars"}
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["items"]
                else:
                    raise Exception(f"Failed to search repositories: {response.status}")
    
    def format_repository_summary(self, repo_info: GitHubRepositoryInfo, issues_info: GitHubIssuesInfo) -> str:
        """Format repository information into a readable summary."""
        summary = f"""
## Repository Analysis: {repo_info.full_name}

**Basic Information:**
- Description: {repo_info.description or "No description available"}
- Primary Language: {repo_info.language or "Not specified"}
- Stars: {repo_info.stars:,}
- Forks: {repo_info.forks:,}
- Last Updated: {repo_info.last_updated}

**Issues Overview:**
- Total Issues: {issues_info.total_issues}
- Open Issues: {issues_info.open_issues}
- Closed Issues: {issues_info.closed_issues}

**Recent Issues:**
"""
        
        for issue in issues_info.recent_issues:
            summary += f"- **{issue['title']}** ({issue['state']}) - {issue['created_at']}\n"
            if issue['labels']:
                summary += f"  Labels: {', '.join(issue['labels'])}\n"
        
        if repo_info.topics:
            summary += f"\n**Topics:** {', '.join(repo_info.topics)}\n"
        
        return summary


class GitHubTool(BaseTool):
    """LangChain tool wrapper for GitHub operations."""
    
    name = "github_analyzer"
    description = "Analyze GitHub repositories, fetch issues, and search for repositories"
    github_token: Optional[str] = Field(default=None)
    base_url: str = Field(default="https://api.github.com")
    headers: Dict[str, str] = Field(default_factory=dict)
    
    def __init__(self, github_token: Optional[str] = None):
        super().__init__()
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AgenticWorkflowDemo/1.0"
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
    
    def _run(self, query: str) -> str:
        """Synchronous wrapper for GitHub operations."""
        return asyncio.run(self._arun(query))
    
    async def _arun(self, query: str) -> str:
        """Asynchronous GitHub operations."""
        try:
            # Parse the query to determine operation
            if "repo:" in query.lower():
                # Extract repository name
                repo_name = query.split("repo:")[-1].strip()
                
                # Fetch repository info and issues
                repo_info = await self.get_repository_info(repo_name)
                issues_info = await self.get_repository_issues(repo_name)
                
                return self.format_repository_summary(repo_info, issues_info)
            
            elif "search:" in query.lower():
                # Extract search query
                search_query = query.split("search:")[-1].strip()
                
                # Search repositories
                results = await self.search_repositories(search_query)
                
                summary = f"## Search Results for '{search_query}':\n\n"
                for repo in results:
                    summary += f"- **{repo['full_name']}** ({repo['stargazers_count']} stars)\n"
                    summary += f"  {repo.get('description', 'No description')}\n"
                    summary += f"  Language: {repo.get('language', 'Not specified')}\n\n"
                
                return summary
            
            else:
                return "Please specify either 'repo:repository_name' or 'search:query' in your request."
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def get_repository_info(self, repo_name: str) -> GitHubRepositoryInfo:
        """Fetch comprehensive repository information."""
        url = f"{self.base_url}/repos/{repo_name}"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return GitHubRepositoryInfo(
                        name=data["name"],
                        full_name=data["full_name"],
                        description=data.get("description"),
                        language=data.get("language"),
                        stars=data["stargazers_count"],
                        forks=data["forks_count"],
                        open_issues=data["open_issues_count"],
                        last_updated=data["updated_at"],
                        topics=data.get("topics", [])
                    )
                else:
                    raise Exception(f"Failed to fetch repository info: {response.status}")
    
    async def get_repository_issues(self, repo_name: str, limit: int = 10) -> GitHubIssuesInfo:
        """Fetch repository issues information."""
        url = f"{self.base_url}/repos/{repo_name}/issues"
        params = {"state": "all", "per_page": limit}
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    issues = await response.json()
                    
                    # Get total counts
                    total_issues = len(issues)
                    open_issues = len([i for i in issues if i["state"] == "open"])
                    closed_issues = total_issues - open_issues
                    
                    # Format recent issues
                    recent_issues = []
                    for issue in issues[:5]:  # Get top 5 recent issues
                        recent_issues.append({
                            "title": issue["title"],
                            "state": issue["state"],
                            "created_at": issue["created_at"],
                            "labels": [label["name"] for label in issue.get("labels", [])]
                        })
                    
                    return GitHubIssuesInfo(
                        total_issues=total_issues,
                        open_issues=open_issues,
                        closed_issues=closed_issues,
                        recent_issues=recent_issues
                    )
                else:
                    raise Exception(f"Failed to fetch issues: {response.status}")
    
    async def search_repositories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for repositories based on query."""
        url = f"{self.base_url}/search/repositories"
        params = {"q": query, "per_page": limit, "sort": "stars"}
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["items"]
                else:
                    raise Exception(f"Failed to search repositories: {response.status}")
    
    def format_repository_summary(self, repo_info: GitHubRepositoryInfo, issues_info: GitHubIssuesInfo) -> str:
        """Format repository information into a readable summary."""
        summary = f"""
## Repository Analysis: {repo_info.full_name}

**Basic Information:**
- Description: {repo_info.description or "No description available"}
- Primary Language: {repo_info.language or "Not specified"}
- Stars: {repo_info.stars:,}
- Forks: {repo_info.forks:,}
- Last Updated: {repo_info.last_updated}

**Issues Overview:**
- Total Issues: {issues_info.total_issues}
- Open Issues: {issues_info.open_issues}
- Closed Issues: {issues_info.closed_issues}

**Recent Issues:**
"""
        
        for issue in issues_info.recent_issues:
            summary += f"- **{issue['title']}** ({issue['state']}) - {issue['created_at']}\n"
            if issue['labels']:
                summary += f"  Labels: {', '.join(issue['labels'])}\n"
        
        if repo_info.topics:
            summary += f"\n**Topics:** {', '.join(repo_info.topics)}\n"
        
        return summary
