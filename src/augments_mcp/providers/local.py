"""Local file system documentation provider."""

import os
import re
from typing import Optional, List, Dict, Any
from pathlib import Path
import structlog

from .base import BaseProvider

logger = structlog.get_logger(__name__)


class LocalProvider(BaseProvider):
    """Provider for fetching documentation from local file system."""

    def __init__(self, base_path: Optional[str] = None):
        """Initialize Local provider.
        
        Args:
            base_path: Optional base path to restrict access to (security)
        """
        self.base_path = Path(base_path).resolve() if base_path else None
        logger.info("Local provider initialized", base_path=str(self.base_path) if self.base_path else "unrestricted")

    async def close(self):
        """Close resources."""
        # Nothing to close for local file system
        pass

    async def fetch_documentation(
        self,
        path: str,
        target_path: Optional[str] = None
    ) -> Optional[str]:
        """Fetch documentation content from a local directory or file.
        
        Args:
            path: Path to the documentation directory or file
            target_path: Optional specific sub-path within the documentation
            
        Returns:
            Formatted documentation content or None if not found
        """
        try:
            # Resolve path
            full_path = Path(path).resolve()
            
            if target_path:
                full_path = full_path / target_path
                
            # Security check: ensure we haven't escaped the base path if set
            if self.base_path:
                try:
                    full_path.relative_to(self.base_path)
                except ValueError:
                    logger.warning("Attempted to access path outside base path", path=str(full_path), base=str(self.base_path))
                    return None
            
            if not full_path.exists():
                logger.warning("Local documentation path not found", path=str(full_path))
                return None
                
            if full_path.is_file():
                return self._format_single_file(full_path)
            
            # Process directory
            documentation_parts = []
            
            # Sort files to prioritize common documentation files
            priority_files = ["README.md", "index.md", "introduction.md", "getting-started.md"]
            regular_files = []
            
            # List directory contents
            try:
                found_files = []
                for ext in ['*.md', '*.mdx']:
                    found_files.extend(full_path.rglob(ext))

                for item in found_files:
                    if item.is_file():
                        if item.name in priority_files:
                            # Add with priority
                            priority_index = priority_files.index(item.name)
                            documentation_parts.append((priority_index, item))
                        else:
                            regular_files.append(item)
            except Exception as e:
                logger.error("Error listing directory", path=str(full_path), error=str(e))
                return None
            
            # Sort priority files and add regular files
            documentation_parts.sort(key=lambda x: x[0])
            priority_items = [item for _, item in documentation_parts]
            
            # Limit to prevent overwhelming output
            all_files = priority_items + regular_files[:30]
            
            # Read content for each file
            content_parts = []
            for file_path in all_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    formatted_content = self._format_file_content(
                        content, 
                        str(file_path.relative_to(full_path)),
                        str(file_path)
                    )
                    content_parts.append(formatted_content)
                except Exception as e:
                    logger.warning("Failed to read file", file=str(file_path), error=str(e))
            
            if not content_parts:
                logger.warning("No readable documentation files found", path=str(full_path))
                return None
            
            # Combine all parts
            header = f"# Documentation from {path}\n"
            if target_path:
                header += f"**Path:** {target_path}\n"
            header += "\n"
            
            full_content = header + "\n\n".join(content_parts)
            
            logger.info("Local documentation fetched successfully", 
                       path=str(full_path), 
                       files=len(content_parts))
            
            return full_content
            
        except Exception as e:
            logger.error("Local documentation fetch failed", 
                        path=path, 
                        error=str(e))
            return None

    async def fetch_examples(
        self,
        path: str,
        target_path: Optional[str] = None,
        pattern: Optional[str] = None
    ) -> Optional[str]:
        """Fetch code examples from a local directory.
        
        Args:
            path: Path to the examples directory
            target_path: Optional specific sub-path
            pattern: Specific pattern to search for
            
        Returns:
            Formatted examples content or None if not found
        """
        try:
            # Resolve path
            full_path = Path(path).resolve()
            
            if target_path:
                full_path = full_path / target_path
                
            # Security check
            if self.base_path:
                try:
                    full_path.relative_to(self.base_path)
                except ValueError:
                    return None
            
            if not full_path.exists() or not full_path.is_dir():
                return None
            
            # Filter for code files
            code_extensions = ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.go', '.rs', '.cpp', '.c']
            example_files = []
            
            try:
                for item in full_path.rglob("*"): # Recursive search might be better for examples
                    if item.is_file():
                        file_name = item.name.lower()
                        
                        # Check if it's a code file
                        if any(file_name.endswith(ext) for ext in code_extensions):
                            # If pattern is specified, filter by pattern
                            if pattern:
                                if pattern.lower() in file_name or pattern.lower() in str(item).lower():
                                    example_files.append(item)
                            else:
                                example_files.append(item)
            except Exception as e:
                logger.error("Error scanning for examples", path=str(full_path), error=str(e))
                return None
            
            if not example_files:
                return None
            
            # Limit number of files to process
            example_files = example_files[:5]
            
            # Fetch content for each example file
            examples_parts = []
            for file_path in example_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Detect language for syntax highlighting
                    language = self._detect_language(file_path.name)
                    
                    rel_path = file_path.relative_to(full_path)
                    formatted_example = f"### {rel_path}\n\n"
                    formatted_example += f"```{language}\n{content}\n```\n"
                    
                    examples_parts.append(formatted_example)
                except Exception as e:
                    logger.warning("Failed to read example file", file=str(file_path), error=str(e))
            
            if not examples_parts:
                return None
            
            # Combine all examples
            header = f"# Examples from {path}\n"
            if target_path:
                header += f"**Path:** {target_path}\n"
            if pattern:
                header += f"**Pattern:** {pattern}\n"
            header += "\n"
            
            full_content = header + "\n".join(examples_parts)
            
            logger.info("Local examples fetched successfully", 
                       path=str(full_path), 
                       pattern=pattern,
                       files=len(examples_parts))
            
            return full_content
            
        except Exception as e:
            logger.error("Local examples fetch failed", 
                        path=path, 
                        pattern=pattern,
                        error=str(e))
            return None

    def _format_single_file(self, file_path: Path) -> str:
        """Format content from a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Clean up the content
            content = self._clean_markdown(content)
            
            # Add file header if it doesn't already have one
            if not content.strip().startswith('#'):
                content = f"# {file_path.name}\n\n{content}"
            
            return content
        except Exception as e:
            logger.error("Failed to format single file", file=str(file_path), error=str(e))
            return ""

    def _format_file_content(self, content: str, file_name: str, file_path: str) -> str:
        """Format content from a specific file."""
        content = self._clean_markdown(content)
        
        # Add section header
        section_title = file_name.replace('.md', '').replace('.mdx', '').replace('-', ' ').title()
        formatted_content = f"## {section_title}\n\n{content}"
        
        return formatted_content

    def _clean_markdown(self, content: str) -> str:
        """Clean and normalize markdown content."""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        return content.strip()

    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        ext_map = {
            '.js': 'javascript',
            '.jsx': 'jsx', 
            '.ts': 'typescript',
            '.tsx': 'tsx',
            '.py': 'python',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        for ext, lang in ext_map.items():
            if filename.lower().endswith(ext):
                return lang
        
        return 'text'

