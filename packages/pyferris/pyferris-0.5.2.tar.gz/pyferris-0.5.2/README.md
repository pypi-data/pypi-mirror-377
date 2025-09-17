# PyFerris

**PyFerris** is a high-performance parallel processing library for Python, powered by Rust and PyO3. It provides a seamless, Pythonic API to leverage Rust's speed and memory safety for parallel and distributed computing, bypassing Python's Global Interpreter Lock (GIL). PyFerris is designed for developers and engineers across all fields who need efficient parallel processing for compute-intensive tasks, running anywhere from embedded systems to enterprise-grade applications.

## Installation

PyFerris is available on PyPI and can be installed with `pip` or `poetry`.

```bash
pip install pyferris
```

To build from source (requires Rust and `maturin`):

```bash
git clone https://github.com/DVNghiem/Pyferris.git
cd pyferris
poetry install
maturin develop
```

## Quick Start

Here's a simple example of using `parallel_map` to square a large dataset:

```python
from pyferris import parallel_map

def square(x):
    return x * x

numbers = range(1000000)
results = parallel_map(square, numbers)
print(list(results)[:5])  # [0, 1, 4, 9, 16]
```

For an asynchronous example with progress tracking:

```python
import asyncio
from pyferris import async_parallel_map, ProgressTracker

async def process(x):
    await asyncio.sleep(0.1)
    return x * 2

async def main():
    data = range(1000)
    tracker = ProgressTracker(total=1000, desc="Processing")
    results = await async_parallel_map(process, data, progress=tracker)
    print(list(results)[:5])  # [0, 2, 4, 6, 8]

asyncio.run(main())
```

More examples are available in the `examples/` directory, covering all features from basic to enterprise-level.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Core Features](docs/core.md)** - Parallel operations (`parallel_map`, `parallel_filter`, `parallel_reduce`, `parallel_starmap`)
- **[Executor](docs/executor.md)** - Task execution and thread pool management
- **[I/O Operations](docs/io.md)** - File I/O and parallel data processing (CSV, JSON, text files)
- **[Examples](docs/examples.md)** - Practical usage examples and real-world use cases
- **[API Reference](docs/api_reference.md)** - Complete API documentation

### Quick Start Guide

```python
# Core parallel operations
from pyferris import parallel_map, parallel_filter, parallel_reduce

# Process data in parallel
results = parallel_map(lambda x: x**2, range(1000))
evens = parallel_filter(lambda x: x % 2 == 0, range(1000))
total = parallel_reduce(lambda x, y: x + y, range(1000))

# High-performance caching with SmartCache
from pyferris import SmartCache, EvictionPolicy, cached

# Create intelligent cache with LRU eviction
cache = SmartCache(max_size=1000, policy=EvictionPolicy.LRU)
cache.put("user:123", {"name": "Alice", "age": 30})
user = cache.get("user:123")

# Function caching decorator for immediate performance gains
@cached(max_size=100, policy=EvictionPolicy.ADAPTIVE)
def expensive_computation(n):
    return n * n * n

# Task execution with improved Rayon-based executor
from pyferris.executor import Executor

# Python callback tasks (GIL-limited but still beneficial)
with Executor(max_workers=4) as executor:
    # Single task submission
    future = executor.submit(expensive_function, data)
    result = future.result()
    
    # Multiple tasks (recommended approach)
    results = executor.map(process_function, data_list)
    
    # Pure Rust computation (true parallel speedup)
    numbers = list(range(1, 1000))
    parallel_sum = executor.submit_computation('heavy_computation', numbers)
    
    # Performance tuning
    executor.set_chunk_size(50)  # Optimize for your workload

# File I/O operations
from pyferris.io import simple_io, csv, json

# Read/write files in parallel
contents = simple_io.read_files_parallel(['file1.txt', 'file2.txt'])
data = csv.read_csv('large_dataset.csv')
json.write_json('output.json', processed_data)
```

## Performance

PyFerris leverages Rust's performance and memory safety to outperform Python's built-in `multiprocessing` and `concurrent.futures` for compute-intensive tasks. For example, `parallel_map` can be 2-5x faster than `multiprocessing.Pool.map` for large datasets, thanks to Rust's zero-cost abstractions and GIL-free execution across all processor types and platforms.

## Contributing

We welcome contributions! To get started:
1. Fork the repository on GitHub.
2. Clone your fork: `git clone https://github.com/DVNghiem/Pyferris.git`.
3. Install dependencies: `poetry install`.
4. Build the Rust extension: `maturin develop`.
5. Run tests: `poetry run pytest`.
6. Submit a pull request with your changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

PyFerris is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

- **Issues**: Report bugs or request features at [GitHub Issues](https://github.com/DVNghiem/Pyferris/issues).

---

*PyFerris: Unleash the power of Rust in Python for universal parallel processing!*
