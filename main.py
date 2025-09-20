"""
Main orchestration workflow for the agentic system.
Demonstrates autonomous multi-agent collaboration for repository analysis.
"""
import asyncio
import json
import sys
from typing import Dict, List, Optional, Any
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import MessagesPlaceholder

# Import our custom agents
from agents.github_agent import GitHubTool
from agents.documentation_agent import DocumentationTool
from agents.reasoning_agent import ReasoningTool
from config import Config


class AgenticWorkflowOrchestrator:
    """Main orchestrator for the agentic workflow."""
    
    def __init__(self):
        # Validate configuration
        Config.validate()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            openai_api_key=Config.OPENAI_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE
        )
        
        # Initialize tools
        self.tools = [
            GitHubTool(Config.GITHUB_TOKEN),
            DocumentationTool(),
            ReasoningTool(Config.OPENAI_API_KEY, Config.MODEL_NAME, Config.TEMPERATURE)
        ]
        
        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an intelligent agentic workflow orchestrator. Your role is to:

1. **Analyze GitHub Repositories**: Use the github_analyzer tool to fetch repository information, issues, and search for repositories.

2. **Retrieve Documentation**: Use the documentation_analyzer tool to fetch and analyze documentation from URLs.

3. **Validate and Reason**: Use the reasoning_analyzer tool to validate data, analyze information, and apply logical reasoning.

4. **Coordinate Multi-Agent Workflows**: Orchestrate multiple agents to work together on complex tasks.

5. **Provide Comprehensive Analysis**: Combine insights from all agents to provide actionable recommendations.

**Workflow Guidelines:**
- Always validate data before making decisions
- Provide reasoning for your analysis
- Suggest concrete next steps
- Be autonomous but explain your reasoning
- Handle errors gracefully and provide fallback options

**Available Tools:**
- github_analyzer: Analyze GitHub repositories and search for repositories
- documentation_analyzer: Fetch and analyze documentation from URLs
- reasoning_analyzer: Validate data and apply logical reasoning

Use these tools autonomously to complete the user's request."""),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=Config.MAX_ITERATIONS,
            handle_parsing_errors=True
        )
    
    async def analyze_repository_workflow(self, repository_name: str, documentation_url: Optional[str] = None) -> Dict[str, Any]:
        """Complete workflow for analyzing a repository and its documentation."""
        
        print(f"🚀 Starting agentic workflow for repository: {repository_name}")
        
        # Step 1: Analyze GitHub repository
        print("\n📊 Step 1: Analyzing GitHub repository...")
        github_query = f"repo:{repository_name}"
        github_result = await self.agent_executor.ainvoke({"input": github_query})
        
        # Step 2: Analyze documentation if provided
        doc_result = None
        if documentation_url:
            print(f"\n📚 Step 2: Analyzing documentation from {documentation_url}...")
            doc_query = f"Analyze the documentation at {documentation_url}"
            doc_result = await self.agent_executor.ainvoke({"input": doc_query})
        
        # Step 3: Validate and reason about the data
        print("\n🔍 Step 3: Validating and reasoning about the data...")
        
        # Prepare data for validation
        validation_data = {
            "github": {"repository": repository_name, "analysis": github_result},
            "documentation": {"url": documentation_url, "analysis": doc_result} if documentation_url else None
        }
        
        validation_query = f"analyze:{json.dumps(validation_data)}"
        validation_result = await self.agent_executor.ainvoke({"input": validation_query})
        
        # Step 4: Generate final recommendations
        print("\n💡 Step 4: Generating final recommendations...")
        final_query = f"""
        Based on the GitHub analysis and documentation analysis, provide:
        1. A comprehensive summary of the repository
        2. Key strengths and weaknesses
        3. Actionable recommendations for improvement
        4. Next steps for someone interested in this project
        
        GitHub Analysis: {github_result}
        Documentation Analysis: {doc_result if doc_result else 'No documentation provided'}
        Validation Results: {validation_result}
        """
        
        final_result = await self.agent_executor.ainvoke({"input": final_query})
        
        return {
            "repository": repository_name,
            "github_analysis": github_result,
            "documentation_analysis": doc_result,
            "validation_results": validation_result,
            "final_recommendations": final_result,
            "workflow_status": "completed"
        }
    
    async def search_and_analyze_workflow(self, search_query: str, max_repos: int = 3) -> Dict[str, Any]:
        """Workflow for searching and analyzing multiple repositories."""
        
        print(f"🔍 Starting search and analysis workflow for: {search_query}")
        
        # Step 1: Search for repositories
        print(f"\n📊 Step 1: Searching for repositories matching '{search_query}'...")
        search_query_formatted = f"search:{search_query}"
        search_result = await self.agent_executor.ainvoke({"input": search_query_formatted})
        
        # Step 2: Analyze top repositories
        print(f"\n🔍 Step 2: Analyzing top {max_repos} repositories...")
        analysis_results = []
        
        # Extract repository names from search results (simplified parsing)
        repo_names = self._extract_repository_names(search_result, max_repos)
        
        for repo_name in repo_names:
            print(f"\n  📋 Analyzing {repo_name}...")
            repo_query = f"repo:{repo_name}"
            repo_result = await self.agent_executor.ainvoke({"input": repo_query})
            analysis_results.append({
                "repository": repo_name,
                "analysis": repo_result
            })
        
        # Step 3: Compare and rank repositories
        print(f"\n⚖️ Step 3: Comparing and ranking repositories...")
        comparison_query = f"""
        Compare and rank the following repositories based on:
        1. Code quality indicators (stars, forks, issues)
        2. Documentation quality
        3. Community activity
        4. Overall project health
        
        Provide a ranked list with reasoning for each ranking.
        
        Repository Analyses: {json.dumps(analysis_results, indent=2)}
        """
        
        comparison_result = await self.agent_executor.ainvoke({"input": comparison_query})
        
        return {
            "search_query": search_query,
            "search_results": search_result,
            "repository_analyses": analysis_results,
            "comparison_and_ranking": comparison_result,
            "workflow_status": "completed"
        }
    
    def _extract_repository_names(self, search_result: str, max_repos: int) -> List[str]:
        """Extract repository names from search results."""
        repo_names = []
        
        # Simple extraction - look for patterns like "owner/repo"
        import re
        matches = re.findall(r'(\w+/\w+)', search_result)
        
        for match in matches[:max_repos]:
            if match not in repo_names:
                repo_names.append(match)
        
        return repo_names
    
    async def autonomous_decision_workflow(self, context: str, decision_point: str) -> Dict[str, Any]:
        """Workflow for autonomous decision making."""
        
        print(f"🤖 Starting autonomous decision workflow...")
        print(f"Context: {context}")
        print(f"Decision Point: {decision_point}")
        
        # Step 1: Gather relevant information
        print(f"\n📊 Step 1: Gathering relevant information...")
        info_query = f"""
        Based on the context and decision point, identify what information would be helpful:
        
        Context: {context}
        Decision Point: {decision_point}
        
        Suggest what data or analysis would be most valuable for making this decision.
        """
        
        info_result = await self.agent_executor.ainvoke({"input": info_query})
        
        # Step 2: Apply reasoning
        print(f"\n🧠 Step 2: Applying logical reasoning...")
        reasoning_query = f"reason:{context}\n\nDecision Point: {decision_point}"
        reasoning_result = await self.agent_executor.ainvoke({"input": reasoning_query})
        
        # Step 3: Generate decision and rationale
        print(f"\n💡 Step 3: Generating decision and rationale...")
        decision_query = f"""
        Based on the context, decision point, and reasoning analysis, provide:
        1. A clear decision or recommendation
        2. The rationale behind the decision
        3. Potential risks and mitigation strategies
        4. Alternative options considered
        5. Next steps for implementation
        
        Context: {context}
        Decision Point: {decision_point}
        Reasoning Analysis: {reasoning_result}
        """
        
        decision_result = await self.agent_executor.ainvoke({"input": decision_query})
        
        return {
            "context": context,
            "decision_point": decision_point,
            "information_gathering": info_result,
            "reasoning_analysis": reasoning_result,
            "decision_and_rationale": decision_result,
            "workflow_status": "completed"
        }


async def main():
    """Main function to demonstrate the agentic workflow."""
    
    print("🌟 CloudBees Agentic Workflow Demo")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = AgenticWorkflowOrchestrator()
    
    # Example 1: Analyze a specific repository
    print("\n🎯 Example 1: Repository Analysis Workflow")
    print("-" * 40)
    
    try:
        result1 = await orchestrator.analyze_repository_workflow(
            repository_name="microsoft/vscode",
            documentation_url="https://code.visualstudio.com/docs"
        )
        
        print("\n✅ Repository Analysis Complete!")
        print(f"Repository: {result1['repository']}")
        print(f"Status: {result1['workflow_status']}")
        
    except Exception as e:
        print(f"❌ Error in repository analysis: {e}")
    
    # Example 2: Search and analyze multiple repositories
    print("\n🎯 Example 2: Search and Analysis Workflow")
    print("-" * 40)
    
    try:
        result2 = await orchestrator.search_and_analyze_workflow(
            search_query="python web framework",
            max_repos=2
        )
        
        print("\n✅ Search and Analysis Complete!")
        print(f"Search Query: {result2['search_query']}")
        print(f"Status: {result2['workflow_status']}")
        
    except Exception as e:
        print(f"❌ Error in search and analysis: {e}")
    
    # Example 3: Autonomous decision making
    print("\n🎯 Example 3: Autonomous Decision Workflow")
    print("-" * 40)
    
    try:
        result3 = await orchestrator.autonomous_decision_workflow(
            context="A development team is considering adopting a new JavaScript framework for their web application. They currently use React but are interested in exploring alternatives like Vue.js or Svelte. The team has 5 developers with varying levels of experience.",
            decision_point="Should the team adopt Vue.js, Svelte, or stick with React?"
        )
        
        print("\n✅ Autonomous Decision Complete!")
        print(f"Decision Point: {result3['decision_point']}")
        print(f"Status: {result3['workflow_status']}")
        
    except Exception as e:
        print(f"❌ Error in autonomous decision: {e}")
    
    print("\n🎉 Agentic Workflow Demo Complete!")
    print("=" * 50)


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
