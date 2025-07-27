"""
Tests for response caching system.
"""

import pytest
import tempfile
import time
from pathlib import Path
import sqlite3

from quill.core.cache import ResponseCache


class TestResponseCache:
    """Test response cache functionality."""
    
    def test_cache_init(self):
        """Test cache initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir), memory_size=10, ttl=60)
            
            # Check database was created
            assert (Path(tmpdir) / "response_cache.db").exists()
            
            # Check initial stats
            stats = cache.get_stats()
            assert stats["memory_entries"] == 0
            assert stats["disk_entries"] == 0
            assert stats["hit_rate"] == 0
            
    def test_cache_set_get(self):
        """Test basic cache set and get operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir), ttl=60)
            
            # Store a response
            prompt = "What is 2+2?"
            response = "2+2 equals 4"
            model = "test-model"
            temp = 0.7
            
            cache.set(prompt, model, temp, response)
            
            # Retrieve it
            cached = cache.get(prompt, model, temp)
            assert cached == response
            
            # Check stats
            stats = cache.get_stats()
            assert stats["memory_hits"] == 1
            assert stats["misses"] == 0
            
    def test_cache_miss(self):
        """Test cache miss behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir))
            
            # Try to get non-existent entry
            result = cache.get("unknown prompt", "model", 0.5)
            assert result is None
            
            # Check stats
            stats = cache.get_stats()
            assert stats["misses"] == 1
            assert stats["memory_hits"] == 0
            
    def test_cache_expiration(self):
        """Test TTL expiration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir), ttl=1)  # 1 second TTL
            
            # Store and retrieve immediately
            cache.set("prompt", "model", 0.7, "response")
            assert cache.get("prompt", "model", 0.7) == "response"
            
            # Wait for expiration
            time.sleep(1.5)
            
            # Should be expired
            assert cache.get("prompt", "model", 0.7) is None
            
    def test_memory_eviction(self):
        """Test LRU eviction from memory cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir), memory_size=3)
            
            # Fill cache beyond capacity
            for i in range(5):
                cache.set(f"prompt{i}", "model", 0.7, f"response{i}")
                
            stats = cache.get_stats()
            assert stats["memory_entries"] == 3  # Only 3 in memory
            assert stats["disk_entries"] == 5    # All 5 on disk
            assert stats["evictions"] == 2       # 2 were evicted
            
    def test_disk_promotion(self):
        """Test promotion from disk to memory cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir), memory_size=2)
            
            # Fill memory cache
            cache.set("prompt1", "model", 0.7, "response1")
            cache.set("prompt2", "model", 0.7, "response2")
            cache.set("prompt3", "model", 0.7, "response3")  # Evicts prompt1
            
            # Get prompt1 (should be on disk only)
            result = cache.get("prompt1", "model", 0.7)
            assert result == "response1"
            
            # Check it was promoted to memory
            stats = cache.get_stats()
            assert stats["disk_hits"] == 1
            assert stats["memory_entries"] == 2
            
    def test_error_responses_not_cached(self):
        """Test that error responses are not cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir))
            
            # Try to cache an error
            cache.set("prompt", "model", 0.7, "ERROR: Connection failed")
            
            # Should not be cached
            assert cache.get("prompt", "model", 0.7) is None
            
    def test_cache_key_generation(self):
        """Test cache key uniqueness."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir))
            
            # Different parameters should have different keys
            key1 = cache._generate_key("prompt", "model1", 0.7)
            key2 = cache._generate_key("prompt", "model2", 0.7)
            key3 = cache._generate_key("prompt", "model1", 0.8)
            
            assert key1 != key2  # Different models
            assert key1 != key3  # Different temperatures
            
    def test_cache_clear(self):
        """Test clearing cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir))
            
            # Add some entries
            for i in range(5):
                cache.set(f"prompt{i}", "model", 0.7, f"response{i}")
                
            # Clear cache
            cache.clear()
            
            # Check everything is gone
            stats = cache.get_stats()
            assert stats["memory_entries"] == 0
            assert stats["disk_entries"] == 0
            
    def test_cache_export(self):
        """Test cache export functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir))
            
            # Add entries
            cache.set("prompt1", "model", 0.7, "response1")
            cache.set("prompt2", "model", 0.8, "response2")
            
            # Export
            export_path = Path(tmpdir) / "export.json"
            cache.export_cache(export_path)
            
            # Check export exists and has correct content
            assert export_path.exists()
            
            import json
            with open(export_path) as f:
                data = json.load(f)
                
            assert len(data["entries"]) == 2
            assert data["entries"][0]["prompt"] == "prompt1"
            assert "stats" in data
            
    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(Path(tmpdir), ttl=1)
            
            # Add entry
            cache.set("old_prompt", "model", 0.7, "response")
            
            # Wait for expiration
            time.sleep(1.5)
            
            # Add new entry
            cache.set("new_prompt", "model", 0.7, "response")
            
            # Clean up expired
            cache.cleanup_expired()
            
            # Check only new entry remains
            stats = cache.get_stats()
            assert stats["disk_entries"] == 1
            assert cache.get("new_prompt", "model", 0.7) == "response"
            assert cache.get("old_prompt", "model", 0.7) is None