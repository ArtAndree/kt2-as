"""Дополнительные задания. Основное решение находится в main.py."""

from pathlib import Path
from main import load_graph


def dfs_with_cache(graph, start, cache):
    """Кэш результатов подграфов. Только для графа без циклов."""
    if start not in cache:
        result = set()
        for dependency in graph.graph[start]:
            result.add(dependency)
            result.update(dfs_with_cache(graph, dependency, cache))
        cache[start] = result
    return cache[start].copy()


def critical_path(graph, weights):
    order = graph.get_topological_order()
    if order is None:
        raise ValueError("Обнаружен цикл")

    distance = {}
    paths = {}
    for name in order:
        distance[name] = 0
        paths[name] = [name]
        for dependency in graph.graph[name]:
            weight = weights.get((name, dependency), 1)
            if weight < 0:
                raise ValueError("Вес не должен быть отрицательным")
            candidate = distance[dependency] + weight
            if candidate > distance[name]:
                distance[name] = candidate
                paths[name] = paths[dependency] + [name]

    if not order:
        return [], 0
    end = max(order, key=distance.get)
    return paths[end], distance[end]


def draw_graph(graph, weights, filename):
    # Нужны Python-пакет graphviz и установленная программа Graphviz.
    from graphviz import Digraph

    picture = Digraph(format="svg")
    for name in graph.graph:
        picture.node(name)
        for dependency in graph.graph[name]:
            weight = weights.get((name, dependency), 1)
            picture.edge(name, dependency, label=str(weight))
    picture.render(filename, cleanup=True)


if __name__ == "__main__":
    folder = Path(__file__).parent
    graph = load_graph(folder / "dependencies.txt")
    # Вес ребра (компонент, его зависимость). Неуказанный вес равен 1.
    weights = {("A", "B"): 3, ("A", "C"): 2, ("B", "D"): 4,
               ("C", "D"): 1, ("C", "E"): 5, ("E", "B"): 2}

    if graph.is_acyclic():
        cache = {}
        print("DFS с кэшем:", sorted(dfs_with_cache(graph, "A", cache)))
        path, total = critical_path(graph, weights)
        print("Критический путь в порядке сборки:", " -> ".join(path))
        print("Сумма весов:", total)
        if input("Создать SVG через Graphviz? [да/нет]: ").strip().lower() == "да":
            draw_graph(graph, weights, str(folder / "graph"))
            print("Сохранено: graph.svg")
    else:
        print("Обнаружен цикл")
