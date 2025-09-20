"""
Basic demo that runs without OpenAI API key - shows GitHub agent functionality.
"""
import asyncio
from agents.github_agent import GitHubAgent


async def basic_github_demo():
    """Run a basic demonstration of the GitHub agent."""
    
    print("🌟 Basic Agentic Workflow Demo (GitHub Agent Only)")
    print("=" * 55)
    print("This demo shows the GitHub agent functionality without requiring OpenAI API key.")
    print()
    
    # Initialize GitHub agent
    github_agent = GitHubAgent()
    
    print("📊 Demo 1: Repository Analysis")
    print("-" * 30)
    
    try:
        # Get repository info for a popular repository
        repo_name = "microsoft/vscode"
        print(f"Analyzing repository: {repo_name}")
        
        # Fetch repository information
        repo_info = await github_agent.get_repository_info(repo_name)
        issues_info = await github_agent.get_repository_issues(repo_name, limit=5)
        
        # Format and display results
        summary = github_agent.format_repository_summary(repo_info, issues_info)
        print(summary)
        
    except Exception as e:
        print(f"❌ Error analyzing repository: {e}")
        print("This might be due to GitHub API rate limits or network issues.")
    
    print("\n🔍 Demo 2: Repository Search")
    print("-" * 30)
    
    try:
        # Search for repositories
        search_query = "python web framework"
        print(f"Searching for: {search_query}")
        
        results = await github_agent.search_repositories(search_query, limit=3)
        
        print(f"\nFound {len(results)} repositories:")
        for i, repo in enumerate(results, 1):
            print(f"\n{i}. {repo['full_name']}")
            print(f"   Stars: {repo['stargazers_count']:,}")
            print(f"   Language: {repo.get('language', 'Not specified')}")
            print(f"   Description: {repo.get('description', 'No description')[:100]}...")
        
    except Exception as e:
        print(f"❌ Error searching repositories: {e}")
        print("This might be due to GitHub API rate limits or network issues.")
    
    print("\n🎉 Basic Demo Complete!")
    print("=" * 55)
    print("\nTo run the full demo with reasoning and analysis, you'll need:")
    print("1. An OpenAI API key (get one at https://platform.openai.com/)")
    print("2. Set the environment variable: OPENAI_API_KEY=your_key_here")
    print("3. Then run: python main.py")


if __name__ == "__main__":
    asyncio.run(basic_github_demo())
