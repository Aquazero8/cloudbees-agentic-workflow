"""
CloudBees Agentic Workflow Demo - Correct Issue Counting
Uses the proper GitHub API approach to get accurate issue counts.
"""
import asyncio
import json
from agents.github_agent import GitHubTool
from agents.documentation_agent import DocumentationTool
from agents.reasoning_agent import ReasoningTool
from config import Config

async def get_correct_repo_analysis(repo_name: str):
    """Get correct repository analysis with accurate issue counts."""
    
    github_tool = GitHubTool()
    
    # Get repository basic info
    repo_info = await github_tool.get_repository_info(repo_name)
    
    # Get accurate issue counts using separate API calls
    issues_info = await get_accurate_issue_counts(repo_name, github_tool)
    
    # Try to get README content with meaningful extraction
    readme_content = None
    try:
        doc_tool = DocumentationTool()
        readme_url = f"https://raw.githubusercontent.com/{repo_name}/main/README.md"
        readme_result = await doc_tool._arun(f"Fetch and analyze content from {readme_url}")
        
        # Extract meaningful content instead of raw analysis
        if hasattr(doc_tool, 'agent') and doc_tool.agent:
            # For README.md files, extract meaningful content
            lines = readme_result.split('\n')
            meaningful_content = []
            
            # Look for key sections that developers care about
            current_section = None
            for line in lines[:50]:  # First 50 lines
                line = line.strip()
                if line.startswith('#'):
                    current_section = line.lower()
                elif line and len(line) > 30:
                    # Clean up HTML and markdown syntax
                    clean_line = line
                    # Remove HTML tags
                    import re
                    clean_line = re.sub(r'<[^>]+>', '', clean_line)
                    # Remove markdown links but keep text
                    clean_line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_line)
                    # Remove extra whitespace
                    clean_line = ' '.join(clean_line.split())
                    
                    if clean_line and len(clean_line) > 20:
                        # Extract content from important sections
                        if any(keyword in current_section for keyword in ['description', 'overview', 'about', 'what', 'introduction']):
                            meaningful_content.append(f"**Description**: {clean_line}")
                        elif any(keyword in current_section for keyword in ['install', 'setup', 'getting started']):
                            meaningful_content.append(f"**Installation**: {clean_line}")
                        elif any(keyword in current_section for keyword in ['usage', 'example', 'demo', 'quick start']):
                            meaningful_content.append(f"**Usage**: {clean_line}")
                        elif len(meaningful_content) < 3:  # Get first 3 meaningful pieces
                            meaningful_content.append(f"**Content**: {clean_line}")
            
            if meaningful_content:
                readme_content = '\n\n'.join(meaningful_content)
            else:
                # Fallback: get first meaningful paragraph
                for line in lines[:20]:
                    line = line.strip()
                    if line and len(line) > 50 and not line.startswith('#'):
                        # Clean up the line
                        clean_line = re.sub(r'<[^>]+>', '', line)
                        clean_line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_line)
                        clean_line = ' '.join(clean_line.split())
                        if clean_line:
                            readme_content = clean_line
                            break
                else:
                    readme_content = "README content extracted but no meaningful content found"
        else:
            readme_content = readme_result
    except Exception as e:
        readme_content = "README not available"
    
    # Create accurate summary
    summary = f"""
## Repository Analysis: {repo_info.full_name}

### Basic Information
- **Description**: {repo_info.description or "No description available"}
- **Primary Language**: {repo_info.language or "Not specified"}
- **Stars**: {repo_info.stars:,}
- **Forks**: {repo_info.forks:,}
- **Last Updated**: {repo_info.last_updated}

### Issues Overview (Correct Counts)
- **Open Issues**: {issues_info['open_issues']} (from GitHub API)
- **Closed Issues**: {issues_info['closed_issues']} (from GitHub API)
- **Total Issues**: {issues_info['total_issues']} (from GitHub API)
- **Recent Issues Sample**: {len(issues_info['recent_issues'])} issues shown below

### Recent Issues
"""
    
    for issue in issues_info['recent_issues']:
        summary += f"- **{issue['title']}** ({issue['state']}) - {issue['created_at']}\n"
        if issue['labels']:
            summary += f"  Labels: {', '.join(issue['labels'])}\n"
    
    # Add Major/Critical Issues section only if there are issues
    if issues_info['open_issues'] > 0:
        summary += f"\n### Major/Critical Issues\n"
        
        # Analyze recent issues to identify important ones
        important_issues = []
        for issue in issues_info['recent_issues']:
            title_lower = issue['title'].lower()
            # Identify important issues based on keywords and patterns
            if any(keyword in title_lower for keyword in ['bug', 'error', 'crash', 'broken', 'not working', 'fails', 'issue']):
                important_issues.append(f"**Bug**: {issue['title']} - Affects core functionality")
            elif any(keyword in title_lower for keyword in ['security', 'vulnerability', 'exploit', 'attack']):
                important_issues.append(f"**Security**: {issue['title']} - Potential security vulnerability")
            elif any(keyword in title_lower for keyword in ['performance', 'slow', 'memory', 'cpu', 'optimization']):
                important_issues.append(f"**Performance**: {issue['title']} - Performance optimization needed")
            elif any(keyword in title_lower for keyword in ['documentation', 'doc', 'readme', 'tutorial', 'guide']):
                important_issues.append(f"**Documentation**: {issue['title']} - Documentation improvement needed")
            elif any(keyword in title_lower for keyword in ['feature', 'enhancement', 'improvement', 'request']):
                important_issues.append(f"**Feature Request**: {issue['title']} - New functionality requested")
            elif any(keyword in title_lower for keyword in ['how to', 'question', 'help', 'support']):
                important_issues.append(f"**Support**: {issue['title']} - User needs assistance")
        
        if important_issues:
            for issue in important_issues[:5]:  # Show top 5 important issues
                summary += f"- {issue}\n"
        else:
            # If no specific important issues found, show the most recent issues as important
            summary += f"- **Recent Important Issues**:\n"
            for issue in issues_info['recent_issues'][:3]:  # Show top 3 recent issues
                summary += f"  - {issue['title']}\n"
            summary += f"- **Overall**: {issues_info['open_issues']} open issues may indicate maintenance challenges\n"
    
    if repo_info.topics:
        summary += f"\n### Topics\n{', '.join(repo_info.topics)}\n"
    
    # Add README content if available (simplified)
    if readme_content and readme_content != "README not available":
        # Clean up the content for better readability
        clean_content = readme_content.replace("**Content**: ", "").replace("**Description**: ", "").replace("**Installation**: ", "").replace("**Usage**: ", "")
        # Remove duplicate lines and clean up
        lines = clean_content.split('\n')
        unique_lines = []
        for line in lines:
            line = line.strip()
            if line and line not in unique_lines and len(line) > 20:
                unique_lines.append(line)
        
        if unique_lines:
            summary += f"\n### Key Information\n"
            meaningful_count = 0
            for line in unique_lines:
                # Clean up the line to remove HTML and make it readable
                clean_line = re.sub(r'<[^>]+>', '', line)
                clean_line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_line)
                clean_line = ' '.join(clean_line.split())
                
                # Only include lines that are meaningful and not HTML artifacts
                if (clean_line and len(clean_line) > 30 and 
                    not clean_line.startswith('**') and 
                    not any(tag in line.lower() for tag in ['img src=', 'alt=', 'colab.research.google.com'])):
                    summary += f"- {clean_line}\n"
                    meaningful_count += 1
                    if meaningful_count >= 3:  # Limit to 3 meaningful lines
                        break
    
    return summary, readme_content

async def get_accurate_issue_counts(repo_name: str, github_tool):
    """Get accurate issue counts using proper GitHub API calls."""
    
    import aiohttp
    
    # Use the search API to get accurate counts
    # This is more reliable than the issues endpoint for counts
    
    async with aiohttp.ClientSession(headers=github_tool.headers) as session:
        # Get open issues count
        open_url = f"{github_tool.base_url}/search/issues"
        open_params = {
            "q": f"repo:{repo_name} type:issue state:open",
            "per_page": 1  # We only need the count
        }
        
        async with session.get(open_url, params=open_params) as response:
            if response.status == 200:
                open_data = await response.json()
                open_issues = open_data.get('total_count', 0)
            else:
                open_issues = 0
        
        # Get closed issues count
        closed_params = {
            "q": f"repo:{repo_name} type:issue state:closed",
            "per_page": 1  # We only need the count
        }
        
        async with session.get(open_url, params=closed_params) as response:
            if response.status == 200:
                closed_data = await response.json()
                closed_issues = closed_data.get('total_count', 0)
            else:
                closed_issues = 0
        
        # Get recent issues for display
        recent_url = f"{github_tool.base_url}/repos/{repo_name}/issues"
        recent_params = {"state": "all", "per_page": 10, "sort": "updated"}
        
        async with session.get(recent_url, params=recent_params) as response:
            if response.status == 200:
                all_items = await response.json()
                # Filter out pull requests
                issues_only = [item for item in all_items if 'pull_request' not in item]
                
                recent_issues = []
                for issue in issues_only[:5]:
                    recent_issues.append({
                        "title": issue["title"],
                        "state": issue["state"],
                        "created_at": issue["created_at"],
                        "labels": [label["name"] for label in issue.get("labels", [])]
                    })
            else:
                recent_issues = []
        
        total_issues = open_issues + closed_issues
        
        return {
            'total_issues': total_issues,
            'open_issues': open_issues,
            'closed_issues': closed_issues,
            'recent_issues': recent_issues
        }

async def get_clean_reasoning_analysis(repo_name: str, github_data: str, readme_data: str, additional_docs: str = None):
    """Get clean reasoning analysis with proper formatting."""
    
    reasoning_tool = ReasoningTool(Config.OPENAI_API_KEY, Config.MODEL_NAME, Config.TEMPERATURE)
    
    # Prepare data for reasoning
    reasoning_data = {
        "repository": repo_name,
        "github_analysis": github_data,
        "readme_content": readme_data,
        "additional_docs": additional_docs or "No additional documentation",
        "analysis_type": "comprehensive_repository_evaluation"
    }
    
    try:
        reasoning_query = f"analyze:{json.dumps(reasoning_data)}"
        reasoning_result = await reasoning_tool._arun(reasoning_query)
        
        # Debug: Print what we actually got
        print(f"DEBUG: Reasoning result type: {type(reasoning_result)}")
        print(f"DEBUG: Reasoning result preview: {str(reasoning_result)[:200]}...")
        
        # Clean up the output - extract just the text content
        if isinstance(reasoning_result, str):
            # Check if we got an error message
            if "Error in reasoning operation:" in reasoning_result:
                return f"## AI Analysis Summary\n\n**Error**: {reasoning_result}\n\n**Recommendation**: Check OpenAI API configuration and network connectivity."
            
            # Check if we got the template instead of analysis
            if "You are an expert analyst" in reasoning_result:
                clean_result = reasoning_result
            else:
                # The result is already properly formatted
                clean_result = reasoning_result
            
            # If it still contains the template, try to extract the actual analysis
            if "You are an expert analyst" in clean_result:
                # This means we got the template instead of the analysis
                # Create an honest fallback that mentions what data we couldn't get
                project_name = repo_name.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
                
                # Check what data we actually have
                has_repo_info = 'repo_info' in locals()
                has_issues_info = 'issues_info' in locals()
                
                return f"""
## AI Analysis Summary

**Note**: The AI reasoning analysis failed to generate a proper response. Below is the available repository data:

**Repository**: {repo_name}
**Project Name**: {project_name}

**Available Data**:
{f"- **Language**: {repo_info.language}" if has_repo_info else "- **Language**: Not available"}
{f"- **Stars**: {repo_info.stars:,}" if has_repo_info else "- **Stars**: Not available"}
{f"- **Forks**: {repo_info.forks:,}" if has_repo_info else "- **Forks**: Not available"}
{f"- **Open Issues**: {issues_info['open_issues']}" if has_issues_info else "- **Open Issues**: Not available"}

**Missing Analysis**:
- AI-powered project overview and capabilities assessment
- Technical strengths and weaknesses analysis
- Specific use cases and applications
- Development status and maturity assessment

**Recommendation**: 
The repository data was successfully retrieved, but the AI analysis component failed to generate insights. This could be due to:
- OpenAI API issues
- Insufficient context for analysis
- Model limitations with the provided data

**Next Steps**: 
- Review the GitHub analysis and README content above
- Consider re-running the analysis
- Check OpenAI API status and configuration
"""
            else:
                return clean_result
        else:
            return str(reasoning_result)
            
    except Exception as e:
        return f"Reasoning analysis error: {e}"

async def analyze_repository_correct(repository_name: str, additional_doc_url: str = None):
    """Correct repository analysis with accurate issue counts."""
    
    print(f"Analyzing: {repository_name}")
    print("=" * 50)
    
    # Initialize tools
    github_tool = GitHubTool()
    doc_tool = DocumentationTool()
    
    results = {}
    
    # Step 1: Correct GitHub + README Analysis
    print("Step 1: Correct GitHub Repository + README Analysis")
    print("-" * 50)
    
    try:
        github_result, readme_content = await get_correct_repo_analysis(repository_name)
        results['github_and_readme'] = github_result
        results['readme_content'] = readme_content
        print("Correct GitHub + README analysis completed")
        
    except Exception as e:
        print(f"GitHub analysis failed: {e}")
        results['github_and_readme'] = f"Error: {e}"
        results['readme_content'] = "Error"
    
    # Step 2: Additional Documentation (if provided)
    additional_docs = None
    step_counter = 2
    if additional_doc_url:
        print(f"\nStep 2: Additional Documentation Analysis")
        print("-" * 40)
        print(f"Analyzing: {additional_doc_url}")
        
        try:
            doc_result = await doc_tool._arun(f"Analyze documentation at {additional_doc_url}")
            additional_docs = doc_result
            results['additional_docs'] = doc_result
            print("Additional documentation analysis completed")
            
        except Exception as e:
            print(f"Additional documentation analysis failed: {e}")
            results['additional_docs'] = f"Error: {e}"
        
        step_counter = 3
    
    # Final Step: Clean Reasoning Analysis
    print(f"\nStep {step_counter}: AI Reasoning Analysis")
    print("-" * 30)
    
    try:
        reasoning_result = await get_clean_reasoning_analysis(
            repository_name, 
            results.get('github_and_readme', 'No data'),
            results.get('readme_content', 'No README'),
            additional_docs
        )
        results['reasoning'] = reasoning_result
        print("Reasoning analysis completed")
        
    except Exception as e:
        print(f"Reasoning analysis failed: {e}")
        results['reasoning'] = f"Error: {e}"
    
    return results

async def main():
    """Main function for correct demo."""
    
    print("CloudBees Agentic Workflow Demo - Correct Version")
    print("=" * 60)
    print("Features:")
    print("   - Correct issue counting using GitHub Search API")
    print("   - Clean, readable output formatting")
    print("   - Automatic GitHub README fetching")
    print("   - AI-powered reasoning analysis")
    print("   - Optional additional documentation")
    print()
    
    # Get user input with validation
    while True:
        repo_name = input("GitHub Repository (format: owner/repo): ").strip()
        if repo_name and "/" in repo_name and not repo_name.startswith("http"):
            break
        elif not repo_name:
            repo_name = "facebookresearch/co-tracker"
            print(f"   Using default: {repo_name}")
            break
        else:
            print("Please enter repository in format: owner/repo (e.g., facebookresearch/co-tracker)")
    
    print("\nAdditional Documentation Options:")
    print("   - Leave blank for GitHub README only")
    print("   - Official docs (e.g., https://react.dev/)")
    print("   - Any other documentation URL")
    
    additional_doc_url = input("Additional Documentation URL (optional): ").strip()
    if not additional_doc_url:
        additional_doc_url = None
        print("   Using GitHub README only")
    elif not additional_doc_url.startswith("http"):
        print("Please provide a full URL starting with http:// or https://")
        additional_doc_url = None
    
    print()
    
    # Run analysis
    try:
        results = await analyze_repository_correct(repo_name, additional_doc_url)
        
        print("\nAnalysis Complete!")
        print("\n" + "="*60)
        print("COMPREHENSIVE ANALYSIS RESULTS")
        print("="*60)
        
        # Display results in clean format
        print("\n" + results.get('github_and_readme', 'No data'))
        
        if additional_doc_url and 'additional_docs' in results:
            print(f"\nADDITIONAL DOCUMENTATION ANALYSIS")
            print("-" * 40)
            docs_content = results['additional_docs']
            if isinstance(docs_content, str) and len(docs_content) > 500:
                print(docs_content[:500] + "...")
            else:
                print(docs_content)
        
        print(f"\nAI REASONING ANALYSIS")
        print("-" * 30)
        reasoning_content = results.get('reasoning', 'No reasoning available')
        print(reasoning_content)
        
        print(f"\nAnalysis completed successfully!")
        print(f"Repository: {repo_name}")
        print(f"README: {'Included' if results.get('readme_content') != 'README not available' else 'Not found'}")
        print(f"Additional Docs: {'Included' if additional_doc_url else 'Not provided'}")
        
    except Exception as e:
        print(f"Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
