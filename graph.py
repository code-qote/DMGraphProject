import dataclasses
from collections import deque


class Graph:

    def __init__(self, directed):
        self.graph = dict()
        self.directed = directed
        self.nodes = set()

    def add_edge(self, node1, node2, directed):
        if node1 not in self.graph:
            self.graph[node1] = set()
        self.graph[node1].add(node2)
        if not directed:
            if node2 not in self.graph:
                self.graph[node2] = set()
            self.graph[node2].add(node1)
        else:
            self.graph[node2] = self.graph.get(node2, set())
        self.nodes.add(node1)
        self.nodes.add(node2)

    def remove_edge(self, node1, node2):
        if node2 in self.graph[node1]:
            self.graph[node1].remove(node2)
        if node1 in self.graph[node2]:
            self.graph[node2].remove(node1)

    def _is_connectivity_valid(self, graph) -> bool:
        visited = dict()
        for v in graph:
            visited[v] = False
        for v in graph:
            if len(graph[v]) > 0:
                self._dfs(v, visited)
                break
        for v in graph:
            if len(graph[v]) > 0 and not visited[v]:
                return False
        return True

    def _get_weak_connectivity(self) -> dict:
        res = dict()
        for v in self.graph:
            res[v] = self.graph[v]
            for u in self.graph[v]:
                res[u] = res.get(u, set()).add(v)
        return res

    def check_euler_path_directed(self) -> bool:
        in_degree = dict()
        out_degree = dict()

        for v in self.graph:
            out_degree[v] = len(self.graph[v])
            for u in self.graph[v]:
                in_degree[u] = in_degree.get(u, 0) + 1

        delta = []
        for v in self.graph:
            delta.append(in_degree.get(v, 0) - out_degree.get(v, 0))

        return delta.count(1) <= 1 and delta.count(-1) <= 1

    def check_euler_path(self) -> bool:
        if not self.graph:
            return False

        if self.directed:
            return self.check_euler_path_directed()
        odd_v = 0
        for v in self.graph:
            if len(self.graph[v]) % 2 != 0:
                odd_v += 1
        if odd_v > 2:
            return False
        return self._is_connectivity_valid(self.graph)

    def _dfs(self, u, visited):
        visited[u] = True
        for v in self.graph[u]:
            if not visited[v]:
                self._dfs(v, visited)

    def find_euler_path(self):
        if not self.graph:
            green_nodes = list(self.nodes)
            states = [{"yellow_nodes": set(), "red_nodes": set(),
                           "red_edges": set(), "green_nodes": green_nodes, "green_edges": set()}]
            return states

        start = list(self.graph.keys())[0]
        for v in self.graph:
            if len(self.graph[v]) % 2 != 0:
                start = v
                break
        s = deque()
        s.append(start)
        res = []
        states = []
        yellow_nodes = set()
        red_edges = set()
        red_nodes = set()
        green_edges = []
        states.append({"yellow_nodes": yellow_nodes.copy(), "red_nodes": red_nodes.copy(),
                       "red_edges": red_edges.copy(), "green_nodes": res.copy(), "green_edges": green_edges.copy()})
        while s:
            w = s[0]
            yellow_nodes.add(w)
            found_edge = False
            if self.graph[w]:
                u = self.graph[w].pop()
                red_nodes.add(u)
                red_edges.add((w, u))
                s.appendleft(u)
                if w in self.graph[u]:
                    self.graph[u].remove(w)
                found_edge = True
            if not found_edge:
                if s:
                    p = s.popleft()
                    if res:
                        green_edges.append((res[-1], p))
                    res.append(p)
            state = {"yellow_nodes": yellow_nodes.copy(), "red_nodes": red_nodes.copy(),
                           "red_edges": red_edges.copy(),
                           "green_nodes": list(reversed(res.copy())),
                           "green_edges": green_edges.copy()}
            if states[-1] != state:
                states.append(state)

        return states

    def hamilton_cycle(self):
        visited = dict()
        for v in self.graph:
            visited[v] = False

        path = []
        states = []
        yellow_nodes = set()
        red_edges = set()
        red_nodes = set()
        green_edges = set()
        states.append({"yellow_nodes": yellow_nodes.copy(), "red_nodes": red_nodes.copy(),
                       "red_edges": red_edges.copy(), "green_nodes": path.copy(), "green_edges": green_edges.copy()})

        def hamilton(u):
            if path:
                green_edges.add((path[-1], u))
            path.append(u)
            states.append({"yellow_nodes": yellow_nodes.copy(), "red_nodes": red_nodes.copy(),
                           "red_edges": red_edges.copy(), "green_nodes": path.copy(),
                           "green_edges": green_edges.copy()})
            if len(path) == len(self.graph):
                if path[-1] in self.graph[path[0]]:
                    return True
                else:
                    path.pop()
                    return False
            visited[u] = True
            for v in self.graph:
                if v in self.graph[u] and not visited[v]:
                    red_edges.add((u, v))
                    red_nodes.add(v)
                    states.append({"yellow_nodes": yellow_nodes.copy(), "red_nodes": red_nodes.copy(),
                                   "red_edges": red_edges.copy(), "green_nodes": path.copy(),
                                   "green_edges": green_edges.copy()})
                    if hamilton(v):
                        return True
            visited[u] = False
            path.pop()
            states.append({"yellow_nodes": yellow_nodes.copy(), "red_nodes": red_nodes.copy(),
                           "red_edges": red_edges.copy(), "green_nodes": path.copy(),
                           "green_edges": green_edges.copy()})
            return False

        start = list(self.graph.keys())[0]
        hamilton(start)
        if states[-1]["green_nodes"]:
            states[-1]["green_edges"].add((states[-1]["green_nodes"][-1], states[-1]["green_nodes"][0]))
            states[-1]["green_nodes"].append(states[-1]["green_nodes"][0])

        return states

    def hamilton_path(self):

        @dataclasses.dataclass
        class Item:
            weight: int
            path: list

        states = []
        yellow_nodes = set()
        red_nodes = set()
        red_edges = set()
        green_nodes = []
        green_edges = set()
        states.append({"yellow_nodes": yellow_nodes.copy(), "red_nodes": red_nodes.copy(),
                       "red_edges": red_edges.copy(), "green_nodes": green_nodes.copy(),
                       "green_edges": green_edges.copy()})

        INF = 10 ** 15
        n = len(self.nodes)
        self.nodes = sorted(list(self.nodes))

        mask_dict = dict()
        for i in range(n):
            mask_dict[self.nodes[i]] = i

        dp = dict()
        for v in self.nodes:
            for mask in range(1 << n):
                dp[v] = dp.get(v, [])
                if mask == 1 << mask_dict[v]:
                    dp[v].append(Item(0, [v]))
                else:
                    dp[v].append(Item(INF, [v]))

        for mask in range(1 << n):
            for v in self.nodes:
                yellow_nodes.clear()
                red_nodes.clear()
                green_nodes.clear()
                for u in self.nodes:
                    if mask & (1 << mask_dict[u]):
                        red_nodes.add(u)
                        continue
                    newmask = mask | (1 << mask_dict[u])
                    yellow_nodes.add(u)
                    if u in self.graph.get(v, set()) or (not self.directed and v in self.graph.get(u, set())):
                        red_edges.add((v, u))
                        if dp[v][mask].weight + 1 < dp[u][newmask].weight:
                            dp[u][newmask].weight = dp[v][mask].weight + 1
                            dp[u][newmask].path = dp[v][mask].path + [u]
                            green_edges.add((v, u))
            states.append({"yellow_nodes": yellow_nodes.copy(), "red_nodes": red_nodes.copy(),
                           "red_edges": red_edges.copy(), "green_nodes": green_nodes.copy(),
                           "green_edges": green_edges.copy()})

        path_weight = INF
        last = None

        for u in self.nodes:
            if dp[u][(1 << n) - 1].weight < path_weight:
                path_weight = dp[u][(1 << n) - 1].weight
                last = u

        if path_weight != INF:
            green_nodes = dp[last][(1 << n) - 1].path
            states.append({"yellow_nodes": yellow_nodes.copy(), "red_nodes": red_nodes.copy(),
                           "red_edges": red_edges.copy(), "green_nodes": green_nodes.copy(),
                           "green_edges": green_edges.copy()})
        return states
