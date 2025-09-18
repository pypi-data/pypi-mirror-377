# Simple re-export of stdlib heapq functions so sp.py can import locally
from heapq import heappush, heappop

__all__ = ["heappush", "heappop"]
