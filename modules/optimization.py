# Created by Jeff Hollaway

import logging
import time
import functools
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any

logger = logging.getLogger(__name__)

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"[PERF] {func.__name__} completed in {elapsed:.3f}s")
        return result
    return wrapper

def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"[RETRY] {func.__name__} attempt {attempt}/{max_attempts} failed: {e}")
                    if attempt == max_attempts:
                        raise
                    time.sleep(delay * attempt)
        return wrapper
    return decorator

class BatchProcessor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def process_parallel(self, items: List, func: Callable, **kwargs) -> List:
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(func, item, **kwargs): i for i, item in enumerate(items)}
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    result = future.result()
                    results.append((idx, result))
                except Exception as e:
                    logger.error(f"[BATCH] Item {idx} failed: {e}")
                    results.append((idx, None))
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]

    def process_chunked(self, items: List, func: Callable, chunk_size: int = 10) -> List:
        results = []
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            chunk_results = self.process_parallel(chunk, func)
            results.extend(chunk_results)
            logger.info(f"[BATCH] Processed chunk {i//chunk_size + 1}, total: {len(results)}/{len(items)}")
        return results

class MemoryManager:
    def __init__(self, max_memory_mb: int = 4096):
        self.max_memory_mb = max_memory_mb

    def check_memory(self):
        try:
            import psutil
            mem = psutil.virtual_memory()
            used_mb = mem.used / (1024 * 1024)
            if used_mb > self.max_memory_mb:
                logger.warning(f"[MEM] High memory usage: {used_mb:.0f}MB / {self.max_memory_mb}MB")
                return False
            return True
        except ImportError:
            return True

    def cleanup_temp_files(self, temp_dir: str):
        import os, glob
        files = glob.glob(os.path.join(temp_dir, "*.tmp"))
        for f in files:
            try:
                os.remove(f)
            except OSError:
                pass
        logger.info(f"[MEM] Cleaned {len(files)} temp files")
