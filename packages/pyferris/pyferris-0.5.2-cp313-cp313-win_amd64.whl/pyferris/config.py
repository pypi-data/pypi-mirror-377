"""
Configuration management for PyFerris.
"""

from ._pyferris import (
    set_worker_count as _set_worker_count,
    get_worker_count as _get_worker_count,
    set_chunk_size as _set_chunk_size,
    get_chunk_size as _get_chunk_size,
    Config as _Config,
)

def set_worker_count(count):
    """
    Set the number of worker threads for parallel operations.
    
    Args:
        count: Number of worker threads (must be > 0)
    
    Example:
        >>> from pyferris import set_worker_count
        >>> set_worker_count(8)  # Use 8 worker threads
    """
    return _set_worker_count(count)

def get_worker_count():
    """
    Get the current number of worker threads.
    
    Returns:
        Number of worker threads
    
    Example:
        >>> from pyferris import get_worker_count
        >>> get_worker_count()
        8
    """
    return _get_worker_count()

def set_chunk_size(size):
    """
    Set the default chunk size for parallel operations.
    
    Args:
        size: Chunk size (must be > 0)
    
    Example:
        >>> from pyferris import set_chunk_size
        >>> set_chunk_size(500)  # Use chunks of 500 items
    """
    return _set_chunk_size(size)

def get_chunk_size():
    """
    Get the current default chunk size.
    
    Returns:
        Current chunk size
    
    Example:
        >>> from pyferris import get_chunk_size
        >>> get_chunk_size()
        500
    """
    return _get_chunk_size()

class Config:
    """
    Configuration class for managing global PyFerris settings.
    
    Example:
        >>> from pyferris import Config
        >>> config = Config(worker_count=8, chunk_size=1000, error_strategy='raise')
        >>> config.apply()  # Apply settings globally
    """
    
    def __init__(self, worker_count=None, chunk_size=None, error_strategy=None):
        """
        Initialize configuration.
        
        Args:
            worker_count: Number of worker threads
            chunk_size: Default chunk size
            error_strategy: Error handling strategy ('raise', 'ignore', 'collect')
        """
        self._config = _Config(worker_count, chunk_size, error_strategy)
    
    @property
    def worker_count(self):
        return self._config.worker_count
    
    @worker_count.setter
    def worker_count(self, value):
        self._config.worker_count = value
    
    @property
    def chunk_size(self):
        return self._config.chunk_size
    
    @chunk_size.setter
    def chunk_size(self, value):
        self._config.chunk_size = value
    
    @property
    def error_strategy(self):
        return self._config.error_strategy
    
    @error_strategy.setter
    def error_strategy(self, value):
        self._config.error_strategy = value
    
    def apply(self):
        """Apply the configuration globally."""
        return self._config.apply()
    
    def __repr__(self):
        return repr(self._config)

__all__ = [
    "set_worker_count",
    "get_worker_count", 
    "set_chunk_size",
    "get_chunk_size",
    "Config",
]