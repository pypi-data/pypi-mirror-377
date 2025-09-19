import sys
from heapq import heappush, heappop

def dijkstra(graph, source):
    """
    Dijkstra's shortest path algorithm.
    
    Args:
        graph: Dictionary where graph[u][v] = weight of edge from u to v
        source: Starting vertex
    
    Returns:
        dist: Dictionary of shortest distances from source to all vertices
        path: Dictionary of shortest paths from source to all vertices
    """
    # Initialize distances
    dist = {}
    path = {}
    
    # Set all distances to infinity initially
    for vertex in graph:
        dist[vertex] = sys.maxsize
        path[vertex] = []
    
    # Add vertices that might be destinations but not sources
    for u in graph:
        for v in graph[u]:
            if v not in dist:
                dist[v] = sys.maxsize
                path[v] = []
    
    # Distance to source is 0
    dist[source] = 0
    path[source] = []
    
    # Priority queue: (distance, vertex)
    heap = []
    heappush(heap, (0, source))
    
    while heap:
        current_dist, u = heappop(heap)
        
        # Skip if we've already found a better path
        if current_dist > dist[u]:
            continue
            
        # Check all neighbors of u
        if u in graph:
            for v in graph[u]:
                # Calculate distance through u to v
                new_dist = dist[u] + graph[u][v]
                
                # If we found a shorter path, update it
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    path[v] = path[u] + [u]
                    heappush(heap, (new_dist, v))
    
    return dist, path

