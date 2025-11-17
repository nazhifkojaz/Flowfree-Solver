import time
from flowfree.stats import bump, ensure_keys, new_stats

from .board import Board, Coord
from .node import Node
from .propagation import Propagation

INF = 10**12


class Solver:
    def __init__(
        self,
        board: Board,
        NODE_CAP: int = 100_000,
        TIME_CAP: float = 300.0,
        metrics: dict[str, int | float] | None = None,
    ):
        self.root = Node(board=board)
        self.root.compute_key()
        self.root.depth = 0
        self._node_cap = NODE_CAP
        self._time_cap = TIME_CAP
        # legacy attribute name kept for compatibility with existing analysis scripts
        self.max_nodes = NODE_CAP
        self.nodes_generated = 1
        self.transpositions: dict[tuple[int, ...], Node] = {}
        base_extra = {
            "expansions": 0,
            "terminal_proved": 0,
            "terminal_disproved": 0,
            "tt_hits": 0,
            "tt_max_entries": 0,
            "max_depth": 0,
            "max_branching": 0,
        }
        self.metrics = metrics if metrics is not None else new_stats(base_extra)
        if metrics is not None:
            # merge user-supplied metrics into the canonical schema
            merged = new_stats(base_extra)
            merged.update(metrics)
            self.metrics = merged
        else:
            ensure_keys(self.metrics, base_extra.keys())
        ensure_keys(
            self.metrics,
            (
                "propagations_calls",
                "propagations_rounds",
                "propagations_forced_moves",
                "propagations_degree_moves",
                "propagations_contradictions",
                "decision_nodes",
                "abort_timeout",
                "abort_node_cap",
                "stopped",
            ),
        )

    def is_terminal(self, board: Board) -> tuple[bool, int, int]:
        if board.is_solved():
            return True, 0, INF
        if (
            Propagation.any_color_disconnected(board)
            or Propagation.stranded_empty_exists(board)
            or not board.empty_regions_port_ok()
        ):
            return True, INF, 0
        if not board.legal_moves():
            return True, INF, 0
        return False, 1, 1

    def select_mpn(self, node: Node) -> Node:
        current = node
        while current.expanded and current.children:
            current = min(current.children, key=lambda child: (child.pn, child.dn))
        return current

    def expand(self, node: Node) -> None:
        if node.expanded:
            return

        board = node.board
        terminal, pn, dn = self.is_terminal(board)
        if terminal:
            node.pn, node.dn = pn, dn
            node.expanded = True
            if pn == 0:
                self.metrics["terminal_proved"] += 1
            else:
                self.metrics["terminal_disproved"] += 1
            return

        self.metrics["decision_nodes"] += 1
        children = []
        self.metrics["expansions"] += 1
        for move in board.legal_moves():
            if self.nodes_generated >= self._node_cap:
                break
            head, dst = move
            color = board.grid[head]
            if color <= 0:
                continue

            new_board = board.clone()
            new_board.paint(dst, color)
            if (
                Propagation.any_color_disconnected(new_board)
                or Propagation.stranded_empty_exists(new_board)
                or not new_board.empty_regions_port_ok()
            ):
                continue
            if not Propagation.run(new_board, self.metrics):
                continue

            child = Node(board=new_board, parent=node)
            child.compute_key()

            if child.key in self.transpositions:
                cached = self.transpositions[child.key]
                child.pn, child.dn = cached.pn, cached.dn
                bump(self.metrics, "tt_hits")
            else:
                self.transpositions[child.key] = child
                self.metrics["tt_max_entries"] = max(
                    self.metrics["tt_max_entries"], len(self.transpositions)
                )

            term, child_pn, child_dn = self.is_terminal(new_board)
            child.pn, child.dn = (child_pn, child_dn) if term else (1, 1)
            if term:
                if child_pn == 0:
                    self.metrics["terminal_proved"] += 1
                else:
                    self.metrics["terminal_disproved"] += 1

            children.append(child)
            self.nodes_generated += 1
            self.metrics["attempts"] += 1
            child.depth = node.depth + 1
            self.metrics["max_depth"] = max(self.metrics["max_depth"], child.depth)

        node.children = children
        node.expanded = True
        self.metrics["max_branching"] = max(
            self.metrics["max_branching"], len(children)
        )
        self.metrics["total_branching"] += len(children)
        if not node.children:
            self.metrics["backtracks"] += 1
        if not node.children:
            node.pn, node.dn = INF, 0

    def update_ancestors(self, node: Node | None) -> None:
        current = node
        while current is not None:
            if current.children:
                current.pn = min(child.pn for child in current.children)
                dn_sum = 0
                overflow = False
                for child in current.children:
                    dn_sum += child.dn
                    if dn_sum >= INF:
                        overflow = True
                        break
                current.dn = INF if overflow else dn_sum
            current = current.parent

    def _finalize_and_pack(
        self,
        elapsed: float,
        iterations: int,
        timeout_hit: bool,
        node_cap_hit: bool,
    ) -> dict[str, int | float | bool]:
        ensure_keys(self.metrics, ("abort_timeout", "abort_node_cap", "stopped"))
        self.metrics["iterations"] = iterations
        self.metrics["nodes_generated"] = self.nodes_generated
        self.metrics["tree_depth"] = max(
            self.metrics.get("tree_depth", 0), self.metrics.get("max_depth", 0)
        )
        self.metrics["time_s"] = elapsed
        self.metrics["abort_timeout"] = timeout_hit
        self.metrics["abort_node_cap"] = node_cap_hit
        self.metrics["stopped"] = timeout_hit or node_cap_hit
        self.metrics["proof_pn_root"] = self.root.pn
        self.metrics["proof_dn_root"] = self.root.dn
        return dict(self.metrics)

    def solve(self) -> tuple[bool, Board | None, dict[str, int | float | bool]]:
        start = time.perf_counter()
        iterations = 0
        timeout_hit = False
        node_cap_hit = False

        while True:
            elapsed = time.perf_counter() - start
            if elapsed >= self._time_cap:
                timeout_hit = True
                break
            if self.nodes_generated >= self._node_cap:
                node_cap_hit = True
                break

            leaf = self.select_mpn(self.root)
            self.expand(leaf)
            self.update_ancestors(leaf)
            iterations += 1
            self.metrics["iterations"] = iterations

            if self.root.pn == 0:
                stats = self._finalize_and_pack(elapsed, iterations, False, False)
                return True, self._extract_solution(), stats
            if self.root.dn == 0:
                stats = self._finalize_and_pack(elapsed, iterations, False, False)
                return False, None, stats

        elapsed = time.perf_counter() - start
        solved = self.root.pn == 0
        solution_board = self._extract_solution() if solved else None
        stats = self._finalize_and_pack(elapsed, iterations, timeout_hit, node_cap_hit)
        return solved, solution_board, stats


    def _extract_solution(self) -> Board | None:
        node = self.root
        seen_ids = set()
        while node.children:
            solutions = [child for child in node.children if child.pn == 0]
            if solutions:
                node = solutions[0]
            else:
                node = min(node.children, key=lambda child: (child.pn, child.dn))
            if id(node) in seen_ids:
                break
            seen_ids.add(id(node))
            if node.board.is_solved():
                return node.board
        if node.board.is_solved():
            return node.board
        return None
