"""
Nia MCP Proxy Server - Lightweight server that communicates with Nia API
"""
import os
import logging
import json
import asyncio
import webbrowser
from typing import List, Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Resource
from .api_client import NIAApiClient, APIError
from .project_init import initialize_nia_project
from .profiles import get_supported_profiles
from dotenv import load_dotenv
import json

# Load .env from parent directory (nia-app/.env)
from pathlib import Path
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Changed from INFO to DEBUG for troubleshooting
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

# TOOL SELECTION GUIDE FOR AI ASSISTANTS:
# 
# Use 'nia_web_search' for:
#   - "Find RAG libraries" → Simple search
#   - "What's trending in Rust?" → Quick discovery
#   - "Show me repos like LangChain" → Similarity search
#
# Use 'nia_deep_research_agent' for:
#   - "Compare RAG vs GraphRAG approaches" → Comparative analysis
#   - "What are the best vector databases for production?" → Evaluation needed
#   - "Analyze the pros and cons of different LLM frameworks" → Structured analysis
#
# The AI should assess query complexity and choose accordingly.

# Create the MCP server
mcp = FastMCP("nia-knowledge-agent")

# Global API client instance
api_client: Optional[NIAApiClient] = None

def get_api_key() -> str:
    """Get API key from environment."""
    api_key = os.getenv("NIA_API_KEY")
    if not api_key:
        raise ValueError(
            "NIA_API_KEY environment variable not set. "
            "Get your API key at https://trynia.ai/api-keys"
        )
    return api_key

async def ensure_api_client() -> NIAApiClient:
    """Ensure API client is initialized."""
    global api_client
    if not api_client:
        api_key = get_api_key()
        api_client = NIAApiClient(api_key)
        # Validate the API key
        if not await api_client.validate_api_key():
            # The validation error is already logged, just raise a generic error
            raise ValueError("Failed to validate API key. Check logs for details.")
    return api_client

# Tools

@mcp.tool()
async def index_repository(
    repo_url: str,
    branch: Optional[str] = None
) -> List[TextContent]:
    """
    Index a GitHub repository for intelligent code search.
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/owner/repo or https://github.com/owner/repo/tree/branch)
        branch: Branch to index (optional, defaults to main branch)
        
    Returns:
        Status of the indexing operation
    
    Important:
        - When started indexing, prompt users to either use check_repository_status tool or go to app.trynia.ai to check the status.
    """
    try:
        client = await ensure_api_client()
        
        # Start indexing
        logger.info(f"Starting to index repository: {repo_url}")
        result = await client.index_repository(repo_url, branch)
        
        repository = result.get("repository", repo_url)
        status = result.get("status", "unknown")
        
        if status == "completed":
            return [TextContent(
                type="text",
                text=f"✅ Repository already indexed: {repository}\n"
                     f"Branch: {result.get('branch', 'main')}\n"
                     f"You can now search this codebase!"
            )]
        else:
            # Wait for indexing to complete
            return [TextContent(
                type="text",
                text=f"⏳ Indexing started for: {repository}\n"
                     f"Branch: {branch or 'default'}\n"
                     f"Status: {status}\n\n"
                     f"Use `check_repository_status` to monitor progress."
            )]
            
    except APIError as e:
        logger.error(f"API Error indexing repository: {e} (status_code={e.status_code}, detail={e.detail})")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "indexing operations" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error indexing repository: {e}")
        error_msg = str(e)
        if "indexing operations" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
            )]
        return [TextContent(
            type="text",
            text=f"❌ Error indexing repository: {error_msg}"
        )]

@mcp.tool()
async def search_codebase(
    query: str,
    repositories: Optional[List[str]] = None,
    include_sources: bool = True
) -> List[TextContent]:
    """
    Search indexed repositories using natural language.
    
    Args:
        query: Natural language search query. Don't just use keywords or unstrctured query, make a comprehensive question to get the best results possible.
        repositories: List of repositories to search (owner/repo or owner/repo/tree/branch if indexed differently before).
            - "owner/repo" - Search entire repository (e.g., "facebook/react")
            - "owner/repo/tree/branch/folder" - Search specific folder indexed separately
              (e.g., "PostHog/posthog/tree/master/docs")
            Use the EXACT format shown in list_repositories output for folder-indexed repos.
            If not specified, searches all indexed repos.
        include_sources: Whether to include source code in results
        
    Returns:
        Search results with relevant code snippets and explanations
        
    Examples:
        # Search all indexed repositories
        search_codebase("How does authentication work?")
        
        # Search specific repository
        search_codebase("How to create custom hooks?", ["facebook/react"])
        
        # Search folder-indexed repository (use exact format from list_repositories)
        search_codebase("What is Flox?", ["PostHog/posthog/tree/master/docs"])

    Important:
        - If you want to search a specific folder, use the EXACT repository path shown above
        - Example: `search_codebase(\"query\", [\"owner/repo/tree/branch/folder\"])`
    """
    try:
        client = await ensure_api_client()
        
        # Get all indexed repositories if not specified
        if not repositories:
            all_repos = await client.list_repositories()
            
            # Ensure all_repos is a list and contains dictionaries
            if not isinstance(all_repos, list):
                logger.error(f"Unexpected type for all_repos: {type(all_repos)}")
                return [TextContent(
                    type="text",
                    text="❌ Error retrieving repositories. The API returned an unexpected response."
                )]
            
            repositories = []
            for repo in all_repos:
                if isinstance(repo, dict) and repo.get("status") == "completed":
                    repo_name = repo.get("repository")
                    if repo_name:
                        repositories.append(repo_name)
                    else:
                        logger.warning(f"Repository missing 'repository' field: {repo}")
                else:
                    logger.warning(f"Unexpected repository format: {type(repo)}, value: {repo}")
            
            if not repositories:
                return [TextContent(
                    type="text",
                    text="❌ No indexed repositories found. Use `index_repository` to index a codebase first."
                )]
        
        # Build messages for the query
        messages = [
            {"role": "user", "content": query}
        ]
        
        logger.info(f"Searching {len(repositories)} repositories")
        
        # Stream the response using unified query
        response_parts = []
        sources_parts = []
        follow_up_questions = []
        
        async for chunk in client.query_unified(
            messages=messages,
            repositories=repositories,
            data_sources=[],  # No documentation sources
            search_mode="repositories",  # Use repositories mode to exclude external sources
            stream=True,
            include_sources=include_sources
        ):
            try:
                data = json.loads(chunk)
                
                if "content" in data and data["content"] and data["content"] != "[DONE]":
                    response_parts.append(data["content"])
                
                if "sources" in data and data["sources"]:
                    logger.debug(f"Received sources data: {type(data['sources'])}, count: {len(data['sources'])}")
                    sources_parts.extend(data["sources"])
                
                if "follow_up_questions" in data and data["follow_up_questions"]:
                    follow_up_questions = data["follow_up_questions"]
                    logger.debug(f"Received {len(follow_up_questions)} follow-up questions")
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON chunk: {chunk}, error: {e}")
                continue
        
        # Format the response
        response_text = "".join(response_parts)
        
        if sources_parts and include_sources:
            response_text += "\n\n## Sources\n\n"
            for i, source in enumerate(sources_parts[:10], 1):  # Limit to 10 sources (matches backend)
                response_text += f"### Source {i}\n"
                
                # Handle both string sources (file paths) and dictionary sources
                if isinstance(source, str):
                    # Source is just a file path string
                    response_text += f"**File:** `{source}`\n\n"
                    continue
                elif not isinstance(source, dict):
                    logger.warning(f"Expected source to be dict or str, got {type(source)}: {source}")
                    response_text += f"**Source:** {str(source)}\n\n"
                    continue
                
                # Handle dictionary sources with metadata
                metadata = source.get("metadata", {})
                
                # Repository name
                repository = source.get("repository") or metadata.get("source_name") or metadata.get("repository")
                if repository:
                    response_text += f"**Repository:** {repository}\n"
                
                # File path
                file_path = source.get("file") or source.get("file_path") or metadata.get("file_path")
                if file_path:
                    response_text += f"**File:** `{file_path}`\n"
                
                # Content/preview
                content = source.get("preview") or source.get("content")
                if content:
                    # Truncate very long content
                    if len(content) > 500:
                        content = content[:500] + "..."
                    response_text += f"```\n{content}\n```\n\n"
                else:
                    # If no content, at least show that this is a valid source
                    response_text += f"*Referenced source*\n\n"
            
            # Add helpful text about read_source_content tool
            response_text += "\n💡 **Need more details from a source?**\n\n"
            response_text += "If you need more information from the source links provided above, use the `read_source_content` tool from the available tools provided by Nia to get full context about that particular source.\n"
        
        # Add follow-up questions if available
        if follow_up_questions:
            response_text += "\n\n## 🔍 Suggested Follow-up Questions\n\n"
            for i, question in enumerate(follow_up_questions, 1):
                response_text += f"{i}. {question}\n"
            response_text += "\n*These questions are based on the search results and can help you explore deeper insights.*\n"
        
        return [TextContent(type="text", text=response_text)]
        
    except APIError as e:
        logger.error(f"API Error searching codebase: {e} (status_code={e.status_code}, detail={e.detail})")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "indexing operations" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error searching codebase: {e}")
        error_msg = str(e)
        if "indexing operations" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
            )]
        return [TextContent(
            type="text",
            text=f"❌ Error searching codebase: {error_msg}"
        )]

@mcp.tool()
async def search_documentation(
    query: str,
    sources: Optional[List[str]] = None,
    include_sources: bool = True
) -> List[TextContent]:
    """
    Search indexed documentation using natural language. 
    
    Args:
        query: Natural language search query. Don't just use keywords or unstrctured query, make a comprehensive question to get the best results possible.
        sources: List of documentation source IDs to search. Use it based on user's query.
        include_sources: Whether to include source references in results
        
    Returns:
        Search results with relevant documentation excerpts

    Important:
        - Always use Source ID. If you don't have it, use `list_documentation` tool to get it.
    """
    try:
        client = await ensure_api_client()
        
        # Get all indexed documentation sources if not specified
        if not sources:
            all_sources = await client.list_data_sources()
            sources = [source["id"] for source in all_sources if source.get("status") == "completed"]
            if not sources:
                return [TextContent(
                    type="text",
                    text="❌ No indexed documentation found. Use `index_documentation` to index documentation first."
                )]
        
        # Build messages for the query
        messages = [
            {"role": "user", "content": query}
        ]
        
        logger.info(f"Searching {len(sources)} documentation sources")
        
        # Stream the response using unified query
        response_parts = []
        sources_parts = []
        follow_up_questions = []
        
        async for chunk in client.query_unified(
            messages=messages,
            repositories=[],  # No repositories
            data_sources=sources,
            search_mode="unified",  # Use unified mode for intelligent LLM processing
            stream=True,
            include_sources=include_sources
        ):
            try:
                data = json.loads(chunk)
                
                if "content" in data and data["content"] and data["content"] != "[DONE]":
                    response_parts.append(data["content"])
                
                if "sources" in data and data["sources"]:
                    logger.debug(f"Received doc sources data: {type(data['sources'])}, count: {len(data['sources'])}")
                    sources_parts.extend(data["sources"])
                
                if "follow_up_questions" in data and data["follow_up_questions"]:
                    follow_up_questions = data["follow_up_questions"]
                    logger.debug(f"Received {len(follow_up_questions)} follow-up questions for documentation")
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON chunk in documentation search: {chunk}, error: {e}")
                continue
        
        # Format the response
        response_text = "".join(response_parts)
        
        if sources_parts and include_sources:
            response_text += "\n\n## Sources\n\n"
            for i, source in enumerate(sources_parts[:10], 1):  # Limit to 10 sources (matches backend)
                response_text += f"### Source {i}\n"
                
                # Handle both string sources and dictionary sources
                if isinstance(source, str):
                    # Source is just a URL or file path string
                    response_text += f"**Document:** {source}\n\n"
                    continue
                elif not isinstance(source, dict):
                    logger.warning(f"Expected source to be dict or str, got {type(source)}: {source}")
                    response_text += f"**Source:** {str(source)}\n\n"
                    continue
                
                # Handle dictionary sources with metadata
                metadata = source.get("metadata", {})
                
                # URL or file
                url = source.get("url") or metadata.get("url") or metadata.get("source") or metadata.get("sourceURL")
                file_path = source.get("file") or source.get("file_path") or metadata.get("file_path") or metadata.get("document_name")
                
                if url:
                    response_text += f"**URL:** {url}\n"
                elif file_path:
                    response_text += f"**Document:** {file_path}\n"
                
                # Title if available
                title = source.get("title") or metadata.get("title")
                if title:
                    response_text += f"**Title:** {title}\n"
                
                # Add spacing after each source
                response_text += "\n"
            
            # Add helpful text about read_source_content tool
            response_text += "\n💡 **Need more details from a source?**\n\n"
            response_text += "If you need more information from the source links provided above, use the `read_source_content` tool from the available tools provided by Nia to get full context about that particular source.\n"
        
        # Add follow-up questions if available
        if follow_up_questions:
            response_text += "\n\n## 🔍 Suggested Follow-up Questions\n\n"
            for i, question in enumerate(follow_up_questions, 1):
                response_text += f"{i}. {question}\n"
            response_text += "\n*These questions are based on the documentation and can help you explore related topics.*\n"
        
        return [TextContent(type="text", text=response_text)]
        
    except APIError as e:
        logger.error(f"API Error searching documentation: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 3 indexing operations. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error searching documentation: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error searching documentation: {str(e)}"
        )]

# @mcp.tool()
# async def list_repositories() -> List[TextContent]:
    """
    List all indexed repositories.
    
    Returns:
        List of indexed repositories with their status
    """
    try:
        client = await ensure_api_client()
        repositories = await client.list_repositories()
        
        if not repositories:
            return [TextContent(
                type="text",
                text="No indexed repositories found.\n\n"
                     "Get started by indexing a repository:\n"
                     "Use `index_repository` with a GitHub URL."
            )]
        
        # Format repository list
        lines = ["# Indexed Repositories\n"]
        
        # Check if any repositories have folder paths (contain /tree/)
        has_folder_repos = any('/tree/' in repo.get('repository', '') for repo in repositories)
        
        for repo in repositories:
            status_icon = "✅" if repo.get("status") == "completed" else "⏳"
            
            # Show display name if available, otherwise show repository
            display_name = repo.get("display_name")
            repo_name = repo['repository']
            
            if display_name:
                lines.append(f"\n## {status_icon} {display_name}")
                lines.append(f"- **Repository:** {repo_name}")
            else:
                lines.append(f"\n## {status_icon} {repo_name}")
            
            lines.append(f"- **Branch:** {repo.get('branch', 'main')}")
            lines.append(f"- **Status:** {repo.get('status', 'unknown')}")
            if repo.get("indexed_at"):
                lines.append(f"- **Indexed:** {repo['indexed_at']}")
            if repo.get("error"):
                lines.append(f"- **Error:** {repo['error']}")
            
            # Add usage hint for completed repositories
            if repo.get("status") == "completed":
                lines.append(f"- **Usage:** `search_codebase(query, [\"{repo_name}\"])`")
        
        # Return without usage tips
        return [TextContent(type="text", text="\n".join(lines))]
        
    except APIError as e:
        logger.error(f"API Error listing repositories: {e} (status_code={e.status_code}, detail={e.detail})")
        # Check for free tier limit errors
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "indexing operations" in str(e).lower():
            # Extract the specific limit message
            if e.detail and "3 free indexing operations" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error listing repositories (type={type(e).__name__}): {e}")
        # Check if this looks like an API limit error that wasn't caught properly
        error_msg = str(e)
        if "indexing operations" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
            )]
        return [TextContent(
            type="text",
            text=f"❌ Error listing repositories: {error_msg}"
        )]

# @mcp.tool()
# async def check_repository_status(repository: str) -> List[TextContent]:
    """
    Check the indexing status of a repository.
    
    Args:
        repository: Repository in owner/repo format
        
    Returns:
        Current status of the repository
    """
    try:
        client = await ensure_api_client()
        status = await client.get_repository_status(repository)
        
        if not status:
            return [TextContent(
                type="text",
                text=f"❌ Repository '{repository}' not found."
            )]
        
        # Format status
        status_icon = {
            "completed": "✅",
            "indexing": "⏳",
            "failed": "❌",
            "pending": "🔄"
        }.get(status["status"], "❓")
        
        lines = [
            f"# Repository Status: {repository}\n",
            f"{status_icon} **Status:** {status['status']}",
            f"**Branch:** {status.get('branch', 'main')}"
        ]
        
        if status.get("progress"):
            progress = status["progress"]
            if isinstance(progress, dict):
                lines.append(f"**Progress:** {progress.get('percentage', 0)}%")
                if progress.get("stage"):
                    lines.append(f"**Stage:** {progress['stage']}")
        
        if status.get("indexed_at"):
            lines.append(f"**Indexed:** {status['indexed_at']}")
        
        if status.get("error"):
            lines.append(f"**Error:** {status['error']}")
        
        return [TextContent(type="text", text="\n".join(lines))]
        
    except APIError as e:
        logger.error(f"API Error checking repository status: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 3 indexing operations. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error checking repository status: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error checking repository status: {str(e)}"
        )]

@mcp.tool()
async def index_documentation(
    url: str,
    url_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    max_age: Optional[int] = None,
    only_main_content: Optional[bool] = True,
    wait_for: Optional[int] = None,
    include_screenshot: Optional[bool] = None,
    check_llms_txt: Optional[bool] = True,
    llms_txt_strategy: Optional[str] = "prefer"
) -> List[TextContent]:
    """
    Index documentation or website for intelligent search.
    
    Args:
        url: URL of the documentation site to index
        url_patterns: Optional list of URL patterns to include in crawling (e.g., ["/docs/*", "/guide/*"])
        exclude_patterns: Optional list of URL patterns to exclude from crawling (e.g., ["/blog/*", "/changelog/*"])
        max_age: Maximum age of cached content in seconds (for fast scraping mode)
        only_main_content: Extract only main content (removes navigation, ads, etc.)
        wait_for: Time to wait for page to load in milliseconds (defaults to backend setting)
        include_screenshot: Whether to capture full page screenshots (defaults to backend setting)
        check_llms_txt: Check for llms.txt file for curated documentation URLs (default: True)
        llms_txt_strategy: How to use llms.txt if found:
            - "prefer": Start with llms.txt URLs, then crawl additional pages if under limit
            - "only": Only index URLs listed in llms.txt
            - "ignore": Skip llms.txt check (traditional behavior)
        
    Returns:
        Status of the indexing operation

    Important:
        - When started indexing, prompt users to either use check_documentation_status tool or go to app.trynia.ai to check the status.
        - By default, crawls the entire domain (up to 10,000 pages)
        - Use exclude_patterns to filter out unwanted sections like blogs, changelogs, etc.
    """
    try:
        client = await ensure_api_client()
        
        # Create and start indexing
        logger.info(f"Starting to index documentation: {url}")
        result = await client.create_data_source(
            url=url, 
            url_patterns=url_patterns,
            exclude_patterns=exclude_patterns,
            max_age=max_age,
            only_main_content=only_main_content,
            wait_for=wait_for,
            include_screenshot=include_screenshot,
            check_llms_txt=check_llms_txt,
            llms_txt_strategy=llms_txt_strategy
        )
        
        source_id = result.get("id")
        status = result.get("status", "unknown")
        
        if status == "completed":
            return [TextContent(
                type="text",
                text=f"✅ Documentation already indexed: {url}\n"
                     f"Source ID: {source_id}\n"
                     f"You can now search this documentation!"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"⏳ Documentation indexing started: {url}\n"
                     f"Source ID: {source_id}\n"
                     f"Status: {status}\n\n"
                     f"Use `check_documentation_status` to monitor progress."
            )]
            
    except APIError as e:
        logger.error(f"API Error indexing documentation: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 3 indexing operations. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error indexing documentation: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error indexing documentation: {str(e)}"
        )]

# @mcp.tool()
# async def list_documentation() -> List[TextContent]:
    """
    List all indexed documentation sources.
    
    Returns:
        List of indexed documentation with their status
    """
    try:
        client = await ensure_api_client()
        sources = await client.list_data_sources()
        
        if not sources:
            return [TextContent(
                type="text",
                text="No indexed documentation found.\n\n"
                     "Get started by indexing documentation:\n"
                     "Use `index_documentation` with a URL."
            )]
        
        # Format source list
        lines = ["# Indexed Documentation\n"]
        
        for source in sources:
            status_icon = "✅" if source.get("status") == "completed" else "⏳"
            
            # Show display name if available, otherwise show URL
            display_name = source.get("display_name")
            url = source.get('url', 'Unknown URL')
            
            if display_name:
                lines.append(f"\n## {status_icon} {display_name}")
                lines.append(f"- **URL:** {url}")
            else:
                lines.append(f"\n## {status_icon} {url}")
            
            lines.append(f"- **ID:** {source['id']}")
            lines.append(f"- **Status:** {source.get('status', 'unknown')}")
            lines.append(f"- **Type:** {source.get('source_type', 'web')}")
            if source.get("page_count", 0) > 0:
                lines.append(f"- **Pages:** {source['page_count']}")
            if source.get("created_at"):
                lines.append(f"- **Created:** {source['created_at']}")
        
        return [TextContent(type="text", text="\n".join(lines))]
        
    except APIError as e:
        logger.error(f"API Error listing documentation: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 3 indexing operations. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error listing documentation: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error listing documentation: {str(e)}"
        )]

# @mcp.tool()
# async def check_documentation_status(source_id: str) -> List[TextContent]:
    """
    Check the indexing status of a documentation source.
    
    Args:
        source_id: Documentation source ID
        
    Returns:
        Current status of the documentation source
    """
    try:
        client = await ensure_api_client()
        status = await client.get_data_source_status(source_id)
        
        if not status:
            return [TextContent(
                type="text",
                text=f"❌ Documentation source '{source_id}' not found."
            )]
        
        # Format status
        status_icon = {
            "completed": "✅",
            "processing": "⏳",
            "failed": "❌",
            "pending": "🔄"
        }.get(status["status"], "❓")
        
        lines = [
            f"# Documentation Status: {status.get('url', 'Unknown URL')}\n",
            f"{status_icon} **Status:** {status['status']}",
            f"**Source ID:** {source_id}"
        ]
        
        if status.get("page_count", 0) > 0:
            lines.append(f"**Pages Indexed:** {status['page_count']}")
        
        if status.get("details"):
            details = status["details"]
            if details.get("progress"):
                lines.append(f"**Progress:** {details['progress']}%")
            if details.get("stage"):
                lines.append(f"**Stage:** {details['stage']}")
        
        if status.get("created_at"):
            lines.append(f"**Created:** {status['created_at']}")
        
        if status.get("error"):
            lines.append(f"**Error:** {status['error']}")
        
        return [TextContent(type="text", text="\n".join(lines))]
        
    except APIError as e:
        logger.error(f"API Error checking documentation status: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 3 indexing operations. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error checking documentation status: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error checking documentation status: {str(e)}"
        )]

# Combined Resource Management Tools

@mcp.tool()
async def rename_resource(
    resource_type: str,
    identifier: str,
    new_name: str
) -> List[TextContent]:
    """
    Rename a resource (repository or documentation) for better organization.

    Args:
        resource_type: Type of resource - "repository" or "documentation"
        identifier:
            - For repository: Repository in owner/repo format (e.g., "facebook/react")
            - For documentation: Documentation source ID
        new_name: New display name for the resource (1-100 characters)

    Returns:
        Confirmation of rename operation

    Examples:
        - rename_resource("repository", "facebook/react", "React Framework")
        - rename_resource("documentation", "doc-id-123", "Python Official Docs")
    """
    try:
        # Validate resource type
        if resource_type not in ["repository", "documentation"]:
            return [TextContent(
                type="text",
                text=f"❌ Invalid resource_type: '{resource_type}'. Must be 'repository' or 'documentation'."
            )]

        # Validate name length
        if not new_name or len(new_name) > 100:
            return [TextContent(
                type="text",
                text="❌ Display name must be between 1 and 100 characters."
            )]

        client = await ensure_api_client()

        if resource_type == "repository":
            result = await client.rename_repository(identifier, new_name)
            resource_desc = f"repository '{identifier}'"
        else:  # documentation
            result = await client.rename_data_source(identifier, new_name)
            resource_desc = f"documentation source"

        if result.get("success"):
            return [TextContent(
                type="text",
                text=f"✅ Successfully renamed {resource_desc} to '{new_name}'"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ Failed to rename {resource_type}: {result.get('message', 'Unknown error')}"
            )]

    except APIError as e:
        logger.error(f"API Error renaming {resource_type}: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error renaming {resource_type}: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error renaming {resource_type}: {str(e)}"
        )]

@mcp.tool()
async def delete_resource(
    resource_type: str,
    identifier: str
) -> List[TextContent]:
    """
    Delete an indexed resource (repository or documentation).

    Args:
        resource_type: Type of resource - "repository" or "documentation"
        identifier:
            - For repository: Repository in owner/repo format (e.g., "facebook/react")
            - For documentation: Documentation source ID

    Returns:
        Confirmation of deletion

    Examples:
        - delete_resource("repository", "facebook/react")
        - delete_resource("documentation", "doc-id-123")
    """
    try:
        # Validate resource type
        if resource_type not in ["repository", "documentation"]:
            return [TextContent(
                type="text",
                text=f"❌ Invalid resource_type: '{resource_type}'. Must be 'repository' or 'documentation'."
            )]

        client = await ensure_api_client()

        if resource_type == "repository":
            success = await client.delete_repository(identifier)
            resource_desc = f"repository: {identifier}"
        else:  # documentation
            success = await client.delete_data_source(identifier)
            resource_desc = f"documentation source: {identifier}"

        if success:
            return [TextContent(
                type="text",
                text=f"✅ Successfully deleted {resource_desc}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ Failed to delete {resource_desc}"
            )]

    except APIError as e:
        logger.error(f"API Error deleting {resource_type}: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 3 indexing operations. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error deleting {resource_type}: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error deleting {resource_type}: {str(e)}"
        )]

@mcp.tool()
async def check_resource_status(
    resource_type: str,
    identifier: str
) -> List[TextContent]:
    """
    Check the indexing status of a resource (repository or documentation).

    Args:
        resource_type: Type of resource - "repository" or "documentation"
        identifier:
            - For repository: Repository in owner/repo format (e.g., "facebook/react")
            - For documentation: Documentation source ID

    Returns:
        Current status of the resource

    Examples:
        - check_resource_status("repository", "facebook/react")
        - check_resource_status("documentation", "doc-id-123")
    """
    try:
        # Validate resource type
        if resource_type not in ["repository", "documentation"]:
            return [TextContent(
                type="text",
                text=f"❌ Invalid resource_type: '{resource_type}'. Must be 'repository' or 'documentation'."
            )]

        client = await ensure_api_client()

        if resource_type == "repository":
            status = await client.get_repository_status(identifier)
            if not status:
                return [TextContent(
                    type="text",
                    text=f"❌ Repository '{identifier}' not found."
                )]
            title = f"Repository Status: {identifier}"
            status_key = "status"
        else:  # documentation
            status = await client.get_data_source_status(identifier)
            if not status:
                return [TextContent(
                    type="text",
                    text=f"❌ Documentation source '{identifier}' not found."
                )]
            title = f"Documentation Status: {status.get('url', 'Unknown URL')}"
            status_key = "status"

        # Format status with appropriate icon
        status_text = status.get(status_key, "unknown")
        status_icon = {
            "completed": "✅",
            "indexing": "⏳",
            "processing": "⏳",
            "failed": "❌",
            "pending": "🔄",
            "error": "❌"
        }.get(status_text, "❓")

        lines = [
            f"# {title}\n",
            f"{status_icon} **Status:** {status_text}"
        ]

        # Add resource-specific fields
        if resource_type == "repository":
            lines.append(f"**Branch:** {status.get('branch', 'main')}")
            if status.get("progress"):
                progress = status["progress"]
                if isinstance(progress, dict):
                    lines.append(f"**Progress:** {progress.get('percentage', 0)}%")
                    if progress.get("stage"):
                        lines.append(f"**Stage:** {progress['stage']}")
        else:  # documentation
            lines.append(f"**Source ID:** {identifier}")
            if status.get("page_count", 0) > 0:
                lines.append(f"**Pages Indexed:** {status['page_count']}")
            if status.get("details"):
                details = status["details"]
                if details.get("progress"):
                    lines.append(f"**Progress:** {details['progress']}%")
                if details.get("stage"):
                    lines.append(f"**Stage:** {details['stage']}")

        # Common fields
        if status.get("indexed_at"):
            lines.append(f"**Indexed:** {status['indexed_at']}")
        elif status.get("created_at"):
            lines.append(f"**Created:** {status['created_at']}")

        if status.get("error"):
            lines.append(f"**Error:** {status['error']}")

        return [TextContent(type="text", text="\n".join(lines))]

    except APIError as e:
        logger.error(f"API Error checking {resource_type} status: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 3 indexing operations. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error checking {resource_type} status: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error checking {resource_type} status: {str(e)}"
        )]

@mcp.tool()
async def list_resources(
    resource_type: Optional[str] = None
) -> List[TextContent]:
    """
    List indexed resources (repositories and/or documentation).

    Args:
        resource_type: Optional filter - "repository", "documentation", or None for all

    Returns:
        List of indexed resources with their status

    Examples:
        - list_resources() - List all resources
        - list_resources("repository") - List only repositories
        - list_resources("documentation") - List only documentation
    """
    try:
        # Validate resource type if provided
        if resource_type and resource_type not in ["repository", "documentation"]:
            return [TextContent(
                type="text",
                text=f"❌ Invalid resource_type: '{resource_type}'. Must be 'repository', 'documentation', or None for all."
            )]

        client = await ensure_api_client()
        lines = []

        # Determine what to list
        list_repos = resource_type in [None, "repository"]
        list_docs = resource_type in [None, "documentation"]

        if list_repos:
            repositories = await client.list_repositories()

            if repositories:
                lines.append("# Indexed Repositories\n")
                for repo in repositories:
                    status_icon = "✅" if repo.get("status") == "completed" else "⏳"

                    # Show display name if available, otherwise show repository
                    display_name = repo.get("display_name")
                    repo_name = repo['repository']

                    if display_name:
                        lines.append(f"\n## {status_icon} {display_name}")
                        lines.append(f"- **Repository:** {repo_name}")
                    else:
                        lines.append(f"\n## {status_icon} {repo_name}")

                    lines.append(f"- **Branch:** {repo.get('branch', 'main')}")
                    lines.append(f"- **Status:** {repo.get('status', 'unknown')}")
                    if repo.get("indexed_at"):
                        lines.append(f"- **Indexed:** {repo['indexed_at']}")
                    if repo.get("error"):
                        lines.append(f"- **Error:** {repo['error']}")

                    # Add usage hint for completed repositories
                    if repo.get("status") == "completed":
                        lines.append(f"- **Usage:** `search_codebase(query, [\"{repo_name}\"])`")
            elif resource_type == "repository":
                lines.append("No indexed repositories found.\n\n")
                lines.append("Get started by indexing a repository:\n")
                lines.append("Use `index_repository` with a GitHub URL.")

        if list_docs:
            sources = await client.list_data_sources()

            if sources:
                if lines:  # Add separator if we already have repositories
                    lines.append("\n---\n")
                lines.append("# Indexed Documentation\n")

                for source in sources:
                    status_icon = "✅" if source.get("status") == "completed" else "⏳"

                    # Show display name if available, otherwise show URL
                    display_name = source.get("display_name")
                    url = source.get('url', 'Unknown URL')

                    if display_name:
                        lines.append(f"\n## {status_icon} {display_name}")
                        lines.append(f"- **URL:** {url}")
                    else:
                        lines.append(f"\n## {status_icon} {url}")

                    lines.append(f"- **ID:** {source['id']}")
                    lines.append(f"- **Status:** {source.get('status', 'unknown')}")
                    lines.append(f"- **Type:** {source.get('source_type', 'web')}")
                    if source.get("page_count", 0) > 0:
                        lines.append(f"- **Pages:** {source['page_count']}")
                    if source.get("created_at"):
                        lines.append(f"- **Created:** {source['created_at']}")
            elif resource_type == "documentation":
                lines.append("No indexed documentation found.\n\n")
                lines.append("Get started by indexing documentation:\n")
                lines.append("Use `index_documentation` with a URL.")

        if not lines:
            lines.append("No indexed resources found.\n\n")
            lines.append("Get started by indexing:\n")
            lines.append("- Use `index_repository` for GitHub repositories\n")
            lines.append("- Use `index_documentation` for documentation sites")

        return [TextContent(type="text", text="\n".join(lines))]

    except APIError as e:
        logger.error(f"API Error listing resources: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 or "free tier limit" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                error_msg = f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
            else:
                error_msg += "\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Unexpected error listing resources: {e}")
        error_msg = str(e)
        if "indexing operations" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
            )]
        return [TextContent(
            type="text",
            text=f"❌ Error listing resources: {error_msg}"
        )]

# Old individual tools (to be commented out after testing)

# @mcp.tool()
# async def delete_documentation(source_id: str) -> List[TextContent]:
    """
    Delete an indexed documentation source.
    
    Args:
        source_id: Documentation source ID to delete
        
    Returns:
        Confirmation of deletion
    """
    try:
        client = await ensure_api_client()
        success = await client.delete_data_source(source_id)
        
        if success:
            return [TextContent(
                type="text",
                text=f"✅ Successfully deleted documentation source: {source_id}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ Failed to delete documentation source: {source_id}"
            )]
            
    except APIError as e:
        logger.error(f"API Error deleting documentation: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 3 indexing operations. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error deleting documentation: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error deleting documentation: {str(e)}"
        )]

# @mcp.tool()
# async def delete_repository(repository: str) -> List[TextContent]:
    """
    Delete an indexed repository.
    
    Args:
        repository: Repository in owner/repo format
        
    Returns:
        Confirmation of deletion
    """
    try:
        client = await ensure_api_client()
        success = await client.delete_repository(repository)
        
        if success:
            return [TextContent(
                type="text",
                text=f"✅ Successfully deleted repository: {repository}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ Failed to delete repository: {repository}"
            )]
            
    except APIError as e:
        logger.error(f"API Error deleting repository: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit of 3 indexing operations. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error deleting repository: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error deleting repository: {str(e)}"
        )]

# @mcp.tool()
# async def rename_repository(repository: str, new_name: str) -> List[TextContent]:
    """
    Rename an indexed repository for better organization.
    
    Args:
        repository: Repository in owner/repo format
        new_name: New display name for the repository (1-100 characters)
        
    Returns:
        Confirmation of rename operation
    """
    try:
        # Validate name length
        if not new_name or len(new_name) > 100:
            return [TextContent(
                type="text",
                text="❌ Display name must be between 1 and 100 characters."
            )]
        
        client = await ensure_api_client()
        result = await client.rename_repository(repository, new_name)
        
        if result.get("success"):
            return [TextContent(
                type="text",
                text=f"✅ Successfully renamed repository '{repository}' to '{new_name}'"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ Failed to rename repository: {result.get('message', 'Unknown error')}"
            )]
            
    except APIError as e:
        logger.error(f"API Error renaming repository: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error renaming repository: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error renaming repository: {str(e)}"
        )]

# @mcp.tool()
# async def rename_documentation(source_id: str, new_name: str) -> List[TextContent]:
    """
    Rename a documentation source for better organization.
    
    Args:
        source_id: Documentation source ID
        new_name: New display name for the documentation (1-100 characters)
        
    Returns:
        Confirmation of rename operation
    """
    try:
        # Validate name length
        if not new_name or len(new_name) > 100:
            return [TextContent(
                type="text",
                text="❌ Display name must be between 1 and 100 characters."
            )]
        
        client = await ensure_api_client()
        result = await client.rename_data_source(source_id, new_name)
        
        if result.get("success"):
            return [TextContent(
                type="text",
                text=f"✅ Successfully renamed documentation source to '{new_name}'"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ Failed to rename documentation: {result.get('message', 'Unknown error')}"
            )]
            
    except APIError as e:
        logger.error(f"API Error renaming documentation: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 and "lifetime limit" in str(e).lower():
            error_msg += "\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error renaming documentation: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error renaming documentation: {str(e)}"
        )]

@mcp.tool()
async def nia_web_search(
    query: str,
    num_results: int = 5,
    category: Optional[str] = None,
    days_back: Optional[int] = None,
    find_similar_to: Optional[str] = None
) -> List[TextContent]:
    """
    Search repositories, documentation, and other content using AI-powered search.
    Returns results formatted to guide next actions.
    
    USE THIS TOOL WHEN:
    - Finding specific repos/docs/content ("find X library", "trending Y frameworks")
    - Looking for examples or implementations
    - Searching for what's available on a topic
    - Simple, direct searches that need quick results
    - Finding similar content to a known URL
    
    DON'T USE THIS FOR:
    - Comparative analysis (use nia_deep_research_agent instead)
    - Complex multi-faceted questions (use nia_deep_research_agent instead)
    - Questions requiring synthesis of multiple sources (use nia_deep_research_agent instead)
    
    Args:
        query: Natural language search query (e.g., "best RAG implementations", "trending rust web frameworks")
        num_results: Number of results to return (default: 5, max: 10)
        category: Filter by category: "github", "company", "research paper", "news", "tweet", "pdf"
        days_back: Only show results from the last N days (for trending content)
        find_similar_to: URL to find similar content to
        
    Returns:
        Search results with actionable next steps
    """
    try:
        client = await ensure_api_client()
        
        logger.info(f"Searching content for query: {query}")
        
        # Use the API client method instead of direct HTTP call
        result = await client.web_search(
            query=query,
            num_results=num_results,
            category=category,
            days_back=days_back,
            find_similar_to=find_similar_to
        )
        
        # Extract results
        github_repos = result.get("github_repos", [])
        documentation = result.get("documentation", [])
        other_content = result.get("other_content", [])
        
        # Format response to naturally guide next actions
        response_text = f"## 🔍 Nia Web Search Results for: \"{query}\"\n\n"
        
        if days_back:
            response_text += f"*Showing results from the last {days_back} days*\n\n"
        
        if find_similar_to:
            response_text += f"*Finding content similar to: {find_similar_to}*\n\n"
        
        # GitHub Repositories Section
        if github_repos:
            response_text += f"### 📦 GitHub Repositories ({len(github_repos)} found)\n\n"
            
            for i, repo in enumerate(github_repos[:num_results], 1):
                response_text += f"**{i}. {repo['title']}**\n"
                response_text += f"   📍 `{repo['url']}`\n"
                if repo.get('published_date'):
                    response_text += f"   📅 Updated: {repo['published_date']}\n"
                if repo['summary']:
                    response_text += f"   📝 {repo['summary']}...\n"
                if repo['highlights']:
                    response_text += f"   ✨ Key features: {', '.join(repo['highlights'])}\n"
                response_text += "\n"
            
            # Be more aggressive based on query specificity
            if len(github_repos) == 1 or any(specific_word in query.lower() for specific_word in ["specific", "exact", "particular", "find me", "looking for"]):
                response_text += "**🚀 RECOMMENDED ACTION - Index this repository with Nia:**\n"
                response_text += f"```\nIndex {github_repos[0]['owner_repo']}\n```\n"
                response_text += "✨ This will enable AI-powered code search, understanding, and analysis!\n\n"
            else:
                response_text += "**🚀 Make these repositories searchable with NIA's AI:**\n"
                response_text += f"- **Quick start:** Say \"Index {github_repos[0]['owner_repo']}\"\n"
                response_text += "- **Index multiple:** Say \"Index all repositories\"\n"
                response_text += "- **Benefits:** AI-powered code search, architecture understanding, implementation details\n\n"
        
        # Documentation Section
        if documentation:
            response_text += f"### 📚 Documentation ({len(documentation)} found)\n\n"
            
            for i, doc in enumerate(documentation[:num_results], 1):
                response_text += f"**{i}. {doc['title']}**\n"
                response_text += f"   📍 `{doc['url']}`\n"
                if doc['summary']:
                    response_text += f"   📝 {doc['summary']}...\n"
                if doc.get('highlights'):
                    response_text += f"   ✨ Key topics: {', '.join(doc['highlights'])}\n"
                response_text += "\n"
            
            # Be more aggressive for documentation too
            if len(documentation) == 1 or any(specific_word in query.lower() for specific_word in ["docs", "documentation", "guide", "tutorial", "reference"]):
                response_text += "**📖 RECOMMENDED ACTION - Index this documentation with NIA:**\n"
                response_text += f"```\nIndex documentation {documentation[0]['url']}\n```\n"
                response_text += "✨ NIA will make this fully searchable with AI-powered Q&A!\n\n"
            else:
                response_text += "**📖 Make this documentation AI-searchable with NIA:**\n"
                response_text += f"- **Quick start:** Say \"Index documentation {documentation[0]['url']}\"\n"
                response_text += "- **Index all:** Say \"Index all documentation\"\n"
                response_text += "- **Benefits:** Instant answers, smart search, code examples extraction\n\n"
        
        # Other Content Section
        if other_content and not github_repos and not documentation:
            response_text += f"### 🌐 Other Content ({len(other_content)} found)\n\n"
            
            for i, content in enumerate(other_content[:num_results], 1):
                response_text += f"**{i}. {content['title']}**\n"
                response_text += f"   📍 `{content['url']}`\n"
                if content['summary']:
                    response_text += f"   📝 {content['summary']}...\n"
                response_text += "\n"
        
        # No results found
        if not github_repos and not documentation and not other_content:
            response_text = f"No results found for '{query}'. Try:\n"
            response_text += "- Using different keywords\n"
            response_text += "- Being more specific (e.g., 'Python RAG implementation')\n"
            response_text += "- Including technology names (e.g., 'LangChain', 'TypeScript')\n"
        
        # Add prominent call-to-action if we found indexable content
        if github_repos or documentation:
            response_text += "\n## 🎯 **Ready to unlock NIA's AI capabilities?**\n"
            response_text += "The repositories and documentation above can be indexed for:\n"
            response_text += "- 🤖 AI-powered code understanding and search\n"
            response_text += "- 💡 Instant answers to technical questions\n"
            response_text += "- 🔍 Deep architectural insights\n"
            response_text += "- 📚 Smart documentation Q&A\n\n"
            response_text += "**Just copy and paste the index commands above!**\n"
        
        # Add search metadata
        response_text += f"\n---\n"
        response_text += f"*Searched {result.get('total_results', 0)} sources using NIA Web Search*"
        
        return [TextContent(type="text", text=response_text)]
        
    except APIError as e:
        logger.error(f"API Error in web search: {e}")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "indexing operations" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error in NIA web search: {str(e)}")
        return [TextContent(
            type="text",
            text=f"❌ NIA Web Search error: {str(e)}\n\n"
                 "This might be due to:\n"
                 "- Network connectivity issues\n"
                 "- Service temporarily unavailable"
        )]

@mcp.tool()
async def nia_deep_research_agent(
    query: str,
    output_format: Optional[str] = None
) -> List[TextContent]:
    """
    Perform deep, multi-step research on a topic using advanced AI research capabilities.
    Best for complex questions that need comprehensive analysis. Don't just use keywords or unstrctured query, make a comprehensive question to get the best results possible.
    
    USE THIS TOOL WHEN:
    - Comparing multiple options ("compare X vs Y vs Z")
    - Analyzing pros and cons
    - Questions with "best", "top", "which is better"
    - Needing structured analysis or synthesis
    - Complex questions requiring multiple sources
    - Questions about trends, patterns, or developments
    - Requests for comprehensive overviews
    
    DON'T USE THIS FOR:
    - Simple lookups (use nia_web_search instead)
    - Finding a specific known item (use nia_web_search instead)
    - Quick searches for repos/docs (use nia_web_search instead)
    
    COMPLEXITY INDICATORS:
    - Words like: compare, analyze, evaluate, pros/cons, trade-offs
    - Multiple criteria mentioned
    - Asking for recommendations based on context
    - Needing structured output (tables, lists, comparisons)
    
    Args:
        query: Research question (e.g., "Compare top 3 RAG frameworks with pros/cons")
        output_format: Optional structure hint (e.g., "comparison table", "pros and cons list")
        
    Returns:
        Comprehensive research results with citations
    """
    try:
        client = await ensure_api_client()
        
        logger.info(f"Starting deep research for: {query}")
        
        # Use the API client method with proper timeout handling
        try:
            result = await asyncio.wait_for(
                client.deep_research(query=query, output_format=output_format),
                timeout=720.0  # 12 minutes to allow for longer research tasks
            )
        except asyncio.TimeoutError:
            logger.error(f"Deep research timed out after 12 minutes for query: {query}")
            return [TextContent(
                type="text",
                text="❌ Research timed out. The query may be too complex. Try:\n"
                     "- Breaking it into smaller questions\n"  
                     "- Using more specific keywords\n"
                     "- Trying the nia_web_search tool for simpler queries"
            )]
        
        # Format the research results
        response_text = f"## 🔬 NIA Deep Research Agent Results\n\n"
        response_text += f"**Query:** {query}\n\n"
        
        if result.get("data"):
            response_text += "### 📊 Research Findings:\n\n"
            
            # Pretty print the JSON data
            
            formatted_data = json.dumps(result["data"], indent=2)
            response_text += f"```json\n{formatted_data}\n```\n\n"
            
            # Add citations if available
            if result.get("citations"):
                response_text += "### 📚 Sources & Citations:\n\n"
                citation_num = 1
                for field, citations in result["citations"].items():
                    if citations:
                        response_text += f"**{field}:**\n"
                        for citation in citations[:3]:  # Limit to 3 citations per field
                            response_text += f"{citation_num}. [{citation.get('title', 'Source')}]({citation.get('url', '#')})\n"
                            if citation.get('snippet'):
                                response_text += f"   > {citation['snippet'][:150]}...\n"
                            citation_num += 1
                        response_text += "\n"
            
            response_text += "### 💡 RECOMMENDED NEXT ACTIONS WITH NIA:\n\n"
            
            # Extract potential repos and docs from the research data
            repos_found = []
            docs_found = []
            
            # Helper function to extract URLs from nested data structures
            def extract_urls_from_data(data, urls_list=None):
                if urls_list is None:
                    urls_list = []
                
                if isinstance(data, dict):
                    for value in data.values():
                        extract_urls_from_data(value, urls_list)
                elif isinstance(data, list):
                    for item in data:
                        extract_urls_from_data(item, urls_list)
                elif isinstance(data, str):
                    # Check if this string is a URL
                    if data.startswith(('http://', 'https://')):
                        urls_list.append(data)
                
                return urls_list
            
            # Extract all URLs from the data
            all_urls = extract_urls_from_data(result["data"])
            
            # Filter for GitHub repos and documentation
            import re
            github_pattern = r'github\.com/([a-zA-Z0-9-]+/[a-zA-Z0-9-_.]+)'
            
            for url in all_urls:
                # Check for GitHub repos
                github_match = re.search(github_pattern, url)
                if github_match and '/tree/' not in url and '/blob/' not in url:
                    repos_found.append(github_match.group(1))
                # Check for documentation URLs
                elif any(doc_indicator in url.lower() for doc_indicator in ['docs', 'documentation', '.readthedocs.', '/guide', '/tutorial']):
                    docs_found.append(url)
            
            # Remove duplicates and limit results
            repos_found = list(set(repos_found))[:3]
            docs_found = list(set(docs_found))[:3]
            
            if repos_found:
                response_text += "**🚀 DISCOVERED REPOSITORIES - Index with NIA for deep analysis:**\n"
                for repo in repos_found:
                    response_text += f"```\nIndex {repo}\n```\n"
                response_text += "✨ Enable AI-powered code search and architecture understanding!\n\n"
            
            if docs_found:
                response_text += "**📖 DISCOVERED DOCUMENTATION - Index with NIA for smart search:**\n"
                for doc in docs_found[:2]:  # Limit to 2 for readability
                    response_text += f"```\nIndex documentation {doc}\n```\n"
                response_text += "✨ Make documentation instantly searchable with AI Q&A!\n\n"
            
            if not repos_found and not docs_found:
                response_text += "**🔍 Manual indexing options:**\n"
                response_text += "- If you see any GitHub repos mentioned: Say \"Index [owner/repo]\"\n"
                response_text += "- If you see any documentation sites: Say \"Index documentation [url]\"\n"
                response_text += "- These will unlock NIA's powerful AI search capabilities!\n\n"
            
            response_text += "**📊 Other actions:**\n"
            response_text += "- Ask follow-up questions about the research\n"
            response_text += "- Request a different analysis format\n"
            response_text += "- Search for more specific information\n"
        else:
            response_text += "No structured data returned. The research may need a more specific query."
        
        return [TextContent(type="text", text=response_text)]
        
    except APIError as e:
        logger.error(f"API Error in deep research: {e}")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "indexing operations" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited indexing."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for unlimited access."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error in deep research: {str(e)}")
        return [TextContent(
            type="text",
            text=f"❌ Research error: {str(e)}\n\n"
                 "Try simplifying your question or using the regular nia_web_search tool."
        )]

@mcp.tool()
async def initialize_project(
    project_root: str,
    profiles: Optional[List[str]] = None
) -> List[TextContent]:
    """
    Initialize a NIA-enabled project with IDE-specific rules and configurations.
    
    This tool sets up your project with NIA integration, creating configuration files
    and rules tailored to your IDE or editor. It enables AI assistants to better
    understand and work with NIA's knowledge search capabilities.
    
    Args:
        project_root: Absolute path to the project root directory
        profiles: List of IDE profiles to set up (default: ["cursor"]). 
                 Options: cursor, vscode, claude, windsurf, cline, codex, zed, jetbrains, neovim, sublime
        
    Returns:
        Status of the initialization with created files and next steps
    
    Examples:
        - Basic: initialize_project("/path/to/project")
        - Multiple IDEs: initialize_project("/path/to/project", profiles=["cursor", "vscode"])
        - Specific IDE: initialize_project("/path/to/project", profiles=["windsurf"])
    """
    try:
        # Validate project root
        project_path = Path(project_root)
        if not project_path.is_absolute():
            return [TextContent(
                type="text",
                text=f"❌ Error: project_root must be an absolute path. Got: {project_root}"
            )]
        
        # Default to cursor profile if none specified
        if profiles is None:
            profiles = ["cursor"]
        
        # Validate profiles
        supported = get_supported_profiles()
        invalid_profiles = [p for p in profiles if p not in supported]
        if invalid_profiles:
            return [TextContent(
                type="text",
                text=f"❌ Unknown profiles: {', '.join(invalid_profiles)}\n\n"
                     f"Supported profiles: {', '.join(supported)}"
            )]
        
        logger.info(f"Initializing NIA project at {project_root} with profiles: {profiles}")
        
        # Initialize the project
        result = initialize_nia_project(
            project_root=project_root,
            profiles=profiles
        )
        
        if not result.get("success"):
            return [TextContent(
                type="text",
                text=f"❌ Failed to initialize project: {result.get('error', 'Unknown error')}"
            )]
        
        # Format success response
        response_lines = [
            f"✅ Successfully initialized NIA project at: {project_root}",
            "",
            "## 📁 Created Files:",
        ]
        
        for file in result.get("files_created", []):
            response_lines.append(f"- {file}")
        
        if result.get("profiles_initialized"):
            response_lines.extend([
                "",
                "## 🎨 Initialized Profiles:",
            ])
            for profile in result["profiles_initialized"]:
                response_lines.append(f"- {profile}")
        
        if result.get("warnings"):
            response_lines.extend([
                "",
                "## ⚠️ Warnings:",
            ])
            for warning in result["warnings"]:
                response_lines.append(f"- {warning}")
        
        if result.get("next_steps"):
            response_lines.extend([
                "",
                "## 🚀 Next Steps:",
            ])
            for i, step in enumerate(result["next_steps"], 1):
                response_lines.append(f"{i}. {step}")
        
        # Add profile-specific instructions
        response_lines.extend([
            "",
            "## 💡 Quick Start:",
        ])
        
        if "cursor" in profiles:
            response_lines.extend([
                "**For Cursor:**",
                "1. Restart Cursor to load the NIA MCP server",
                "2. Run `list_repositories` to verify connection",
                "3. Start indexing with `index_repository https://github.com/owner/repo`",
                ""
            ])
        
        if "vscode" in profiles:
            response_lines.extend([
                "**For VSCode:**",
                "1. Reload the VSCode window (Cmd/Ctrl+R)",
                "2. Open command palette (Cmd/Ctrl+Shift+P)",
                "3. Run 'NIA: Index Repository' task",
                ""
            ])
        
        if "claude" in profiles:
            response_lines.extend([
                "**For Claude Desktop:**",
                "1. The .claude directory has been created",
                "2. Claude will now understand NIA commands",
                "3. Try: 'Search for authentication patterns'",
                ""
            ])
        
        # Add general tips
        response_lines.extend([
            "## 📚 Tips:",
            "- Use natural language for searches: 'How does X work?'",
            "- Index repositories before searching them",
            "- Use `nia_web_search` to discover new repositories",
            "- Check `list_repositories` to see what's already indexed",
            "",
            "Ready to supercharge your development with AI-powered code search! 🚀"
        ])
        
        return [TextContent(
            type="text",
            text="\n".join(response_lines)
        )]
        
    except Exception as e:
        logger.error(f"Error in initialize_project tool: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error initializing project: {str(e)}\n\n"
                 "Please check:\n"
                 "- The project_root path is correct and accessible\n"
                 "- You have write permissions to the directory\n"
                 "- The NIA MCP server is properly installed"
        )]

@mcp.tool()
async def read_source_content(
    source_type: str,
    source_identifier: str,
    metadata: Optional[Dict[str, Any]] = None
) -> List[TextContent]:
    """
    Read the full content of a specific source file or document.
    
    This tool allows AI to fetch complete content from sources identified during search,
    enabling deeper analysis when the truncated search results are insufficient.
    
    Args:
        source_type: Type of source - "repository" or "documentation"
        source_identifier: 
            - For repository: "owner/repo:path/to/file.py" (e.g., "facebook/react:src/React.js")
            - For documentation: The source URL or document ID
        metadata: Optional metadata from search results to help locate the source
        
    Returns:
        Full content of the requested source with metadata
        
    Examples:
        - read_source_content("repository", "langchain-ai/langchain:libs/core/langchain_core/runnables/base.py")
        - read_source_content("documentation", "https://docs.python.org/3/library/asyncio.html")
    """
    try:
        client = await ensure_api_client()
        
        logger.info(f"Reading source content - type: {source_type}, identifier: {source_identifier}")
        
        # Call the API to get source content
        result = await client.get_source_content(
            source_type=source_type,
            source_identifier=source_identifier,
            metadata=metadata or {}
        )
        
        if not result or not result.get("success"):
            error_msg = result.get("error", "Unknown error") if result else "Failed to fetch source content"
            return [TextContent(
                type="text",
                text=f"❌ Error reading source: {error_msg}"
            )]
        
        # Format the response
        content = result.get("content", "")
        source_metadata = result.get("metadata", {})
        
        # Build response with metadata header
        response_lines = []
        
        if source_type == "repository":
            repo_name = source_metadata.get("repository", "Unknown")
            file_path = source_metadata.get("file_path", source_identifier.split(":", 1)[-1] if ":" in source_identifier else "Unknown")
            branch = source_metadata.get("branch", "main")
            
            response_lines.extend([
                f"# Source: {repo_name}",
                f"**File:** `{file_path}`",
                f"**Branch:** {branch}",
                ""
            ])
            
            if source_metadata.get("url"):
                response_lines.append(f"**GitHub URL:** {source_metadata['url']}")
                response_lines.append("")
            
            # Add file info if available
            if source_metadata.get("size"):
                response_lines.append(f"**Size:** {source_metadata['size']} bytes")
            if source_metadata.get("language"):
                response_lines.append(f"**Language:** {source_metadata['language']}")
                
            response_lines.extend(["", "## Content", ""])
            
            # Add code block with language hint
            language = source_metadata.get("language", "").lower() or "text"
            response_lines.append(f"```{language}")
            response_lines.append(content)
            response_lines.append("```")
            
        elif source_type == "documentation":
            url = source_metadata.get("url", source_identifier)
            title = source_metadata.get("title", "Documentation")
            
            response_lines.extend([
                f"# Documentation: {title}",
                f"**URL:** {url}",
                ""
            ])
            
            if source_metadata.get("last_updated"):
                response_lines.append(f"**Last Updated:** {source_metadata['last_updated']}")
                response_lines.append("")
                
            response_lines.extend(["## Content", "", content])
        
        else:
            # Generic format for unknown source types
            response_lines.extend([
                f"# Source Content",
                f"**Type:** {source_type}",
                f"**Identifier:** {source_identifier}",
                "",
                "## Content",
                "",
                content
            ])
        
        return [TextContent(type="text", text="\n".join(response_lines))]
        
    except APIError as e:
        logger.error(f"API Error reading source content: {e}")
        if e.status_code == 403 or "free tier limit" in str(e).lower():
            return [TextContent(
                type="text",
                text=f"❌ {str(e)}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited access."
            )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error reading source content: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error reading source content: {str(e)}"
        )]

# @mcp.tool()
# async def index_local_filesystem(
#     directory_path: str,
#     inclusion_patterns: Optional[List[str]] = None,
#     exclusion_patterns: Optional[List[str]] = None,
#     max_file_size_mb: int = 50
# ) -> List[TextContent]:
#     """
#     Index a local filesystem directory for intelligent search.
#
#     Args:
#         directory_path: Absolute path to the directory to index
#         inclusion_patterns: Optional list of patterns to include (e.g., ["ext:.py", "dir:src"])
#         exclusion_patterns: Optional list of patterns to exclude (e.g., ["dir:node_modules", "ext:.log"])
#         max_file_size_mb: Maximum file size in MB to process (default: 50)
#
#     Returns:
#         Status of the indexing operation
#
#     Important:
#         - Path must be absolute (e.g., /Users/username/projects/myproject)
#         - When indexing starts, use check_local_filesystem_status tool to monitor progress
#     """
#     try:
#         # Validate absolute path
#         if not os.path.isabs(directory_path):
#             return [TextContent(
#                 type="text",
#                 text=f"❌ Error: directory_path must be an absolute path. Got: {directory_path}\n\n"
#                      f"Example: /Users/username/projects/myproject"
#             )]
#
#         client = await ensure_api_client()
#
#         # Start indexing
#         logger.info(f"Starting to index local directory: {directory_path}")
#         result = await client.index_local_filesystem(
#             directory_path=directory_path,
#             inclusion_patterns=inclusion_patterns or [],
#             exclusion_patterns=exclusion_patterns or [],
#             max_file_size_mb=max_file_size_mb
#         )
#
#         if result.get("success"):
#             source_id = result["data"]["source_id"]
#             status_url = result["data"]["status_url"]
#
#             return [TextContent(
#                 type="text",
#                 text=(
#                     f"✅ Successfully started indexing local directory!\n\n"
#                     f"📁 **Directory:** `{directory_path}`\n"
#                     f"🆔 **Source ID:** `{source_id}`\n"
#                     f"📊 **Status:** Processing\n\n"
#                     f"**What happens next:**\n"
#                     f"• NIA is scanning and indexing your files in the background\n"
#                     f"• This process typically takes a few minutes depending on directory size\n"
#                     f"• Use `check_local_filesystem_status` with source ID `{source_id}` to monitor progress\n"
#                     f"• Once indexed, use `search_codebase` or `search_documentation` to search your files\n\n"
#                     f"📌 **Tip:** You can check the status at any time or visit [app.trynia.ai](https://app.trynia.ai) to monitor progress."
#                 )
#             )]
#         else:
#             return [TextContent(
#                 type="text",
#                 text=f"❌ Failed to start indexing: {result.get('detail', 'Unknown error')}"
#             )]
#
#     except APIError as e:
#         logger.error(f"API error indexing local filesystem: {e}")
#         return [TextContent(
#             type="text",
#             text=f"❌ API Error: {str(e)}\n\nStatus Code: {e.status_code}\nDetails: {e.detail}"
#         )]
#     except Exception as e:
#         logger.error(f"Unexpected error indexing local filesystem: {e}")
#         return [TextContent(
#             type="text",
#             text=f"❌ Error: An unexpected error occurred while indexing the directory: {str(e)}"
#         )]

# @mcp.tool()
# async def scan_local_filesystem(
#     directory_path: str,
#     inclusion_patterns: Optional[List[str]] = None,
#     exclusion_patterns: Optional[List[str]] = None,
#     max_file_size_mb: int = 50
# ) -> List[TextContent]:
#     """
#     Scan a local filesystem directory to preview what files would be indexed.
#
#     This tool helps you understand what files will be processed before actually indexing.
#
#     Args:
#         directory_path: Absolute path to the directory to scan
#         inclusion_patterns: Optional list of patterns to include (e.g., ["ext:.py", "dir:src"])
#         exclusion_patterns: Optional list of patterns to exclude (e.g., ["dir:node_modules", "ext:.log"])
#         max_file_size_mb: Maximum file size in MB to process (default: 50)
#
#     Returns:
#         Summary of files that would be indexed including count, size, and file types
#     """
#     try:
#         # Validate absolute path
#         if not os.path.isabs(directory_path):
#             return [TextContent(
#                 type="text",
#                 text=f"❌ Error: directory_path must be an absolute path. Got: {directory_path}\n\n"
#                      f"Example: /Users/username/projects/myproject"
#             )]
#
#         client = await ensure_api_client()
#
#         logger.info(f"Scanning local directory: {directory_path}")
#         result = await client.scan_local_filesystem(
#             directory_path=directory_path,
#             inclusion_patterns=inclusion_patterns or [],
#             exclusion_patterns=exclusion_patterns or [],
#             max_file_size_mb=max_file_size_mb
#         )
#
#         # Format the scan results
#         total_files = result.get("total_files", 0)
#         total_size_mb = result.get("total_size_mb", 0)
#         file_types = result.get("file_types", {})
#         files = result.get("files", [])
#         truncated = result.get("truncated", False)
#
#         response = f"📊 **Local Directory Scan Results**\n\n"
#         response += f"📁 **Directory:** `{directory_path}`\n"
#         response += f"📄 **Total Files:** {total_files:,}\n"
#         response += f"💾 **Total Size:** {total_size_mb:.2f} MB\n\n"
#
#         if file_types:
#             response += "**File Types:**\n"
#             # Sort by count descending
#             sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
#             for ext, count in sorted_types[:10]:  # Show top 10
#                 response += f"• `{ext}`: {count:,} files\n"
#             if len(sorted_types) > 10:
#                 response += f"• ... and {len(sorted_types) - 10} more types\n"
#             response += "\n"
#
#         if files:
#             response += f"**Largest Files (showing {min(len(files), 10)}):**\n"
#             for i, file_info in enumerate(files[:10]):
#                 size_mb = file_info["size"] / (1024 * 1024)
#                 response += f"{i+1}. `{file_info['path']}` ({size_mb:.2f} MB)\n"
#
#             if truncated:
#                 response += f"\n*Note: Showing first 100 files out of {total_files:,} total*\n"
#
#         if inclusion_patterns:
#             response += f"\n**Inclusion Patterns:** {', '.join(f'`{p}`' for p in inclusion_patterns)}\n"
#         if exclusion_patterns:
#             response += f"**Exclusion Patterns:** {', '.join(f'`{p}`' for p in exclusion_patterns)}\n"
#
#         response += "\n💡 **Next Step:** Use `index_local_filesystem` to index these files."
#
#         return [TextContent(type="text", text=response)]
#
#     except APIError as e:
#         logger.error(f"API error scanning local filesystem: {e}")
#         return [TextContent(
#             type="text",
#             text=f"❌ API Error: {str(e)}\n\nStatus Code: {e.status_code}\nDetails: {e.detail}"
#         )]
#     except Exception as e:
#         logger.error(f"Unexpected error scanning local filesystem: {e}")
#         return [TextContent(
#             type="text",
#             text=f"❌ Error: An unexpected error occurred while scanning: {str(e)}"
#         )]

# @mcp.tool()
# async def check_local_filesystem_status(source_id: str) -> List[TextContent]:
#     """
#     Check the indexing status of a local filesystem source.
#
#     Args:
#         source_id: The source ID returned when indexing was started
#
#     Returns:
#         Current status of the local filesystem indexing
#     """
#     try:
#         client = await ensure_api_client()
#         status = await client.check_local_filesystem_status(source_id)
#
#         # Format status response
#         status_text = status.get("status", "unknown")
#         progress = status.get("progress", 0)
#         message = status.get("message", "")
#         error = status.get("error")
#         directory_path = status.get("directory_path", "Unknown")
#         page_count = status.get("page_count", 0)  # Number of files
#         chunk_count = status.get("chunk_count", 0)
#
#         # Status emoji
#         status_emoji = {
#             "pending": "⏳",
#             "processing": "🔄",
#             "completed": "✅",
#             "failed": "❌",
#             "error": "❌"
#         }.get(status_text, "❓")
#
#         response = f"{status_emoji} **Local Filesystem Status**\n\n"
#         response += f"🆔 **Source ID:** `{source_id}`\n"
#         response += f"📁 **Directory:** `{directory_path}`\n"
#         response += f"📊 **Status:** {status_text.capitalize()}\n"
#
#         if progress > 0:
#             response += f"📈 **Progress:** {progress}%\n"
#
#         if message:
#             response += f"💬 **Message:** {message}\n"
#
#         if status_text == "completed":
#             response += f"\n✨ **Indexing Complete!**\n"
#             response += f"• **Files Indexed:** {page_count:,}\n"
#             response += f"• **Chunks Created:** {chunk_count:,}\n"
#             response += f"\nYou can now search this directory using `search_codebase` or the unified search!"
#         elif status_text in ["failed", "error"]:
#             response += f"\n❌ **Indexing Failed**\n"
#             if error:
#                 response += f"**Error:** {error}\n"
#             response += "\nPlease check your directory path and try again."
#         elif status_text == "processing":
#             response += f"\n🔄 Indexing is in progress...\n"
#             response += "Check back in a few moments or monitor at [app.trynia.ai](https://app.trynia.ai)"
#
#         return [TextContent(type="text", text=response)]
#
#     except APIError as e:
#         logger.error(f"API error checking local filesystem status: {e}")
#         if e.status_code == 404:
#             return [TextContent(
#                 type="text",
#                 text=f"❌ Source ID `{source_id}` not found. Please check the ID and try again."
#             )]
#         return [TextContent(
#             type="text",
#             text=f"❌ API Error: {str(e)}\n\nStatus Code: {e.status_code}\nDetails: {e.detail}"
#         )]
#     except Exception as e:
#         logger.error(f"Unexpected error checking local filesystem status: {e}")
#         return [TextContent(
#             type="text",
#             text=f"❌ Error: An unexpected error occurred: {str(e)}"
#         )]

# @mcp.tool()
# async def search_local_filesystem(
#     source_id: str,
#     query: str,
#     include_sources: bool = True
# ) -> List[TextContent]:
#     """
#     Search an indexed local filesystem directory using its source ID.
#
#     To search local files:
#     1. First index a directory using `index_local_filesystem` - this will return a source_id
#     2. Use that source_id with this tool to search the indexed content
#
#     Args:
#         source_id: The source ID returned when the directory was indexed (required)
#         query: Your search query in natural language (required)
#         include_sources: Whether to include source code snippets in results (default: True)
#
#     Returns:
#         Search results with relevant file snippets and explanations
#
#     Example:
#         # After indexing returns source_id "abc123-def456"
#         search_local_filesystem(
#             source_id="abc123-def456",
#             query="configuration settings"
#         )
#
#     Note: To find your source IDs, use `list_documentation` and look for
#     sources with source_type="local_filesystem"
#     """
#     try:
#         # Validate inputs
#         if not source_id:
#             return [TextContent(
#                 type="text",
#                 text="❌ Error: 'source_id' parameter is required. Use the ID returned from index_local_filesystem."
#             )]
#
#         if not query:
#             return [TextContent(
#                 type="text",
#                 text="❌ Error: 'query' parameter is required"
#             )]
#
#         client = await ensure_api_client()
#
#         # Check if the source exists and is ready
#         logger.info(f"Checking status of source {source_id}")
#         try:
#             status = await client.get_data_source_status(source_id)
#             if not status:
#                 return [TextContent(
#                     type="text",
#                     text=f"❌ Source ID '{source_id}' not found. Please check the ID and try again."
#                 )]
#
#             source_status = status.get("status", "unknown")
#             if source_status == "processing":
#                 progress = status.get("progress", 0)
#                 return [TextContent(
#                     type="text",
#                     text=f"⏳ This source is still being indexed ({progress}% complete).\n\n"
#                          f"Use `check_local_filesystem_status(\"{source_id}\")` to check progress."
#                 )]
#             elif source_status == "failed":
#                 error = status.get("error", "Unknown error")
#                 return [TextContent(
#                     type="text",
#                     text=f"❌ This source failed to index.\n\nError: {error}"
#                 )]
#             elif source_status != "completed":
#                 return [TextContent(
#                     type="text",
#                     text=f"❌ Source is not ready for search. Status: {source_status}"
#                 )]
#         except Exception as e:
#             logger.warning(f"Could not check source status: {e}")
#             # Continue anyway in case it's just a status check issue
#
#         # Perform the search
#         logger.info(f"Searching local filesystem source {source_id} with query: {query}")
#
#         # Use the unified query endpoint with data_sources parameter
#         result = client.query_unified(
#             messages=[{"role": "user", "content": query}],
#             data_sources=[source_id],
#             include_sources=include_sources,
#             stream=False
#         )
#
#         # Parse the response
#         response_text = ""
#         async for chunk in result:
#             data = json.loads(chunk)
#             if "content" in data:
#                 response_text = data["content"]
#                 sources = data.get("sources", [])
#                 break
#
#         # Format the response nicely for local filesystem results
#         if response_text:
#             # Extract the local filesystem results section if present
#             if "**Local filesystem results" in response_text:
#                 # Keep the original response
#                 formatted_response = response_text
#             else:
#                 # Create our own formatted response
#                 formatted_response = f"🔍 **Search Results for Local Directory**\n"
#                 formatted_response += f"🔎 Query: \"{query}\"\n\n"
#                 formatted_response += response_text
#
#             # Add sources if available and requested
#             if include_sources and sources:
#                 formatted_response += "\n\n**📄 Source Details:**\n"
#                 for i, source in enumerate(sources[:5], 1):
#                     metadata = source.get("metadata", {})
#                     file_path = metadata.get("file_path", "Unknown file")
#                     formatted_response += f"\n{i}. `{file_path}`\n"
#
#                     # Add snippet of content
#                     content = source.get("content", "")
#                     if content:
#                         # Truncate to reasonable length
#                         lines = content.split('\n')[:10]
#                         snippet = '\n'.join(lines)
#                         if len(lines) > 10:
#                             snippet += "\n..."
#                         formatted_response += f"```\n{snippet}\n```\n"
#
#             return [TextContent(type="text", text=formatted_response)]
#         else:
#             return [TextContent(
#                 type="text",
#                 text=f"No results found for query: \"{query}\" in the indexed directory."
#             )]
#
#     except APIError as e:
#         logger.error(f"API error searching local filesystem: {e}")
#         return [TextContent(
#             type="text",
#             text=f"❌ API Error: {str(e)}\n\nStatus Code: {e.status_code}\nDetails: {e.detail}"
#         )]
#     except Exception as e:
#         logger.error(f"Unexpected error searching local filesystem: {e}")
#         return [TextContent(
#             type="text",
#             text=f"❌ Error: An unexpected error occurred: {str(e)}"
#         )]

# ===============================================================================
# CHROMA PACKAGE SEARCH INTEGRATION
# ===============================================================================
#
# Provides access to Chroma's Package Search MCP tools for searching actual
# source code from 3,000+ packages across multiple package registries.
# This integration enables AI assistants to search ground-truth code instead
# of relying on training data or hallucinations.
#
# Available Registries:
#   - py_pi: Python Package Index (PyPI) packages
#   - npm: Node.js packages from NPM registry
#   - crates_io: Rust packages from crates.io
#   - golang_proxy: Go modules from Go proxy
#
# Authentication:
#   - Requires CHROMA_API_KEY environment variable
#   - Uses x-chroma-token header for API authentication
#
# Tools:
#   1. nia_package_search_grep: Regex-based code search
#   2. nia_package_search_hybrid: Semantic/AI-powered search
#   3. nia_package_search_read_file: Direct file content retrieval
#
# ===============================================================================

@mcp.tool()
async def nia_package_search_grep(
    registry: str,
    package_name: str,
    pattern: str,
    version: Optional[str] = None,
    language: Optional[str] = None,
    filename_sha256: Optional[str] = None,
    a: Optional[int] = None,
    b: Optional[int] = None,
    c: Optional[int] = None,
    head_limit: Optional[int] = None,
    output_mode: str = "content"
) -> List[TextContent]:
    """
    Executes a grep over the source code of a public package. This tool is useful for deterministically
    finding code in a package using regex. Use this tool before implementing solutions that use external
    packages. The regex pattern should be restrictive enough to only match code you're looking for, to limit
    overfetching.

    Required Args: "registry", "package_name", "pattern" Optional Args: "version", "language",
    "filename_sha256", "a", "b", "c", "head_limit", "output_mode"

    Best for: Deterministic code search, finding specific code patterns, or exploring code structure.

    Parameters:
        a: The number of lines after a grep match to include
        b: The number of lines before a grep match to include
        c: The number of lines before and after a grep match to include
        filename_sha256: The sha256 hash of the file to filter for
        head_limit: Limits number of results returned. If the number of results returned is less than the
            head limit, all results have been returned.
        language: The languages to filter for. If not provided, all languages will be searched. Valid
            options: "Rust", "Go", "Python", "JavaScript", "JSX", "TypeScript", "TSX", "HTML", "Markdown",
            "YAML", "Bash", "SQL", "JSON", "Text", "Dockerfile", "HCL", "Protobuf", "Make", "Toml", "Jupyter Notebook"
        output_mode: Controls the shape of the grep output. Accepted values:
            "content" (default): return content snippets with line ranges
            "files_with_matches": return unique files (path and sha256) that match
            "count": return files with the count of matches per file
        package_name: The name of the requested package. Pass the name as it appears in the package
            manager. For Go packages, use the GitHub organization and repository name in the format
            {org}/{repo}, if unsure check the GitHub URL for the package and use {org}/{repo} from that URL.
        pattern: The regex pattern for exact text matching in the codebase. Must be a valid regex.
            Example: "func\\s+\\(get_repository\\|getRepository\\)\\s*\\(.*?\\)\\s\\{"
        registry: The name of the registry containing the requested package. Must be one of:
            "crates_io", "golang_proxy", "npm", or "py_pi".
        version: Optionally, the specific version of the package whose source code to search.
            If provided, must be in semver format: {major}.{minor}.{patch}. Otherwise, the latest indexed
            version of the package available will be used.
    """
    try:
        # Use API client for backend routing
        client = await ensure_api_client()
        logger.info(f"Searching package {package_name} from {registry} with pattern: {pattern}")

        # Execute grep search through backend
        result = await client.package_search_grep(
            registry=registry,
            package_name=package_name,
            pattern=pattern,
            version=version,
            language=language,
            filename_sha256=filename_sha256,
            a=a,
            b=b,
            c=c,
            head_limit=head_limit,
            output_mode=output_mode
        )

        # Handle raw Chroma JSON response
        if not result or not isinstance(result, dict):
            return [TextContent(
                type="text",
                text=f"No response from Chroma for pattern '{pattern}' in {package_name} ({registry})"
            )]

        # Extract results and version from raw Chroma response
        results = result.get("results", [])
        version_used = result.get("version_used")

        if not results:
            return [TextContent(
                type="text",
                text=f"No matches found for pattern '{pattern}' in {package_name} ({registry})"
            )]

        response_lines = [
            f"# 🔍 Package Search Results: {package_name} ({registry})",
            f"**Pattern:** `{pattern}`",
            ""
        ]

        if version_used:
            response_lines.append(f"**Version:** {version_used}")
        elif version:
            response_lines.append(f"**Version:** {version}")

        response_lines.append(f"**Found {len(results)} matches**\n")

        # Handle grep result format: {output_mode: "content", result: {content, file_path, start_line, etc}}
        for i, item in enumerate(results, 1):
            response_lines.append(f"## Match {i}")

            # Extract data from Chroma grep format
            if "result" in item:
                result_data = item["result"]
                if result_data.get("file_path"):
                    response_lines.append(f"**File:** `{result_data['file_path']}`")

                # Show SHA256 for read_file tool usage
                if result_data.get("filename_sha256"):
                    response_lines.append(f"**SHA256:** `{result_data['filename_sha256']}`")

                if result_data.get("start_line") and result_data.get("end_line"):
                    response_lines.append(f"**Lines:** {result_data['start_line']}-{result_data['end_line']}")
                if result_data.get("language"):
                    response_lines.append(f"**Language:** {result_data['language']}")

                response_lines.append("```")
                response_lines.append(result_data.get("content", ""))
                response_lines.append("```\n")
            else:
                # Fallback for other formats
                response_lines.append("```")
                response_lines.append(str(item))
                response_lines.append("```\n")

        # Add truncation message if present
        if result.get("truncation_message"):
            response_lines.append(f"⚠️ **Note:** {result['truncation_message']}")

        # Add usage hint for read_file workflow (grep tool)
        response_lines.append("\n💡 **To read full file content:**")
        response_lines.append("Copy a SHA256 above and use: `nia_package_search_read_file(registry=..., package_name=..., filename_sha256=\"...\", start_line=1, end_line=100)`")

        return [TextContent(type="text", text="\n".join(response_lines))]

    except Exception as e:
        logger.error(f"Error in package search grep: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error searching package: {str(e)}\n\n"
                 f"Make sure:\n"
                 f"- The registry is one of: crates_io, golang_proxy, npm, py_pi\n"
                 f"- The package name is correct\n"
                 f"- The pattern is a valid regex"
        )]

@mcp.tool()
async def nia_package_search_hybrid(
    registry: str,
    package_name: str,
    semantic_queries: List[str],
    version: Optional[str] = None,
    filename_sha256: Optional[str] = None,
    pattern: Optional[str] = None,
    language: Optional[str] = None
) -> List[TextContent]:
    """
    Searches package source code using semantic understanding AND optionally regex patterns. This
    allows for hybrid search, allowing for prefiltering with regex, and semantic ranking.

    Required Args: "registry", "package_name", "semantic_queries"

    Optional Args: "version", "filename_sha256", "pattern", "language"

    Best for: Understanding how packages implement specific features, finding usage patterns, or
    exploring code structure.

    Parameters:
        filename_sha256: The sha256 hash of the file to filter for
        language: The languages to filter for. If not provided, all languages will be searched. Valid
            options: "Rust", "Go", "Python", "JavaScript", "JSX", "TypeScript", "TSX", "HTML", "Markdown",
            "YAML", "Bash", "SQL", "JSON", "Text", "Dockerfile", "HCL", "Protobuf", "Make", "Toml", "Jupyter Notebook"
        package_name: The name of the requested package. Pass the name as it appears in the package
            manager. For Go packages, use the GitHub organization and repository name in the format
            {org}/{repo}, if unsure check the GitHub URL for the package and use {org}/{repo} from that URL.
        pattern: The regex pattern for exact text matching in the codebase. Must be a valid regex.
            Example: "func\\s+\\(get_repository\\|getRepository\\)\\s*\\(.*?\\)\\s\\{"
        registry: The name of the registry containing the requested package. Must be one of:
            "crates_io", "golang_proxy", "npm", or "py_pi".
        semantic_queries: Array of 1-5 plain English questions about the codebase. Example: ["how is
            argmax implemented in numpy?", "what testing patterns does axum use?"]
        version: Optionally, the specific version of the package whose source code to search.
            If provided, must be in semver format: {major}.{minor}.{patch}. Otherwise, the latest indexed
            version of the package available will be used.
    """
    try:
        # Use API client for backend routing
        client = await ensure_api_client()
        logger.info(f"Hybrid search in {package_name} from {registry} with queries: {semantic_queries}")

        # Execute hybrid search through backend
        result = await client.package_search_hybrid(
            registry=registry,
            package_name=package_name,
            semantic_queries=semantic_queries,
            version=version,
            filename_sha256=filename_sha256,
            pattern=pattern,
            language=language
        )

        # Handle raw Chroma JSON response
        if not result or not isinstance(result, dict):
            queries_str = "\n".join(f"- {q}" for q in semantic_queries)
            return [TextContent(
                type="text",
                text=f"No response from Chroma for queries:\n{queries_str}\n\nin {package_name} ({registry})"
            )]

        # Extract results and version from raw Chroma response
        results = result.get("results", [])
        version_used = result.get("version_used")

        if not results:
            queries_str = "\n".join(f"- {q}" for q in semantic_queries)
            return [TextContent(
                type="text",
                text=f"No relevant code found for queries:\n{queries_str}\n\nin {package_name} ({registry})"
            )]

        response_lines = [
            f"# 🔎 Package Semantic Search: {package_name} ({registry})",
            "**Queries:**"
        ]

        for query in semantic_queries:
            response_lines.append(f"- {query}")

        response_lines.append("")

        if version_used:
            response_lines.append(f"**Version:** {version_used}")
        elif version:
            response_lines.append(f"**Version:** {version}")
        if pattern:
            response_lines.append(f"**Pattern Filter:** `{pattern}`")

        response_lines.append(f"\n**Found {len(results)} relevant code sections**\n")

        # Handle hybrid result format: {id: "...", document: "content", metadata: {...}}
        for i, item in enumerate(results, 1):
            response_lines.append(f"## Result {i}")

            # Extract metadata if available
            metadata = item.get("metadata", {})
            if metadata.get("filename"):
                response_lines.append(f"**File:** `{metadata['filename']}`")

            # Show SHA256 for read_file tool usage (from metadata)
            if metadata.get("filename_sha256"):
                response_lines.append(f"**SHA256:** `{metadata['filename_sha256']}`")

            if metadata.get("start_line") and metadata.get("end_line"):
                response_lines.append(f"**Lines:** {metadata['start_line']}-{metadata['end_line']}")
            if metadata.get("language"):
                response_lines.append(f"**Language:** {metadata['language']}")

            # Get document content
            content = item.get("document", "")
            if content:
                response_lines.append("```")
                response_lines.append(content)
                response_lines.append("```\n")

        # Add truncation message if present
        if result.get("truncation_message"):
            response_lines.append(f"⚠️ **Note:** {result['truncation_message']}")

        # Add usage hint for read_file workflow (hybrid tool)
        response_lines.append("\n💡 **To read full file content:**")
        response_lines.append("Copy a SHA256 above and use: `nia_package_search_read_file(registry=..., package_name=..., filename_sha256=\"...\", start_line=1, end_line=100)`")

        return [TextContent(type="text", text="\n".join(response_lines))]

    except Exception as e:
        logger.error(f"Error in package search hybrid: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error in hybrid search: {str(e)}\n\n"
                 f"Make sure:\n"
                 f"- The registry is one of: crates_io, golang_proxy, npm, py_pi\n"
                 f"- The package name is correct\n"
                 f"- Semantic queries are provided (1-5 queries)"
        )]

@mcp.tool()
async def nia_package_search_read_file(
    registry: str,
    package_name: str,
    filename_sha256: str,
    start_line: int,
    end_line: int,
    version: Optional[str] = None
) -> List[TextContent]:
    """
    Reads exact lines from a source file of a public package. Useful for fetching specific code regions by
    line range.

    Required Args: "registry", "package_name", "filename_sha256", "start_line", "end_line" Optional Args:
    "version"

    Best for: Inspecting exact code snippets when you already know the file and line numbers. Max 200
    lines.

    Parameters:
        end_line: 1-based inclusive end line to read
        filename_sha256: The sha256 hash of the file to filter for
        package_name: The name of the requested package. Pass the name as it appears in the package
            manager. For Go packages, use the GitHub organization and repository name in the format
            {org}/{repo}, if unsure check the GitHub URL for the package and use {org}/{repo} from that URL.
        registry: The name of the registry containing the requested package. Must be one of:
            "crates_io", "golang_proxy", "npm", or "py_pi".
        start_line: 1-based inclusive start line to read
        version: Optionally, the specific version of the package whose source code to search.
            If provided, must be in semver format: {major}.{minor}.{patch}. Otherwise, the latest indexed
            version of the package available will be used.
    """
    try:
        # Validate line range
        if end_line - start_line + 1 > 200:
            return [TextContent(
                type="text",
                text="❌ Error: Maximum 200 lines can be read at once. Please reduce the line range."
            )]

        if start_line < 1 or end_line < start_line:
            return [TextContent(
                type="text",
                text="❌ Error: Invalid line range. Start line must be >= 1 and end line must be >= start line."
            )]

        # Use API client for backend routing
        client = await ensure_api_client()
        logger.info(f"Reading file from {package_name} ({registry}): sha256={filename_sha256}, lines {start_line}-{end_line}")

        # Read file content through backend
        result = await client.package_search_read_file(
            registry=registry,
            package_name=package_name,
            filename_sha256=filename_sha256,
            start_line=start_line,
            end_line=end_line,
            version=version
        )

        # Handle raw Chroma response (read_file typically returns content directly)
        response_lines = [
            f"# 📄 Package File Content: {package_name} ({registry})",
            f"**File SHA256:** `{filename_sha256}`",
            f"**Lines:** {start_line}-{end_line}"
        ]

        if version:
            response_lines.append(f"**Version:** {version}")

        response_lines.append("\n```")
        # For read_file, Chroma typically returns the content directly as a string
        if isinstance(result, str):
            response_lines.append(result)
        elif isinstance(result, dict) and result.get("content"):
            response_lines.append(result["content"])
        else:
            response_lines.append(str(result))
        response_lines.append("```")

        return [TextContent(type="text", text="\n".join(response_lines))]

    except Exception as e:
        logger.error(f"Error reading package file: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error reading file: {str(e)}\n\n"
                 f"Make sure:\n"
                 f"- The registry is one of: crates_io, golang_proxy, npm, py_pi\n"
                 f"- The package name is correct\n"
                 f"- The filename_sha256 is valid\n"
                 f"- The line range is valid (1-based, max 200 lines)"
        )]

@mcp.tool()
async def visualize_codebase(
    repository: str
) -> List[TextContent]:
    """
    Open the graph visualization for an indexed repository in a browser.
    
    This tool launches a browser with the interactive graph visualization
    that shows the code structure, relationships, and dependencies of
    the indexed codebase.
    
    Args:
        repository: Repository in owner/repo format (e.g., "facebook/react")
        
    Returns:
        Status message with the URL that was opened
        
    Examples:
        - visualize_codebase("facebook/react")
        - visualize_codebase("langchain-ai/langchain")
    """
    try:
        client = await ensure_api_client()
        
        logger.info(f"Looking up repository: {repository}")
        
        # List all repositories to find the matching one
        repositories = await client.list_repositories()
        
        # Find the repository by name
        matching_repo = None
        for repo in repositories:
            if repo.get("repository") == repository:
                matching_repo = repo
                break
        
        if not matching_repo:
            # Try case-insensitive match as fallback
            repository_lower = repository.lower()
            for repo in repositories:
                if repo.get("repository", "").lower() == repository_lower:
                    matching_repo = repo
                    break
        
        if not matching_repo:
            return [TextContent(
                type="text",
                text=f"❌ Repository '{repository}' not found.\n\n"
                     f"Available repositories:\n" +
                     "\n".join(f"- {r.get('repository')}" for r in repositories if r.get('repository')) +
                     "\n\nUse `list_repositories` to see all indexed repositories."
            )]
        
        # Check if the repository is fully indexed
        status = matching_repo.get("status", "unknown")
        # Use the actual project ID if available, fall back to repository_id
        repository_id = matching_repo.get("id") or matching_repo.get("repository_id")
        
        if not repository_id:
            return [TextContent(
                type="text",
                text=f"❌ No repository ID found for '{repository}'. This may be a data inconsistency."
            )]
        
        if status != "completed":
            warning_msg = f"⚠️ Note: Repository '{repository}' is currently {status}.\n"
            if status == "indexing":
                warning_msg += "The visualization may show incomplete data.\n\n"
            elif status == "error":
                error_msg = matching_repo.get("error", "Unknown error")
                warning_msg += f"Error: {error_msg}\n\n"
            else:
                warning_msg += "The visualization may not be available.\n\n"
        else:
            warning_msg = ""
        
        # Determine the base URL based on the API URL
        api_base_url = client.base_url
        if "localhost" in api_base_url or "127.0.0.1" in api_base_url:
            # Local development
            app_base_url = "http://localhost:3000"
        else:
            # Production
            app_base_url = "https://app.trynia.ai"
        
        # Construct the visualization URL
        visualization_url = f"{app_base_url}/visualize/{repository_id}"
        
        # Try to open the browser
        try:
            webbrowser.open(visualization_url)
            browser_opened = True
            open_msg = "✅ Opening graph visualization in your default browser..."
        except Exception as e:
            logger.warning(f"Failed to open browser: {e}")
            browser_opened = False
            open_msg = "⚠️ Could not automatically open browser."
        
        # Format the response
        response_lines = [
            f"# Graph Visualization: {repository}",
            "",
            warning_msg if warning_msg else "",
            open_msg,
            "",
            f"**URL:** {visualization_url}",
            "",
        ]
        
        if matching_repo.get("display_name"):
            response_lines.append(f"**Display Name:** {matching_repo['display_name']}")
        
        response_lines.extend([
            f"**Branch:** {matching_repo.get('branch', 'main')}",
            f"**Status:** {status}",
            "",
            "## Features Available:",
            "- 🔍 Interactive force-directed graph",
            "- 🎨 Color-coded node types (functions, classes, files, etc.)",
            "- 🔗 Relationship visualization (calls, imports, inherits, etc.)",
            "- 💬 Click on any node to chat with that specific code element",
            "- 🔎 Search and filter capabilities",
            "- 📊 Graph statistics and insights"
        ])
        
        if not browser_opened:
            response_lines.extend([
                "",
                "**Manual Access:**",
                f"Copy and paste this URL into your browser: {visualization_url}"
            ])
        
        return [TextContent(
            type="text",
            text="\n".join(response_lines)
        )]
        
    except APIError as e:
        logger.error(f"API Error in visualize_codebase: {e}")
        if e.status_code == 403 or "free tier limit" in str(e).lower():
            return [TextContent(
                type="text",
                text=f"❌ {str(e)}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for unlimited access."
            )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error in visualize_codebase: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error opening visualization: {str(e)}"
        )]

# Resources

# Note: FastMCP doesn't have list_resources or read_resource decorators
# Resources should be registered individually using @mcp.resource()
# For now, commenting out these functions as they use incorrect decorators

# @mcp.list_resources
# async def list_resources() -> List[Resource]:
#     """List available repositories as resources."""
#     try:
#         client = await ensure_api_client()
#         repositories = await client.list_repositories()
#         
#         resources = []
#         for repo in repositories:
#             if repo.get("status") == "completed":
#                 resources.append(Resource(
#                     uri=f"nia://repository/{repo['repository']}",
#                     name=repo["repository"],
#                     description=f"Indexed repository at branch {repo.get('branch', 'main')}",
#                     mimeType="application/x-nia-repository"
#                 ))
#         
#         return resources
#     except Exception as e:
#         logger.error(f"Error listing resources: {e}")
#         return []

# @mcp.read_resource
# async def read_resource(uri: str) -> TextContent:
#     """Read information about a repository resource."""
#     if not uri.startswith("nia://repository/"):
#         return TextContent(
#             type="text",
#             text=f"Unknown resource URI: {uri}"
#         )
#     
#     repository = uri.replace("nia://repository/", "")
#     
#     try:
#         client = await ensure_api_client()
#         status = await client.get_repository_status(repository)
#         
#         if not status:
#             return TextContent(
#                 type="text",
#                 text=f"Repository not found: {repository}"
#             )
#         
#         # Format repository information
#         lines = [
#             f"# Repository: {repository}",
#             "",
#             f"**Status:** {status['status']}",
#             f"**Branch:** {status.get('branch', 'main')}",
#         ]
#         
#         if status.get("indexed_at"):
#             lines.append(f"**Indexed:** {status['indexed_at']}")
#         
#         lines.extend([
#             "",
#             "## Usage",
#             f"Search this repository using the `search_codebase` tool with:",
#             f'`repositories=["{repository}"]`'
#         ])
#         
#         return TextContent(type="text", text="\n".join(lines))
#         
#     except Exception as e:
#         logger.error(f"Error reading resource: {e}")
#         return TextContent(
#             type="text",
#             text=f"Error reading resource: {str(e)}"
#         )

# Server lifecycle

async def cleanup():
    """Cleanup resources on shutdown."""
    global api_client
    if api_client:
        await api_client.close()
        api_client = None

def run():
    """Run the MCP server."""
    try:
        # Check for API key early
        get_api_key()
        
        logger.info("Starting NIA MCP Server")
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        # Run cleanup
        loop = asyncio.new_event_loop()
        loop.run_until_complete(cleanup())
        loop.close()