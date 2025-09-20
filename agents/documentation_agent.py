"""
Documentation Retrieval Agent for fetching and processing documentation.
"""
import asyncio
import aiohttp
import re
from typing import Dict, List, Optional, Any
from langchain.tools import BaseTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import markdown


class DocumentationSection(BaseModel):
    """Model for documentation sections."""
    title: str
    content: str
    url: str
    section_type: str  # e.g., "installation", "usage", "api", "examples"


class DocumentationAgent:
    """Agent responsible for documentation retrieval and processing."""
    
    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "AgenticWorkflowDemo/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    
    async def fetch_documentation(self, url: str) -> str:
        """Fetch documentation content from a URL."""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return content
                else:
                    raise Exception(f"Failed to fetch documentation: {response.status}")
    
    def parse_markdown_documentation(self, content: str, base_url: str = "") -> List[DocumentationSection]:
        """Parse markdown documentation into structured sections."""
        sections = []
        
        # Split content by headers
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check if line is a header
            if line.startswith('#'):
                # Save previous section if exists
                if current_section:
                    sections.append(DocumentationSection(
                        title=current_section,
                        content='\n'.join(current_content).strip(),
                        url=base_url,
                        section_type=self._classify_section_type(current_section)
                    ))
                
                # Start new section
                current_section = line.lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_section:
            sections.append(DocumentationSection(
                title=current_section,
                content='\n'.join(current_content).strip(),
                url=base_url,
                section_type=self._classify_section_type(current_section)
            ))
        
        return sections
    
    def parse_html_documentation(self, content: str, base_url: str = "") -> List[DocumentationSection]:
        """Parse HTML documentation into structured sections."""
        soup = BeautifulSoup(content, 'html.parser')
        sections = []
        
        # Find all headers (h1, h2, h3, etc.)
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for header in headers:
            title = header.get_text().strip()
            
            # Get content until next header
            content_elements = []
            current = header.next_sibling
            
            while current and current.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if hasattr(current, 'get_text'):
                    content_elements.append(current.get_text())
                elif isinstance(current, str):
                    content_elements.append(current)
                current = current.next_sibling
            
            content_text = '\n'.join(content_elements).strip()
            
            sections.append(DocumentationSection(
                title=title,
                content=content_text,
                url=base_url,
                section_type=self._classify_section_type(title)
            ))
        
        return sections
    
    def _classify_section_type(self, title: str) -> str:
        """Classify section type based on title."""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['install', 'setup', 'getting started']):
            return 'installation'
        elif any(word in title_lower for word in ['usage', 'example', 'tutorial', 'guide']):
            return 'usage'
        elif any(word in title_lower for word in ['api', 'reference', 'method', 'function']):
            return 'api'
        elif any(word in title_lower for word in ['config', 'configuration', 'settings']):
            return 'configuration'
        elif any(word in title_lower for word in ['troubleshoot', 'faq', 'common issues']):
            return 'troubleshooting'
        else:
            return 'general'
    
    def extract_key_information(self, sections: List[DocumentationSection]) -> Dict[str, Any]:
        """Extract key information from documentation sections."""
        key_info = {
            'installation_steps': [],
            'usage_examples': [],
            'api_references': [],
            'configuration_options': [],
            'common_issues': []
        }
        
        for section in sections:
            if section.section_type == 'installation':
                # Extract installation steps
                steps = self._extract_steps(section.content)
                key_info['installation_steps'].extend(steps)
            
            elif section.section_type == 'usage':
                # Extract code examples
                examples = self._extract_code_examples(section.content)
                key_info['usage_examples'].extend(examples)
            
            elif section.section_type == 'api':
                # Extract API references
                api_refs = self._extract_api_references(section.content)
                key_info['api_references'].extend(api_refs)
            
            elif section.section_type == 'configuration':
                # Extract configuration options
                config_options = self._extract_configuration_options(section.content)
                key_info['configuration_options'].extend(config_options)
        
        return key_info
    
    def _extract_steps(self, content: str) -> List[str]:
        """Extract numbered or bulleted steps from content."""
        steps = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.', line) or line.startswith('- ') or line.startswith('* '):
                steps.append(line)
        
        return steps
    
    def _extract_code_examples(self, content: str) -> List[str]:
        """Extract code examples from content."""
        examples = []
        
        # Look for code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        examples.extend(code_blocks)
        
        # Look for inline code
        inline_code = re.findall(r'`[^`]+`', content)
        examples.extend(inline_code)
        
        return examples
    
    def _extract_api_references(self, content: str) -> List[str]:
        """Extract API references from content."""
        api_refs = []
        
        # Look for function/method definitions
        functions = re.findall(r'(?:def|function|method)\s+\w+\([^)]*\)', content, re.IGNORECASE)
        api_refs.extend(functions)
        
        # Look for class definitions
        classes = re.findall(r'class\s+\w+', content, re.IGNORECASE)
        api_refs.extend(classes)
        
        return api_refs
    
    def _extract_configuration_options(self, content: str) -> List[str]:
        """Extract configuration options from content."""
        config_options = []
        
        # Look for key-value pairs
        kv_pairs = re.findall(r'(\w+)\s*[:=]\s*([^\n]+)', content)
        config_options.extend([f"{k}: {v}" for k, v in kv_pairs])
        
        return config_options
    
    def format_documentation_summary(self, sections: List[DocumentationSection], key_info: Dict[str, Any]) -> str:
        """Format documentation into a comprehensive summary."""
        summary = "## Documentation Analysis\n\n"
        
        # Overview
        summary += f"**Total Sections Found:** {len(sections)}\n\n"
        
        # Section breakdown
        section_types = {}
        for section in sections:
            section_types[section.section_type] = section_types.get(section.section_type, 0) + 1
        
        summary += "**Section Types:**\n"
        for section_type, count in section_types.items():
            summary += f"- {section_type.title()}: {count} sections\n"
        summary += "\n"
        
        # Key information
        if key_info['installation_steps']:
            summary += "**Installation Steps:**\n"
            for step in key_info['installation_steps'][:5]:  # Limit to first 5
                summary += f"- {step}\n"
            summary += "\n"
        
        if key_info['usage_examples']:
            summary += "**Usage Examples:**\n"
            for example in key_info['usage_examples'][:3]:  # Limit to first 3
                summary += f"```\n{example}\n```\n"
            summary += "\n"
        
        if key_info['api_references']:
            summary += "**API References:**\n"
            for api_ref in key_info['api_references'][:5]:  # Limit to first 5
                summary += f"- {api_ref}\n"
            summary += "\n"
        
        # Detailed sections
        summary += "**Detailed Sections:**\n"
        for section in sections[:10]:  # Limit to first 10 sections
            summary += f"### {section.title}\n"
            summary += f"*Type: {section.section_type}*\n\n"
            # Truncate content for readability
            content_preview = section.content[:200] + "..." if len(section.content) > 200 else section.content
            summary += f"{content_preview}\n\n"
        
        return summary


class DocumentationTool(BaseTool):
    """LangChain tool wrapper for documentation operations."""
    
    name = "documentation_analyzer"
    description = "Fetch and analyze documentation from URLs, extract key information and structure"
    agent: DocumentationAgent = Field(default=None)
    
    def __init__(self):
        super().__init__()
        self.agent = DocumentationAgent()
    
    def _run(self, query: str) -> str:
        """Synchronous wrapper for documentation operations."""
        return asyncio.run(self._arun(query))
    
    async def _arun(self, query: str) -> str:
        """Asynchronous documentation operations."""
        try:
            # Extract URL from query
            url_match = re.search(r'https?://[^\s]+', query)
            if not url_match:
                return "Please provide a valid URL in your query."
            
            url = url_match.group(0)
            
            # Fetch documentation
            content = await self.agent.fetch_documentation(url)
            
            # Determine if it's HTML or Markdown
            if url.endswith('.md') or 'markdown' in content.lower():
                sections = self.agent.parse_markdown_documentation(content, url)
            else:
                sections = self.agent.parse_html_documentation(content, url)
            
            # Extract key information
            key_info = self.agent.extract_key_information(sections)
            
            # Format summary
            return self.agent.format_documentation_summary(sections, key_info)
            
        except Exception as e:
            return f"Error analyzing documentation: {str(e)}"
