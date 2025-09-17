"""AST operation tools for MCP server."""

import logging
from typing import Any, Dict, Optional, List, SupportsAbs

from mcp_server_tree_sitter.config import ConfigurationManager, SummarizationConfig
from mcp_server_tree_sitter.di import get_container
from pydantic import BaseModel
from unicodedata import category

from ..exceptions import FileAccessError, ParsingError
from ..models.ast import node_to_dict
from ..utils.file_io import read_binary_file
from ..utils.security import validate_file_access
from ..utils.tree_sitter_helpers import (
    parse_source,
)
from ..utils.tree_sitter_types import Node

logger = logging.getLogger(__name__)


class TocEntry(BaseModel):
    name: str
    category: str
    start_line: int
    end_line: int


#unmergeable_nodes: List[str] = {"class_definition", "function_definition", "subroutine_declaration_statement"}
#important_nodes: List[str] = {"comment", "import"}
#individually_named_nodes: List[str] = {"class_definition", "function_definition", "subroutine_declaration_statement"}
#identifier_types: List[str] = {"identifier", "bareword"}


def classify_block(grammar_name: str, summarization_config: SummarizationConfig) -> str:
    if grammar_name in summarization_config.important_nodes:
        return grammar_name
    if grammar_name in summarization_config.nongeneric_nodes:
        return grammar_name
    return "code_block"

def get_individual_name(node: Node, summarization_config: SummarizationConfig) -> Optional[str]:
    if node.grammar_name in summarization_config.identifier_types:
        if isinstance(node.text, str):
            return node.text
        if isinstance(node.text, bytes):
            return node.text.decode()

    for child in node.children:
        result = get_individual_name(child, summarization_config)
        if result is not None:
            return result

    return None

def summarize_tree(root_node: Node, summarization_config: SummarizationConfig) -> List[TocEntry]:
    result: List[TocEntry] = []
    toc_entry = None
    for node in root_node.children:
        node_type = classify_block(node.grammar_name, summarization_config)
        start_line = node.range.start_point.row
        end_line = node.range.end_point.row
        children_types = []
        individual_name = None
        if node.grammar_name in summarization_config.individually_named_nodes:
            individual_name = get_individual_name(node, summarization_config)
        if not individual_name:
            individual_name = f"{start_line}"

        node_name = f"{node_type}_{individual_name}"
        if not toc_entry:
            toc_entry = TocEntry(category=node_type, name=node_name,  start_line=start_line, end_line=end_line)
            continue

        if node.grammar_name == "comment" and toc_entry.category != "comment" and toc_entry.end_line == end_line:
            # skip inline comments inside blocks
            continue

        if toc_entry.category == node_type and node_type not in summarization_config.important_nodes:
            # Extend current TOC entry
            toc_entry.end_line = end_line
            continue

        result.append(toc_entry)
        toc_entry = TocEntry(category=node_type, name=node_name, start_line=start_line, end_line=end_line)

    if toc_entry:
        result.append(toc_entry)
    return result


def get_file_ast_toc(
        project: Any,
        path: str,
        language_registry: Any,
        tree_cache: Any
) -> Dict[str, any]:
    """
    Get the AST table of content with collapsed non-essential blocks.

    Args:
        project: Project object
        path: File path (relative to project root)
        language_registry: Language registry
        tree_cache: Tree cache instance

    Returns:
        Summary as a list
    """
    abs_path = project.get_file_path(path)

    try:
        validate_file_access(abs_path, project.root_path)
    except Exception as e:
        raise FileAccessError(f"Access denied: {e}") from e

    language = language_registry.language_for_file(path)
    if not language:
        raise ParsingError(f"Could not detect language for {path}")

    config = get_container().get_config()
    summarization_config = config.summarization.get(language)
    if not summarization_config:
        summarization_config = SummarizationConfig()

    tree, source_bytes = parse_file(abs_path, language, language_registry, tree_cache)
    toc = summarize_tree(tree.root_node, summarization_config)

    return {
        "file": path,
        "language": language,
        "toc": toc
    }


def get_file_ast(
    project: Any,
    path: str,
    language_registry: Any,
    tree_cache: Any,
    max_depth: Optional[int] = None,
    include_text: bool = False,
) -> Dict[str, Any]:
    """
    Get the AST for a file.

    Args:
        project: Project object
        path: File path (relative to project root)
        language_registry: Language registry
        tree_cache: Tree cache instance
        max_depth: Maximum depth to traverse the tree
        include_text: Whether to include node text

    Returns:
        AST as a nested dictionary

    Raises:
        FileAccessError: If file access fails
        ParsingError: If parsing fails
    """
    abs_path = project.get_file_path(path)

    try:
        validate_file_access(abs_path, project.root_path)
    except Exception as e:
        raise FileAccessError(f"Access denied: {e}") from e

    language = language_registry.language_for_file(path)
    if not language:
        raise ParsingError(f"Could not detect language for {path}")

    tree, source_bytes = parse_file(abs_path, language, language_registry, tree_cache)

    return {
        "file": path,
        "language": language,
        "tree": node_to_dict(
            tree.root_node,
            source_bytes,
            include_children=True,
            include_text=include_text,
            max_depth=max_depth if max_depth is not None else 5,
        ),
    }


def parse_file(file_path: Any, language: str, language_registry: Any, tree_cache: Any) -> tuple[Any, bytes]:
    """
    Parse a file using tree-sitter.

    Args:
        file_path: Path to file
        language: Language identifier
        language_registry: Language registry
        tree_cache: Tree cache instance

    Returns:
        (Tree, source_bytes) tuple

    Raises:
        ParsingError: If parsing fails
    """
    # Always check the cache first, even if caching is disabled
    # This ensures cache misses are tracked correctly in tests
    cached = tree_cache.get(file_path, language)
    if cached:
        tree, bytes_data = cached
        return tree, bytes_data

    try:
        # Parse the file using helper
        parser = language_registry.get_parser(language)
        # Use source directly with parser to avoid parser vs. language confusion
        source_bytes = read_binary_file(file_path)
        tree = parse_source(source_bytes, parser)
        result_tuple = (tree, source_bytes)

        # Cache the tree only if caching is enabled
        is_cache_enabled = False
        try:
            # Get cache enabled state from tree_cache
            is_cache_enabled = tree_cache._is_cache_enabled()
        except Exception:
            # Fallback to instance value if method not available
            is_cache_enabled = getattr(tree_cache, "enabled", False)

        # Store in cache only if enabled
        if is_cache_enabled:
            tree_cache.put(file_path, language, tree, source_bytes)

        return result_tuple
    except Exception as e:
        raise ParsingError(f"Error parsing {file_path}: {e}") from e


def find_node_at_position(root_node: Any, row: int, column: int) -> Optional[Any]:
    """
    Find the most specific node at a given position.

    Args:
        root_node: Root node to search from
        row: Row (line) number, 0-based
        column: Column number, 0-based

    Returns:
        Node at position or None if not found
    """
    from ..models.ast import find_node_at_position as find_node

    return find_node(root_node, row, column)
