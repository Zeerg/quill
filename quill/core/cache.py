"""
Response caching system for Quill fuzzer.

Provides both in-memory and persistent caching to avoid redundant API calls
and improve fuzzing performance.
"""

import json
import hashlib
import time
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from functools import lru_cache
import logging

from ..utils.logging import get_logger


class ResponseCache:
    """
    Multi-level cache for LLM responses.
    
    Implements:
    - L1: In-memory LRU cache (fastest, limited size)
    - L2: SQLite persistent cache (slower, unlimited size)
    """
    
    def __init__(
        self,
        cache_dir: Path,
        memory_size: int = 1000,
        ttl: int = 3600,
        verbose: bool = False
    ):
        """
        Initialize response cache.
        
        Args:
            cache_dir: Directory to store cache database
            memory_size: Maximum items in memory cache
            ttl: Time-to-live in seconds (default: 1 hour)
            verbose: Enable debug logging
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.log = get_logger(__name__, debug=verbose)
        
        # L1: In-memory cache
        self._memory_cache: Dict[str, Tuple[str, float]] = {}
        self._memory_size = memory_size
        
        # L2: SQLite cache
        self.db_path = self.cache_dir / "response_cache.db"
        self._init_db()
        
        # Statistics
        self.stats = {
            "memory_hits": 0,
            "disk_hits": 0,
            "misses": 0,
            "evictions": 0
        }
        
    def _init_db(self):
        """Initialize SQLite database for persistent cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    model TEXT,
                    temperature REAL,
                    timestamp REAL NOT NULL,
                    hits INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON cache(timestamp)
            """)
            conn.commit()
            
    def _generate_key(
        self, 
        prompt: str, 
        model: str, 
        temperature: float
    ) -> str:
        """
        Generate cache key from prompt and parameters.
        
        Args:
            prompt: The prompt text
            model: Model identifier
            temperature: Temperature setting
            
        Returns:
            MD5 hash as cache key
        """
        content = f"{prompt}|{model}|{temperature:.2f}"
        return hashlib.md5(content.encode()).hexdigest()
        
    def get(
        self, 
        prompt: str, 
        model: str, 
        temperature: float
    ) -> Optional[str]:
        """
        Get cached response if available.
        
        Args:
            prompt: The prompt text
            model: Model identifier
            temperature: Temperature setting
            
        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(prompt, model, temperature)
        current_time = time.time()
        
        # Check L1 (memory) cache
        if key in self._memory_cache:
            response, timestamp = self._memory_cache[key]
            if current_time - timestamp <= self.ttl:
                self.stats["memory_hits"] += 1
                self.log.debug(f"Memory cache hit for key: {key[:8]}...")
                # Move to end (LRU)
                del self._memory_cache[key]
                self._memory_cache[key] = (response, timestamp)
                return response
            else:
                # Expired
                del self._memory_cache[key]
                
        # Check L2 (disk) cache
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT response, timestamp 
                FROM cache 
                WHERE key = ?
            """, (key,))
            
            row = cursor.fetchone()
            if row:
                response, timestamp = row
                if current_time - timestamp <= self.ttl:
                    self.stats["disk_hits"] += 1
                    self.log.debug(f"Disk cache hit for key: {key[:8]}...")
                    
                    # Update hit count
                    conn.execute("""
                        UPDATE cache 
                        SET hits = hits + 1 
                        WHERE key = ?
                    """, (key,))
                    
                    # Promote to memory cache
                    self._add_to_memory(key, response, timestamp)
                    
                    return response
                else:
                    # Expired - delete from disk
                    conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                    
        self.stats["misses"] += 1
        self.log.debug(f"Cache miss for key: {key[:8]}...")
        return None
        
    def set(
        self,
        prompt: str,
        model: str,
        temperature: float,
        response: str
    ):
        """
        Store response in cache.
        
        Args:
            prompt: The prompt text
            model: Model identifier
            temperature: Temperature setting
            response: The response to cache
        """
        key = self._generate_key(prompt, model, temperature)
        timestamp = time.time()
        
        # Don't cache error responses
        if response.startswith("ERROR:"):
            return
            
        # Add to memory cache
        self._add_to_memory(key, response, timestamp)
        
        # Add to disk cache
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache 
                (key, prompt, response, model, temperature, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (key, prompt, response, model, temperature, timestamp))
            conn.commit()
            
        self.log.debug(f"Cached response for key: {key[:8]}...")
        
    def _add_to_memory(self, key: str, response: str, timestamp: float):
        """Add item to memory cache with LRU eviction."""
        # Evict if at capacity
        if len(self._memory_cache) >= self._memory_size:
            # Remove oldest item (first in dict)
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
            self.stats["evictions"] += 1
            
        self._memory_cache[key] = (response, timestamp)
        
    def clear(self):
        """Clear all cached data."""
        self._memory_cache.clear()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()
        self.log.info("Cache cleared")
        
    def cleanup_expired(self):
        """Remove expired entries from disk cache."""
        current_time = time.time()
        cutoff_time = current_time - self.ttl
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM cache 
                WHERE timestamp < ?
            """, (cutoff_time,))
            deleted = cursor.rowcount
            conn.commit()
            
        if deleted > 0:
            self.log.info(f"Cleaned up {deleted} expired cache entries")
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            disk_entries = cursor.fetchone()[0]
            
        total_hits = self.stats["memory_hits"] + self.stats["disk_hits"]
        total_requests = total_hits + self.stats["misses"]
        
        return {
            "memory_entries": len(self._memory_cache),
            "memory_size_limit": self._memory_size,
            "disk_entries": disk_entries,
            "memory_hits": self.stats["memory_hits"],
            "disk_hits": self.stats["disk_hits"],
            "total_hits": total_hits,
            "misses": self.stats["misses"],
            "hit_rate": total_hits / total_requests if total_requests > 0 else 0,
            "evictions": self.stats["evictions"]
        }
        
    def export_cache(self, output_path: Path):
        """
        Export cache contents to JSON file.
        
        Args:
            output_path: Path to save exported cache
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT prompt, response, model, temperature, timestamp, hits
                FROM cache
                ORDER BY hits DESC, timestamp DESC
            """)
            
            entries = []
            for row in cursor:
                entries.append({
                    "prompt": row[0],
                    "response": row[1],
                    "model": row[2],
                    "temperature": row[3],
                    "timestamp": row[4],
                    "hits": row[5]
                })
                
        with open(output_path, 'w') as f:
            json.dump({
                "exported_at": time.time(),
                "entries": entries,
                "stats": self.get_stats()
            }, f, indent=2)
            
        self.log.info(f"Exported {len(entries)} cache entries to {output_path}")