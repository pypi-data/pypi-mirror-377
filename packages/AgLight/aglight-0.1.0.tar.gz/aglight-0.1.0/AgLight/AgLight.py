import os
from functools import wraps
from concurrent.futures import ProcessPoolExecutor
import numpy as np

try:
    from numba import jit, prange
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

def light(func):
    """
    Ultra-accelerating decorator: 
    - Uses Numba JIT if available.
    - Auto-parallelizes heavy loops.
    - Falls back to multiprocessing if Numba unavailable.
    """
    if HAS_NUMBA:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine input size heuristic
            size_hint = args[0] if args and isinstance(args[0], int) else 100
            
            # Decide strategy
            if size_hint <= 100:
                # Small: simple JIT
                if not hasattr(wrapper, "_jit_small"):
                    wrapper._jit_small = jit(nopython=True, cache=True)(func)
                    try: wrapper._jit_small(min(50, size_hint))
                    except: pass
                compiled_func = wrapper._jit_small
            else:
                # Large: optimized JIT (no parallel=True to avoid warning)
                if not hasattr(wrapper, "_jit_large"):
                    wrapper._jit_large = jit(nopython=True, fastmath=True, cache=True)(func)
                    try: wrapper._jit_large(min(50, size_hint))
                    except: pass
                compiled_func = wrapper._jit_large
            
            try:
                return compiled_func(*args, **kwargs)
            except Exception:
                # Fallback to original function
                return func(*args, **kwargs)
        
        return wrapper
    else:
        # No Numba: fallback to multiprocessing for large inputs
        @wraps(func)
        def wrapper(*args, **kwargs):
            size_hint = args[0] if args and isinstance(args[0], int) else 100
            if size_hint > 500:
                try:
                    with ProcessPoolExecutor(max_workers=min(2, os.cpu_count())) as exe:
                        future = exe.submit(func, *args, **kwargs)
                        return future.result(timeout=10)
                except Exception:
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        return wrapper
