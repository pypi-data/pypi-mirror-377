"""Test MCP protocol compliance."""

from unittest.mock import patch

import pytest

from stac_mcp.server import handle_call_tool, handle_list_tools


@pytest.mark.asyncio
async def test_list_tools():
    """Test that list_tools returns proper MCP tool definitions."""
    tools = await handle_list_tools()

    assert len(tools) == 4

    tool_names = [tool.name for tool in tools]
    expected_tools = [
        "search_collections",
        "get_collection",
        "search_items",
        "get_item",
    ]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names

    # Check that each tool has proper schema
    for tool in tools:
        assert tool.name
        assert tool.description
        assert tool.inputSchema
        assert "type" in tool.inputSchema
        assert tool.inputSchema["type"] == "object"
        assert "properties" in tool.inputSchema


@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test calling an unknown tool returns an error."""
    try:
        await handle_call_tool("unknown_tool", {})
        assert False, "Expected ValueError for unknown tool"
    except ValueError as e:
        assert "Unknown tool: unknown_tool" in str(e)


@pytest.mark.asyncio
@patch("stac_mcp.server.stac_client")
async def test_call_tool_search_collections(mock_stac_client):
    """Test calling search_collections tool."""
    # Mock the search_collections method
    mock_stac_client.search_collections.return_value = [
        {
            "id": "test-collection",
            "title": "Test Collection",
            "description": "A test collection",
            "license": "MIT",
        },
    ]

    result = await handle_call_tool("search_collections", {"limit": 1})

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].type == "text"
    assert "Test Collection" in result[0].text
    assert "test-collection" in result[0].text


@pytest.mark.asyncio
@patch("stac_mcp.server.stac_client")
async def test_call_tool_with_error(mock_stac_client):
    """Test calling a tool that raises an exception."""
    mock_stac_client.search_collections.side_effect = Exception("Network error")

    try:
        await handle_call_tool("search_collections", {"limit": 1})
        assert False, "Expected exception to be raised"
    except Exception as e:
        assert "Network error" in str(e)


@pytest.mark.asyncio
async def test_tool_schemas_validation():
    """Test that all tool schemas are valid JSON Schema."""
    import jsonschema

    tools = await handle_list_tools()

    for tool in tools:
        # This should not raise an exception
        jsonschema.Draft7Validator.check_schema(tool.inputSchema)

        # Check required fields are properly defined
        if "required" in tool.inputSchema:
            required_fields = tool.inputSchema["required"]
            properties = tool.inputSchema["properties"]

            for field in required_fields:
                assert field in properties
