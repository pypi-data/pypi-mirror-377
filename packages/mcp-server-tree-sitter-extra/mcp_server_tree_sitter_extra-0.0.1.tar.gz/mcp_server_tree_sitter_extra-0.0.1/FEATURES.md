# MCP Tree-sitter Server (extensions)

This server extends original https://github.com/wrale/mcp-server-tree-sitter with
 * More language mappings
 * High-level AST overview (AST TOC) for AI agents

## AST TOC

We've found AI models easily overwhelmed by JSON ASTs produced by original tree-sitter MCP.
Also, we find LLMs performing better if original entity names (classes, functions) are provided.
Therefore, we introduced get_ast_toc operation that retrieves 1-st order AST for the file and summarizes the tree:
 * All non-important nodes are demoted to generic 'code_block'
 * Adjacent nodes of the same type are collapsed into a single node (unless the node is non-collapsible)
 * Inline comments (on the same line as non-comment node) ignored
 * For 'named nodes' (functions, classes, subroutines) - a name is retrieved and used to construct the node name
 * Non-individually named nodes will get generic names based on node type and a line number

This process is, of course, language specific and is controlled by summarization settings in the configuration file:
 * important_nodes - node types eligible for distinct TOC entries (Default: "class_definition", "function_definition", "subroutine_declaration_statement")
 * nongeneric_nodes - node types that should not be demoted to generic code blocks (Default: "comment", "import")
 * individually_named_nodes - node types that should retain individual names (Default: "class_definition", "function_definition", "subroutine_declaration_statement")
 * identifier_types - node types to consider for searching for parent node names (Default: "identifier", "bareword")
