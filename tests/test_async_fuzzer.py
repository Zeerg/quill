"""
Tests for async fuzzer implementation.
"""

import pytest
import asyncio
from pathlib import Path
import json
import tempfile
from unittest.mock import Mock, patch, AsyncMock

from quill.core.async_fuzzer import AsyncFuzzer, AsyncRequest
from quill.core.classes import FuzzStats


@pytest.mark.asyncio
async def test_async_fuzzer_context_manager():
    """Test async fuzzer context manager"""
    with tempfile.TemporaryDirectory() as tmpdir:
        fuzzer = AsyncFuzzer(
            mode="http",
            model_id="test",
            url="http://localhost:8000",
            output_dir=Path(tmpdir),
            max_prompts=1,
            temperature=0.7,
            mutators=["typo"],
            verbose=False
        )
        
        async with fuzzer as f:
            assert f.session is not None
            assert f.session.closed is False
            
        # Session should be closed after exiting context
        assert fuzzer.session.closed is True


@pytest.mark.asyncio
async def test_async_query_model():
    """Test async model querying"""
    with tempfile.TemporaryDirectory() as tmpdir:
        fuzzer = AsyncFuzzer(
            mode="http",
            model_id="test",
            url="http://localhost:8000",
            output_dir=Path(tmpdir),
            max_prompts=1,
            temperature=0.7,
            mutators=["typo"],
            verbose=False
        )
        
        async with fuzzer as f:
            # Mock the session.post method
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value={"response": "Test response"})
            mock_response.status = 200
            
            with patch.object(f.session, 'post', return_value=mock_response):
                response = await f._query_model_async("Test prompt")
                assert response == "Test response"


@pytest.mark.asyncio
async def test_process_batch():
    """Test batch processing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        fuzzer = AsyncFuzzer(
            mode="http",
            model_id="test", 
            url="http://localhost:8000",
            output_dir=Path(tmpdir),
            max_prompts=3,
            temperature=0.7,
            mutators=["typo"],
            verbose=False,
            batch_size=2
        )
        
        requests = [
            AsyncRequest(index=0, original="prompt1", mutated="prompt1_mutated"),
            AsyncRequest(index=1, original="prompt2", mutated="prompt2_mutated"),
        ]
        
        async with fuzzer as f:
            # Mock the query method
            f._query_model_async = AsyncMock(side_effect=[
                "Response 1",
                "Response 2"
            ])
            
            results = await f._process_batch(requests)
            
            assert len(results) == 2
            assert results[0][0].index == 0
            assert results[0][1] == "Response 1"
            assert results[1][0].index == 1
            assert results[1][1] == "Response 2"


def test_sync_run_wrapper():
    """Test synchronous run wrapper"""
    with tempfile.TemporaryDirectory() as tmpdir:
        fuzzer = AsyncFuzzer(
            mode="http",
            model_id="test",
            url="http://localhost:8000",
            output_dir=Path(tmpdir),
            max_prompts=1,
            temperature=0.7,
            mutators=["typo"],
            verbose=False
        )
        
        # Mock the async run method
        with patch.object(fuzzer, 'run_async', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = FuzzStats()
            
            # Should not raise any exceptions
            stats = fuzzer.run()
            assert isinstance(stats, FuzzStats)


@pytest.mark.asyncio
async def test_ollama_mode():
    """Test Ollama mode async querying"""
    with tempfile.TemporaryDirectory() as tmpdir:
        fuzzer = AsyncFuzzer(
            mode="ollama",
            model_id="llama2",
            url="http://localhost:11434",
            output_dir=Path(tmpdir),
            max_prompts=1,
            temperature=0.7,
            mutators=["typo"],
            verbose=False
        )
        
        async with fuzzer as f:
            # Mock the session.post method
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value={"response": "Ollama response"})
            mock_response.status = 200
            
            with patch.object(f.session, 'post', return_value=mock_response):
                response = await f._query_model_async("Test prompt")
                assert response == "Ollama response"


@pytest.mark.asyncio 
async def test_error_handling():
    """Test error handling in async requests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        fuzzer = AsyncFuzzer(
            mode="http",
            model_id="test",
            url="http://localhost:8000",
            output_dir=Path(tmpdir),
            max_prompts=1,
            temperature=0.7,
            mutators=["typo"],
            verbose=False,
            timeout=0.1  # Very short timeout
        )
        
        async with fuzzer as f:
            # Mock timeout
            with patch.object(f.session, 'post', side_effect=asyncio.TimeoutError):
                response = await f._query_model_async("Test prompt")
                assert "ERROR: Request timeout" in response