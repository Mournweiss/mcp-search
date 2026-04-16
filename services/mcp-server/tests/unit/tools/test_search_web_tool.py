"""
Unit tests for MCP Search Web Tool.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_search.tools.search_web import SearchWebTool
from mcp_search.core.exceptions import ToolExecutionError
from mcp_search.schemas import SearchRequest


@pytest.mark.asyncio
async def test_search_web_tool_initialization():
    """Test SearchWebTool initialization."""
    tool = SearchWebTool()
    
    assert tool is not None
    assert hasattr(tool, 'tool_metadata')
    assert tool.tool_metadata["name"] == "search_web"
    assert tool.tool_metadata["description"] == "Perform a web search using SearxNG."
    assert "query" in tool.tool_metadata["parameters"]
    assert "max_results" in tool.tool_metadata["parameters"]


@pytest.mark.asyncio
async def test_search_web_tool_execute_success():
    """Test SearchWebTool execute method with successful search."""
    tool = SearchWebTool()
    
    # Mock the SearxNG client search method
    mock_search_response = MagicMock()
    mock_search_response.model_dump_json.return_value = '{"results": ["test"]}'
    
    with patch.object(tool.searxng_client, 'search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_search_response
        
        # Test execute method
        result = await tool.execute("test query", 5)
        
        # Verify the result is a string (JSON)
        assert isinstance(result, str)
        assert "results" in result
        
        # Verify search was called with correct parameters
        mock_search.assert_called_once_with("test query", 5)


@pytest.mark.asyncio
async def test_search_web_tool_execute_empty_query():
    """Test SearchWebTool execute method with empty query."""
    tool = SearchWebTool()
    
    # Test with empty query
    result = await tool.execute("", 5)
    
    # Should return error message string
    assert isinstance(result, str)
    assert "Search failed" in result or "empty" in result.lower()


@pytest.mark.asyncio
async def test_search_web_tool_execute_none_query():
    """Test SearchWebTool execute method with None query."""
    tool = SearchWebTool()
    
    # Test with None query
    result = await tool.execute(None, 5)
    
    # Should return error message string
    assert isinstance(result, str)
    assert "Search failed" in result or "empty" in result.lower()


@pytest.mark.asyncio
async def test_search_web_tool_execute_with_defaults():
    """Test SearchWebTool execute method with default parameters."""
    tool = SearchWebTool()
    
    # Mock the SearxNG client search method
    mock_search_response = MagicMock()
    mock_search_response.model_dump_json.return_value = '{"results": ["test"]}'
    
    with patch.object(tool.searxng_client, 'search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_search_response
        
        # Test execute method without max_results (should use default)
        result = await tool.execute("test query")
        
        # Verify the result is a string (JSON)
        assert isinstance(result, str)
        assert "results" in result
        
        # Verify search was called with correct parameters (default max_results should be used)
        mock_search.assert_called_once()


@pytest.mark.asyncio
async def test_search_web_tool_execute_search_error():
    """Test SearchWebTool execute method when search raises SearchError."""
    tool = SearchWebTool()
    
    # Mock the SearxNG client to raise a SearchError
    with patch.object(tool.searxng_client, 'search', new_callable=AsyncMock) as mock_search:
        from mcp_search.core import SearchError
        mock_search.side_effect = SearchError("Search failed")
        
        # Test execute method
        result = await tool.execute("test query", 5)
        
        # Should return error message string
        assert isinstance(result, str)
        assert "Search failed" in result


@pytest.mark.asyncio
async def test_search_web_tool_execute_unexpected_error():
    """Test SearchWebTool execute method when unexpected error occurs."""
    tool = SearchWebTool()
    
    # Mock the SearxNG client to raise an unexpected exception
    with patch.object(tool.searxng_client, 'search', new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = Exception("Unexpected error")
        
        # Test execute method, should raise ToolExecutionError
        with pytest.raises(ToolExecutionError):
            await tool.execute("test query", 5)


@pytest.mark.asyncio
async def test_search_web_tool_execute_parameter_validation():
    """Test SearchWebTool execute method parameter validation."""
    tool = SearchWebTool()
    
    # Test with various parameter combinations
    test_cases = [
        ("valid query", 10),
        ("another query", 1),
        ("query with spaces", 50),
        ("", 5),  # Empty query
        ("valid", None),  # None max_results
    ]
    
    for query, max_results in test_cases:
        if query == "" or max_results is None:
            # These should return error strings rather than raise exceptions
            result = await tool.execute(query, max_results)
            assert isinstance(result, str)
        else:
            # These should work normally (mocked)
            mock_search_response = MagicMock()
            mock_search_response.model_dump_json.return_value = '{"results": ["test"]}'
            
            with patch.object(tool.searxng_client, 'search', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = mock_search_response
                result = await tool.execute(query, max_results)
                assert isinstance(result, str)


@pytest.mark.asyncio
async def test_search_web_tool_execute_with_max_results_capping():
    """Test SearchWebTool execute method with max_results capping."""
    tool = SearchWebTool()
    
    # Mock the SearxNG client search method
    mock_search_response = MagicMock()
    mock_search_response.model_dump_json.return_value = '{"results": ["test"]}'
    
    with patch.object(tool.searxng_client, 'search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_search_response
        
        # Test with max_results that exceeds limit (should be capped)
        result = await tool.execute("test query", 100)  # Should be capped to settings.max_search_results
        
        # Verify the result is a string (JSON)
        assert isinstance(result, str)
        assert "results" in result
        
        mock_search.assert_called_once()


@pytest.mark.asyncio
async def test_search_web_tool_execute_client_integration():
    """Test SearchWebTool execute method client integration."""
    tool = SearchWebTool()
    
    # Verify that the tool has the expected clients
    assert hasattr(tool, 'searxng_client')
    assert hasattr(tool, 'firecrawl_client')
    assert hasattr(tool, 'redis_client')
    
    # Mock the search method to verify it's called on the correct client
    mock_search_response = MagicMock()
    mock_search_response.model_dump_json.return_value = '{"results": ["test"]}'
    
    with patch.object(tool.searxng_client, 'search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_search_response
        
        # Execute the tool
        result = await tool.execute("test query", 5)
        
        # Verify that search was called on the searxng client
        assert mock_search.called
        mock_search.assert_called_once_with("test query", 5)