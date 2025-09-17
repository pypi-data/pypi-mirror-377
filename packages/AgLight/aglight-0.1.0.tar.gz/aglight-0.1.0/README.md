# AgLight

AgLight is a Python module that provides an ultra-accelerating decorator for scientific and numerical functions. It automatically uses Numba JIT compilation and parallelization if available, or falls back to multiprocessing for heavy computations if Numba is not installed.

## Features
- **@light decorator**: Accelerates your functions with minimal code changes.
- Uses Numba JIT and parallelization for optimal speed.
- Falls back to multiprocessing for large workloads if Numba is unavailable.
- Simple API: just decorate your function with `@light`.

## Installation

```bash
pip install AgLight
```

## Usage

```python
from AgLight import light

@light
def my_heavy_function(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

print(my_heavy_function(1000000))
```

## Requirements
- Python 3.7+
- numpy
- (Optional) numba for maximum acceleration

## License
MIT
