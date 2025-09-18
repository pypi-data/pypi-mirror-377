from collections.abc import Callable
from pathlib import Path

from loguru import logger as log

from src.config import MCPServerConfig

from .parsers import ImportErrorDetails, parse_mcp_like_json, permissive_read_json
from .paths import (
    find_claude_code_user_all_candidates,
    find_claude_code_user_settings_file,
    find_cursor_user_file,
    find_vscode_user_mcp_file,
)


def import_from_cursor() -> list[MCPServerConfig]:
    # Only support user-level Cursor config
    files = find_cursor_user_file()
    if not files:
        raise ImportErrorDetails(
            "Cursor MCP config not found (~/.cursor/mcp.json).",
            Path.home() / ".cursor" / "mcp.json",
        )
    data = permissive_read_json(files[0])
    return parse_mcp_like_json(data, default_enabled=True)


def import_from_vscode() -> list[MCPServerConfig]:
    files = find_vscode_user_mcp_file()
    if not files:
        raise ImportErrorDetails(
            "VSCode configuration not found (checked User/mcp.json and User/settings.json)."
        )
    # Try each file; stop at the first that yields MCP servers
    for f in files:
        try:
            log.info("VSCode config detected at: {}", f)
            data = permissive_read_json(f)
            parsed = parse_mcp_like_json(data, default_enabled=True)
            if parsed:
                return parsed
        except Exception as e:
            print(f"Failed reading VSCode config {f}: {e}")
    # If we saw files but none yielded servers, return empty with info
    log.info("No MCP servers found in VSCode config candidates; returning empty list")
    return []


def import_from_claude_code() -> list[MCPServerConfig]:
    # Prefer Claude Code's documented user-level locations if present
    files = find_claude_code_user_all_candidates()
    if not files:
        # Back-compat: also check specific settings.json location
        files = find_claude_code_user_settings_file()
    for f in files:
        try:
            log.info("Claude Code config detected at: {}", f)
            data = permissive_read_json(f)
            parsed = parse_mcp_like_json(data, default_enabled=True)
            if parsed:
                return parsed
        except Exception as e:
            log.warning("Failed reading Claude Code config {}: {}", f, e)

    # No user-level Claude Code config found; return empty per user preference
    log.info("Claude Code config not found; returning empty result (no user-level config found)")
    return []


IMPORTERS: dict[str, Callable[..., list[MCPServerConfig]]] = {
    "cursor": import_from_cursor,
    "vscode": import_from_vscode,
    "claude-code": import_from_claude_code,
}
