from multiprocessing.managers import DictProxy
from typing import Dict, List


def is_dead(father_process_dag: "DictProxy[str, List[str]]") -> bool:
    with father_process_dag._mutex:
        dead = (
            len([v for v in dict(father_process_dag).values() if "error" not in v]) <= 1
        )
    return dead


def is_finished_with_errors(father_process_dag: "DictProxy[str, List[str]]") -> bool:
    with father_process_dag._mutex:
        has_errors = (
            len([v for v in dict(father_process_dag).values() if "error" in v]) >= 1
        )
    dead = is_dead(father_process_dag)

    killme = dead and has_errors
    if killme:
        print("Pipeline has errors and will be closed")
    return killme


def register_father_son(
    father_process_dag: "DictProxy[str, List[str]]", father: str, son: str
):
    with father_process_dag._mutex:
        dag: Dict[str, List[str]] = father_process_dag._getvalue()
        if father not in dag:
            father_process_dag[father] = [son]
        else:
            father_process_dag[father] = [
                *dag[father],
                son,
            ]


def format_node_name(node: str) -> str:
    import psutil

    try:
        p = psutil.Process(int(node))
        return f"({node}) {p.name()}"
    except Exception:
        return node


def make_dot_graph(debug_graph: str, father_process_dag: "DictProxy[str, List[str]]"):
    from graphviz import Digraph  # type: ignore

    dot = Digraph("G", filename=debug_graph, format="png")

    with father_process_dag._mutex:
        for node, parents in father_process_dag.items():
            dot.node(node, format_node_name(node))

            for parent in parents:
                if parent not in father_process_dag:
                    dot.node(parent, parent)

                if parent:
                    dot.edge(parent, node)

    return dot
