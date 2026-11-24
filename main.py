from collections import deque
from pathlib import Path


class DependencyGraph:
    def __init__(self):
        self.graph = {}

    def add_component(self, name):
        if name not in self.graph:
            self.graph[name] = []

    def add_dependency(self, from_component, to_component):
        # from — служебное слово Python, поэтому используем from_component.
        self.add_component(from_component)
        self.add_component(to_component)
        if to_component not in self.graph[from_component]:
            self.graph[from_component].append(to_component)

    def get_topological_order(self) -> list[str] | None:
        # 0 — не посещали, 1 — сейчас обходим, 2 — полностью обработали.
        state = {name: 0 for name in self.graph}
        order = []

        def visit(name):
            if state[name] == 1:
                return False  # Вернулись к вершине текущего пути: цикл.
            if state[name] == 2:
                return True

            state[name] = 1
            for dependency in self.graph[name]:
                if not visit(dependency):
                    return False

            state[name] = 2
            # Сначала добавляются зависимости, затем сам компонент.
            order.append(name)
            return True

        for name in self.graph:
            if not visit(name):
                return None
        return order

    def is_acyclic(self) -> bool:
        return self.get_topological_order() is not None


class DependencyAnalyzer:
    def __init__(self, graph):
        self.graph = graph

    def find_dependencies_bfs(self, start) -> list[list[str]]:
        if start not in self.graph.graph:
            raise ValueError("Такого компонента нет")
        visited = {start}
        queue = deque([start])
        levels = []

        while queue:
            level = []
            # Обрабатываем только вершины текущего уровня.
            for _ in range(len(queue)):
                current = queue.popleft()
                for dependency in self.graph.graph[current]:
                    if dependency not in visited:
                        visited.add(dependency)
                        queue.append(dependency)
                        level.append(dependency)
            if level:
                levels.append(level)
        return levels

    def find_dependencies_dfs(self, start) -> set[str]:
        if start not in self.graph.graph:
            raise ValueError("Такого компонента нет")
        visited = {start}

        def visit(name):
            for dependency in self.graph.graph[name]:
                if dependency not in visited:
                    visited.add(dependency)
                    visit(dependency)

        visit(start)
        visited.remove(start)
        return visited


def load_graph(filename):
    graph = DependencyGraph()
    with open(filename, encoding="utf-8-sig") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            # Пример строки: A: B, C. Пустой список: D:
            name, dependencies = line.split(":", 1)
            name = name.strip()
            graph.add_component(name)
            for dependency in dependencies.split(","):
                dependency = dependency.strip()
                if dependency:
                    graph.add_dependency(name, dependency)
    return graph


def main():
    folder = Path(__file__).parent
    filename = input("Файл [dependencies.txt]: ").strip() or "dependencies.txt"
    start = input("Компонент [A]: ").strip() or "A"
    try:
        graph = load_graph(folder / filename)
        analyzer = DependencyAnalyzer(graph)
        order = graph.get_topological_order()

        print("Можно собрать проект:", graph.is_acyclic())
        if order is None:
            print("Обнаружен цикл")
        else:
            print("Порядок сборки:", order)
        print("BFS:", analyzer.find_dependencies_bfs(start))
        print("DFS:", sorted(analyzer.find_dependencies_dfs(start)))
    except (OSError, ValueError) as error:
        print("Ошибка:", error)


if __name__ == "__main__":
    main()
