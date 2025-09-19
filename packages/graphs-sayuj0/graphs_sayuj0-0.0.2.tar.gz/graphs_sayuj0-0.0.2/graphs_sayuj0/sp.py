from typing import Dict, Tuple, List, Optional
from .heapq import heappush, heappop
from collections import deque

INF = 10 ** 18

def _ensure_all_nodes(graph: Dict[int, Dict[int, int]]) -> Dict[int, int]:
    dist: Dict[int, int] = {}
    for u in graph:
        if u not in dist:
            dist[u] = INF
        for v in graph[u]:
            if v not in dist:
                dist[v] = INF
    return dist


def dijkstra(graph: Dict[int, Dict[int, int]], s: int) -> Tuple[Dict[int, int], Dict[int, List[int]]]:
    dist = _ensure_all_nodes(graph)
    if s not in dist:
        dist[s] = 0
    dist[s] = 0

    parent: Dict[int, Optional[int]] = {u: None for u in dist}
    pq: List[Tuple[int, int]] = []
    heappush(pq, (0, s))
    visited = set()

    while pq:
        d, u = heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        if d > dist[u]:
            continue

        for v, w in graph.get(u, {}).items():
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                heappush(pq, (nd, v))

    path: Dict[int, List[int]] = {}
    for dst, dd in dist.items():
        if dd == INF:
            continue  
        seq: List[int] = []
        cur: Optional[int] = dst
        while cur is not None:
            seq.append(cur)
            cur = parent[cur]
        seq.reverse()
        path[dst] = seq

    return dist, path


# Bonus algorithm: Unweighted shortest paths via BFS
def bfs_shortest_paths(graph: Dict[int, Dict[int, int]], s: int) -> Tuple[Dict[int, int], Dict[int, List[int]]]:
    dist = _ensure_all_nodes(graph)
    dist[s] = 0
    parent: Dict[int, Optional[int]] = {u: None for u in dist}

    q = deque([s])
    seen = {s}
    while q:
        u = q.popleft()
        for v in graph.get(u, {}):
            if v not in seen:
                seen.add(v)
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)

    path: Dict[int, List[int]] = {}
    for dst, dd in dist.items():
        if dd == INF:
            continue
        seq: List[int] = []
        cur: Optional[int] = dst
        while cur is not None:
            seq.append(cur)
            cur = parent[cur]
        seq.reverse()
        path[dst] = seq

    return dist, path
