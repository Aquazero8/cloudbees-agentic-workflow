"""
Reasoning and Validation Agent for analyzing and validating information.
"""
from typing import Dict, List, Optional, Any, Tuple
from langchain.tools import BaseTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import json
import re


class ValidationResult(BaseModel):
    """Model for validation results."""
    is_valid: bool
    confidence: float
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    reasoning: str


class AnalysisResult(BaseModel):
    """Model for analysis results."""
    summary: str
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    risk_assessment: str
    next_steps: List[str] = Field(default_factory=list)


class ReasoningAgent:
    """Agent responsible for reasoning, validation, and analysis."""
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model_name,
            temperature=temperature
        )
        
        # Define reasoning prompts
        self.validation_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert validator and quality assessor. Your role is to:
1. Analyze information for accuracy, completeness, and reliability
2. Identify potential issues or inconsistencies
3. Provide confidence scores and reasoning
4. Suggest improvements or corrections

Be thorough but concise in your analysis."""),
            HumanMessage(content="{input_data}")
        ])
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert analyst specializing in technical documentation and code analysis. Your role is to:
1. Analyze the SPECIFIC technology, framework, or domain of the repository
2. Identify what makes this project unique or interesting
3. Assess the technical quality and maturity based on the actual content
4. Provide SPECIFIC insights about this particular project, not generic advice

IMPORTANT: Your analysis must be specific to the repository being analyzed. Do not provide generic advice that could apply to any project. Focus on:
- What this specific technology does
- What makes it interesting or valuable
- Specific technical strengths or weaknesses you observe
- Domain-specific insights about the technology or use case

CRITICAL: Be confident and direct in your analysis. Avoid phrases like "it appears to be", "looks like", "seems to be". State facts directly based on the evidence provided. Use definitive language like "This is", "The project is", "This technology does".

IMPORTANT: Provide a comprehensive analysis that gives developers a clear understanding of what this repository is about. Include:
- What the technology actually does and how it works
- What makes it unique or valuable
- Specific use cases and applications
- Technical strengths and limitations
- Community health and project maturity
- Specific insights about the domain/technology

Make the analysis longer and more detailed. Developers should understand the project's purpose, capabilities, and value proposition after reading your analysis.

Avoid generic statements like "active development" or "good documentation" unless you can explain WHY specifically for this project."""),
            HumanMessage(content="{input_data}")
        ])
        
        self.reasoning_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a logical reasoning expert. Your role is to:
1. Break down complex problems into manageable parts
2. Identify relationships and dependencies
3. Apply logical reasoning to reach conclusions
4. Explain your reasoning process clearly

Use clear, step-by-step reasoning and provide evidence for your conclusions."""),
            HumanMessage(content="{input_data}")
        ])
    
    def validate_repository_data(self, repo_data: Dict[str, Any]) -> ValidationResult:
        """Validate GitHub repository data."""
        issues = []
        suggestions = []
        
        # Check for required fields
        required_fields = ['name', 'full_name', 'stars', 'forks', 'open_issues']
        for field in required_fields:
            if field not in repo_data:
                issues.append(f"Missing required field: {field}")
        
        # Validate data types and ranges
        if 'stars' in repo_data:
            try:
                stars = int(repo_data['stars'])
                if stars < 0:
                    issues.append("Stars count cannot be negative")
                elif stars > 1000000:
                    suggestions.append("Repository has unusually high star count - verify authenticity")
            except (ValueError, TypeError):
                issues.append("Stars count is not a valid number")
        
        if 'forks' in repo_data:
            try:
                forks = int(repo_data['forks'])
                if forks < 0:
                    issues.append("Forks count cannot be negative")
            except (ValueError, TypeError):
                issues.append("Forks count is not a valid number")
        
        if 'open_issues' in repo_data:
            try:
                issues_count = int(repo_data['open_issues'])
                if issues_count < 0:
                    issues.append("Open issues count cannot be negative")
                elif issues_count > 10000:
                    suggestions.append("High number of open issues - may indicate maintenance challenges")
            except (ValueError, TypeError):
                issues.append("Open issues count is not a valid number")
        
        # Check for suspicious patterns
        if 'description' in repo_data and repo_data['description']:
            desc = repo_data['description'].lower()
            if len(desc) < 10:
                suggestions.append("Description is very short - consider adding more details")
            if any(word in desc for word in ['test', 'example', 'demo', 'sample']):
                suggestions.append("Repository appears to be a test/demo - verify if this is the intended target")
        
        # Calculate confidence score
        confidence = 1.0
        if issues:
            confidence -= len(issues) * 0.2
        if suggestions:
            confidence -= len(suggestions) * 0.1
        confidence = max(0.0, min(1.0, confidence))
        
        reasoning = f"Validation completed with {len(issues)} issues and {len(suggestions)} suggestions. "
        reasoning += "Data appears " + ("reliable" if confidence > 0.7 else "questionable" if confidence > 0.4 else "unreliable") + "."
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
            reasoning=reasoning
        )
    
    def validate_documentation_data(self, doc_data: Dict[str, Any]) -> ValidationResult:
        """Validate documentation data."""
        issues = []
        suggestions = []
        
        # Check for required sections
        required_sections = ['installation', 'usage']
        for section in required_sections:
            if section not in doc_data.get('sections', {}):
                suggestions.append(f"Missing recommended section: {section}")
        
        # Validate content quality
        if 'sections' in doc_data:
            for section_name, section_content in doc_data['sections'].items():
                if len(section_content) < 50:
                    suggestions.append(f"Section '{section_name}' is very short - consider expanding")
                
                # Check for code examples in usage sections
                if section_name.lower() in ['usage', 'examples', 'getting started']:
                    if '```' not in section_content and 'code' not in section_content.lower():
                        suggestions.append(f"Section '{section_name}' lacks code examples")
        
        # Check for common documentation issues
        if 'key_info' in doc_data:
            key_info = doc_data['key_info']
            if not key_info.get('installation_steps'):
                issues.append("No installation steps found")
            if not key_info.get('usage_examples'):
                suggestions.append("No usage examples found")
        
        # Calculate confidence score
        confidence = 1.0
        if issues:
            confidence -= len(issues) * 0.3
        if suggestions:
            confidence -= len(suggestions) * 0.1
        confidence = max(0.0, min(1.0, confidence))
        
        reasoning = f"Documentation validation completed with {len(issues)} critical issues and {len(suggestions)} suggestions. "
        reasoning += "Documentation quality is " + ("excellent" if confidence > 0.8 else "good" if confidence > 0.6 else "needs improvement") + "."
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
            reasoning=reasoning
        )
    
    async def analyze_combined_data(self, github_data: Dict[str, Any], doc_data: Dict[str, Any]) -> AnalysisResult:
        """Analyze combined GitHub and documentation data."""
        
        # Prepare combined data for analysis
        combined_data = {
            "github_repository": github_data,
            "documentation": doc_data,
            "analysis_request": "Provide comprehensive analysis of this repository and its documentation"
        }
        
        # Get LLM analysis
        response = await self.analysis_prompt.ainvoke({"input_data": json.dumps(combined_data, indent=2)})
        analysis_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse the analysis
        key_findings = self._extract_key_findings(analysis_text)
        recommendations = self._extract_recommendations(analysis_text)
        risk_assessment = self._extract_risk_assessment(analysis_text)
        next_steps = self._extract_next_steps(analysis_text)
        
        return AnalysisResult(
            summary=analysis_text,
            key_findings=key_findings,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            next_steps=next_steps
        )
    
    def _extract_key_findings(self, text: str) -> List[str]:
        """Extract key findings from analysis text."""
        findings = []
        
        # Look for bullet points or numbered lists
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+\.\s+', line):
                findings.append(line)
        
        # If no structured findings, extract sentences with key phrases
        if not findings:
            sentences = text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(phrase in sentence.lower() for phrase in ['important', 'key', 'notable', 'significant']):
                    findings.append(sentence + '.')
        
        return findings[:5]  # Limit to 5 findings
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from analysis text."""
        recommendations = []
        
        # Look for recommendation patterns
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(phrase in line.lower() for phrase in ['recommend', 'suggest', 'should', 'consider']):
                recommendations.append(line)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _extract_risk_assessment(self, text: str) -> str:
        """Extract risk assessment from analysis text."""
        # Look for risk-related content
        risk_indicators = ['risk', 'concern', 'issue', 'problem', 'challenge', 'limitation']
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in risk_indicators):
                return sentence + '.'
        
        return "No significant risks identified in the analysis."
    
    def _extract_next_steps(self, text: str) -> List[str]:
        """Extract next steps from analysis text."""
        next_steps = []
        
        # Look for action-oriented phrases
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(phrase in line.lower() for phrase in ['next step', 'action', 'implement', 'deploy', 'test']):
                next_steps.append(line)
        
        return next_steps[:3]  # Limit to 3 next steps
    
    async def reason_about_decision(self, context: str, decision_point: str) -> str:
        """Apply logical reasoning to a decision point."""
        
        reasoning_data = {
            "context": context,
            "decision_point": decision_point,
            "request": "Apply logical reasoning to analyze this decision point and provide a reasoned conclusion"
        }
        
        response = await self.reasoning_prompt.ainvoke({"input_data": json.dumps(reasoning_data, indent=2)})
        return response.content if hasattr(response, 'content') else str(response)


class ReasoningTool(BaseTool):
    """LangChain tool wrapper for reasoning operations."""
    
    name = "reasoning_analyzer"
    description = "Validate data, analyze information, and apply logical reasoning to decision points"
    agent: ReasoningAgent = Field(default=None)
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        super().__init__()
        self.agent = ReasoningAgent(openai_api_key, model_name, temperature)
    
    def _run(self, query: str) -> str:
        """Synchronous wrapper for reasoning operations."""
        import asyncio
        return asyncio.run(self._arun(query))
    
    async def _arun(self, query: str) -> str:
        """Asynchronous reasoning operations."""
        try:
            # Parse the query to determine operation type
            if "validate:github" in query.lower():
                # Extract GitHub data from query
                data_start = query.find("{")
                data_end = query.rfind("}") + 1
                if data_start != -1 and data_end != 0:
                    github_data = json.loads(query[data_start:data_end])
                    result = self.agent.validate_repository_data(github_data)
                    return self._format_validation_result(result)
            
            elif "validate:doc" in query.lower():
                # Extract documentation data from query
                data_start = query.find("{")
                data_end = query.rfind("}") + 1
                if data_start != -1 and data_end != 0:
                    doc_data = json.loads(query[data_start:data_end])
                    result = self.agent.validate_documentation_data(doc_data)
                    return self._format_validation_result(result)
            
            elif "analyze:" in query.lower():
                # Extract data for analysis
                data_start = query.find("{")
                data_end = query.rfind("}") + 1
                if data_start != -1 and data_end != 0:
                    data = json.loads(query[data_start:data_end])
                    github_data = data.get("github", {})
                    doc_data = data.get("documentation", {})
                    result = await self.agent.analyze_combined_data(github_data, doc_data)
                    return self._format_analysis_result(result)
            
            elif "reason:" in query.lower():
                # Extract context and decision point
                parts = query.split("reason:")
                if len(parts) > 1:
                    context = parts[1].strip()
                    decision_point = "Analyze the provided context and provide reasoned conclusions"
                    result = await self.agent.reason_about_decision(context, decision_point)
                    return result
            
            else:
                return "Please specify operation type: 'validate:github', 'validate:doc', 'analyze:', or 'reason:'"
                
        except Exception as e:
            return f"Error in reasoning operation: {str(e)}"
    
    def _format_validation_result(self, result: ValidationResult) -> str:
        """Format validation result for output."""
        output = f"## Validation Result\n\n"
        output += f"**Valid:** {'Yes' if result.is_valid else 'No'}\n"
        output += f"**Confidence:** {result.confidence:.2f}\n\n"
        output += f"**Reasoning:** {result.reasoning}\n\n"
        
        if result.issues:
            output += "**Issues Found:**\n"
            for issue in result.issues:
                output += f"- ❌ {issue}\n"
            output += "\n"
        
        if result.suggestions:
            output += "**Suggestions:**\n"
            for suggestion in result.suggestions:
                output += f"- 💡 {suggestion}\n"
            output += "\n"
        
        return output
    
    def _format_analysis_result(self, result: AnalysisResult) -> str:
        """Format analysis result for output."""
        output = f"## Analysis Result\n\n"
        output += f"**Summary:**\n{result.summary}\n\n"
        
        if result.key_findings:
            output += "**Key Findings:**\n"
            for finding in result.key_findings:
                output += f"- {finding}\n"
            output += "\n"
        
        if result.recommendations:
            output += "**Recommendations:**\n"
            for rec in result.recommendations:
                output += f"- {rec}\n"
            output += "\n"
        
        output += f"**Risk Assessment:** {result.risk_assessment}\n\n"
        
        if result.next_steps:
            output += "**Next Steps:**\n"
            for step in result.next_steps:
                output += f"- {step}\n"
            output += "\n"
        
        return output
