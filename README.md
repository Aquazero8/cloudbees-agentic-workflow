# CloudBees Agentic Workflow Demo

A demonstration of autonomous multi-agent workflows using LangChain, showcasing how AI agents can collaborate to analyze GitHub repositories, retrieve documentation, and make reasoned decisions.

## 🌟 Overview

This project implements a **team of agents** that work together autonomously to:

- **GitHub Agent**: Analyzes repositories, fetches issues, and searches for projects
- **Documentation Agent**: Retrieves and processes documentation from URLs
- **Reasoning Agent**: Validates data, applies logical reasoning, and provides analysis
- **Orchestrator**: Coordinates multi-agent workflows and makes autonomous decisions

## 🚀 Key Features

### Autonomous Multi-Agent Collaboration
- Agents work independently but coordinate through the orchestrator
- Each agent has specialized capabilities and tools
- Agents can reason about their actions and validate their findings

### Comprehensive Repository Analysis
- Fetch repository metadata (stars, forks, issues, languages)
- **Accurate issue counting** using GitHub Search API (separates issues from pull requests)
- Analyze recent issues and community activity
- Search and compare multiple repositories
- Validate data quality and identify potential issues

### Documentation Processing
- Fetch documentation from URLs (HTML and Markdown)
- Parse and structure documentation content
- Extract key information (installation steps, usage examples, API references)
- Analyze documentation quality and completeness

### Intelligent Reasoning and Validation
- Validate data accuracy and completeness
- Apply logical reasoning to decision points
- Provide confidence scores and risk assessments
- Generate actionable recommendations

## 🛠️ Technology Stack

- **LangChain**: Framework for building agentic workflows
- **OpenAI GPT**: Large language model for reasoning and analysis
- **Python**: Core implementation language
- **AsyncIO**: Asynchronous programming for concurrent operations
- **Pydantic**: Data validation and modeling
- **BeautifulSoup**: HTML parsing for documentation
- **aiohttp**: Asynchronous HTTP client for API calls

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- GitHub token (optional, for higher rate limits)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentic-workflow-demo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create a .env file
   cp .env.example .env
   
   # Edit .env with your API keys
   OPENAI_API_KEY=your_openai_api_key_here
   GITHUB_TOKEN=your_github_token_here  # Optional
   ```

4. **Validate configuration**
   ```bash
   python -c "from config import Config; Config.validate(); print('Configuration valid!')"
   ```

## 🎯 Usage Examples

### 1. Repository Analysis Workflow

Analyze a specific repository and its documentation:

```python
from main import AgenticWorkflowOrchestrator
import asyncio

async def analyze_repo():
    orchestrator = AgenticWorkflowOrchestrator()
    
    result = await orchestrator.analyze_repository_workflow(
        repository_name="microsoft/vscode",
        documentation_url="https://code.visualstudio.com/docs"
    )
    
    print("Analysis complete!")
    print(f"Repository: {result['repository']}")
    print(f"Status: {result['workflow_status']}")

# Run the analysis
asyncio.run(analyze_repo())
```

### 2. Search and Compare Repositories

Search for repositories and compare them:

```python
async def search_and_compare():
    orchestrator = AgenticWorkflowOrchestrator()
    
    result = await orchestrator.search_and_analyze_workflow(
        search_query="python web framework",
        max_repos=3
    )
    
    print("Search and analysis complete!")
    print(f"Found {len(result['repository_analyses'])} repositories")

asyncio.run(search_and_compare())
```

### 3. Autonomous Decision Making

Make autonomous decisions based on context:

```python
async def make_decision():
    orchestrator = AgenticWorkflowOrchestrator()
    
    result = await orchestrator.autonomous_decision_workflow(
        context="A team is choosing between React, Vue.js, and Svelte for a new web application",
        decision_point="Which framework should they choose?"
    )
    
    print("Decision analysis complete!")
    print(f"Decision: {result['decision_and_rationale']}")

asyncio.run(make_decision())
```

### 4. Run the Complete Demo

Execute the full demonstration:

```bash
python demo.py
```

This will run an interactive repository analysis workflow:
1. Prompt for repository name (e.g., facebookresearch/co-tracker)
2. Optionally analyze additional documentation
3. Provide comprehensive analysis with accurate issue counts
4. Generate AI-powered insights and recommendations

## 🏗️ Architecture

### Agent Structure

```
AgenticWorkflowOrchestrator
├── GitHubAgent
│   ├── Repository Analysis
│   ├── Issues Tracking
│   └── Repository Search
├── DocumentationAgent
│   ├── URL Fetching
│   ├── Content Parsing
│   └── Information Extraction
├── ReasoningAgent
│   ├── Data Validation
│   ├── Logical Reasoning
│   └── Analysis Generation
└── LangChain Tools
    ├── Tool Integration
    ├── Agent Coordination
    └── Workflow Orchestration
```

### Workflow Types

1. **Repository Analysis**: Complete analysis of a single repository
2. **Search and Analysis**: Multi-repository comparison and ranking
3. **Autonomous Decision**: Context-aware decision making
4. **Custom Workflows**: Extensible for specific use cases

## 🔍 Key Components

### GitHub Agent (`agents/github_agent.py`)
- Fetches repository metadata and statistics
- Analyzes issues and community activity
- Searches for repositories based on criteria
- Validates data quality and identifies anomalies

### Documentation Agent (`agents/documentation_agent.py`)
- Retrieves documentation from URLs
- Parses HTML and Markdown content
- Extracts structured information
- Analyzes documentation quality

### Reasoning Agent (`agents/reasoning_agent.py`)
- Validates data accuracy and completeness
- Applies logical reasoning to problems
- Generates confidence scores and risk assessments
- Provides actionable recommendations

### Main Orchestrator (`main.py`)
- Coordinates multi-agent workflows
- Handles error recovery and fallbacks
- Provides high-level workflow interfaces
- Demonstrates autonomous decision making

## ⚙️ Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
GITHUB_TOKEN=your_github_token_here
MAX_ITERATIONS=5
TEMPERATURE=0.7
MODEL_NAME=gpt-3.5-turbo
```

### Customization

- **Model Selection**: Change the OpenAI model in `config.py`
- **Agent Behavior**: Modify agent prompts and logic
- **Workflow Steps**: Add new workflow types in `main.py`
- **Tool Integration**: Add new LangChain tools

## 🧪 Testing

Run the demo to test all components:

```bash
python demo.py
```

Expected output:
```
🌟 CloudBees Agentic Workflow Demo
==================================================

🎯 Example 1: Repository Analysis Workflow
----------------------------------------
🚀 Starting agentic workflow for repository: microsoft/vscode
📊 Step 1: Analyzing GitHub repository...
📚 Step 2: Analyzing documentation...
🔍 Step 3: Validating and reasoning about the data...
💡 Step 4: Generating final recommendations...
✅ Repository Analysis Complete!

🎯 Example 2: Search and Analysis Workflow
----------------------------------------
🔍 Starting search and analysis workflow for: python web framework
📊 Step 1: Searching for repositories...
🔍 Step 2: Analyzing top 2 repositories...
⚖️ Step 3: Comparing and ranking repositories...
✅ Search and Analysis Complete!

🎯 Example 3: Autonomous Decision Workflow
----------------------------------------
🤖 Starting autonomous decision workflow...
📊 Step 1: Gathering relevant information...
🧠 Step 2: Applying logical reasoning...
💡 Step 3: Generating decision and rationale...
✅ Autonomous Decision Complete!

🎉 Agentic Workflow Demo Complete!
```

## 🚨 Limitations and Assumptions

### Current Limitations
- **API Rate Limits**: GitHub API has rate limits (higher with token)
- **Documentation Parsing**: Limited to HTML and Markdown formats
- **Model Dependencies**: Requires OpenAI API access
- **Error Handling**: Basic error recovery and fallbacks

### Assumptions
- **Repository Access**: Public repositories only
- **Documentation Format**: Standard HTML/Markdown structure
- **API Availability**: Reliable internet connection required
- **Model Behavior**: GPT-3.5-turbo responses are consistent

## 🔮 Future Enhancements

### Potential Improvements
- **Multi-Model Support**: Integration with other LLMs
- **Caching**: Implement caching for API responses
- **Advanced Parsing**: Support for more documentation formats
- **Custom Agents**: Framework for adding new agent types
- **Workflow Persistence**: Save and resume workflows
- **Real-time Updates**: Live monitoring of repository changes

### Extensibility
- **New Agent Types**: Add specialized agents for specific domains
- **Custom Tools**: Integrate additional LangChain tools
- **Workflow Templates**: Predefined workflows for common tasks
- **API Integration**: Connect with other development tools

## 📚 Learning Outcomes

This demo demonstrates:

1. **Autonomous Agent Design**: How to create agents that can work independently
2. **Multi-Agent Coordination**: Orchestrating multiple agents for complex tasks
3. **Tool Integration**: Using LangChain tools effectively
4. **Reasoning and Validation**: Implementing logical reasoning in AI systems
5. **Error Handling**: Building robust agentic workflows
6. **Real-World Applications**: Practical use cases for agentic systems

## 🤝 Contributing

This is a demonstration project for the CloudBees take-home assessment. The code showcases:

- **Clean Architecture**: Well-structured, modular design
- **Async Programming**: Efficient concurrent operations
- **Error Handling**: Robust error recovery mechanisms
- **Documentation**: Comprehensive code documentation
- **Extensibility**: Easy to extend and modify

## 📄 License

This project is created for educational and demonstration purposes as part of the CloudBees take-home assessment.

---

**Note**: This demo requires an OpenAI API key and internet connection to function. The GitHub token is optional but recommended for higher rate limits.
