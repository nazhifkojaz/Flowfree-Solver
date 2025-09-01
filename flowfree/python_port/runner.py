from csp_board import Board
from csp_fc import FC
from csp_solver import BtAlgo


def parse_preassign(initial: str) -> tuple[dict[int, int], int]:
    mapping: dict[int, int] = {}
    max_color = 0
    for i, ch in enumerate(initial.strip()):
        if ch != "x":
            val = int(ch)
            mapping[i] = val
            if val > max_color:
                max_color = val
    return mapping, max_color


def solve_puzzle(initial: str, height: int, width: int) -> str | None:
    pre, n_colors = parse_preassign(initial)
    board = Board(width, height, n_colors if n_colors > 0 else 1)
    board.Preassign(pre)

    FC.Reset()
    solver = BtAlgo(board)
    ok = solver.search()

    return {
        "board": board.AsString() if ok else None,
        "stats": solver._stats,
    }


# --- Smoke test with provided suite ---

tests = [
    ("2xxxx3xx1xx1xxxx3xxxxxxx2", "2222233312113121331211112", 5, 5),
    ("xxxxxxxxxxx23xx13xxx2xxx1", "1111112221123211332122221", 5, 5),
    ("x1223xxxxxxx1xxxxx3xxxxxx", "1122313333131111333111111", 5, 5),
    (
        "5xxxx25x3xx14x4xx3xxxxxxx2xx1xxxxxxx",
        "522222523311424313424313424313444333",
        6,
        6,
    ),
    (
        "3xxxx2xx1x5xxx4xxxxxxxx5xx2xxxxx3x41",
        "322222321155324115324415322411333441",
        6,
        6,
    ),
    (
        "5x3xx32xxxxxxxx1x54xx2xx1xxx4xxxxxxx",
        "553333255555222115442211144441111111",
        6,
        6,
    ),
    (
        "xxx2x5xx4xxx1xxx4x2xxxx1x5xxxx3x3xxxxxxxxxxxxxxxx",
        "5552255545521554452155115515513331551111155555555",
        7,
        7,
    ),
    (
        "3xxxxxxxxxxx12xxxx354xxxx5xxxx1xxxxxxxx2xxxxxxxx4",
        "3222222321111232133543213554321333432222343333334",
        7,
        7,
    ),
    (
        "xxxxxxxxxxx1xx5x3x2xxxxx4xxxxxxxx5xx34xx12xxxxxxx",
        "5555555522211552322152234115233415523441122222222",
        7,
        7,
    ),
    (
        "xxxxxxx5xxxxx43xx4xxxxxxxxx5xxxxxx2xxxxxxx6x2x1xxx1xxxxxxxx3xxx6",
        "3333333534444435341111153115551531222515316625153116655533336666",
        8,
        8,
    ),
    (
        "xxxxxx23xxx51xxxx54xxx62xxxxxxxxxxxxxxxxxxx3x61xx4xxxxxxxxxxxxxx",
        "2222222325551333254113622441336224113662241336122411111222222222",
        8,
        8,
    ),
    (
        "6xxxxxx51xxxxxx32xx2xxxx61xxxxxxxxxxxxxx3xxxx4xxx45xxxxxxxxxxxxx",
        "6666665511111653222216536111165366666653344444533455555333333333",
        8,
        8,
    ),
    (
        "xxxxxxxxxxxxxxxx2xxx5xxxxxxx27xxx7xxxx6x154xxxxxx3xxxxx3xxxx4xxxxxx1xxxx6xxxxxxxx",
        "666666666622222226625555556627777756666115456111135456133335456111115556666666666",
        9,
        9,
    ),
    (
        "6xxxxxx3xxxxx17xxxxx2xxxxxxx25xx4xxx5xxxxxxxx1x4xxxxxxxxxxxxxxxx3x6xxxxxx7xxxxxxx",
        "666666633555517663522517763525514763511114763114444763777777763733666663773333333",
        9,
        9,
    ),
    (
        "xx1xxxxx3xxxxxx5xxx75xxx3xxx6x4xxxxxxxxxxxx2xxxxx27xxxxx4xxxxxxxx6xxxxx1xxxxxxxxx",
        "111777773177755573175553373164433773164337723164327223164322233166333331111111111",
        9,
        9,
    ),
    (
        "xxxxxxxxx6x2xx5xxxxxxxxxxx698xxxxxxxxxxxxxxx4xx3xxx2x1xx57xxxxxxxxxxxx3xxxxx87xxx941xxxxxxxxxxxxxxxx",
        "9996666666929655555592966669859299999985924443338592413357859941355785394135878539413588853333355555",
        10,
        10,
    ),
    (
        "xxx6xxxxxxxx71x5x89xxxxxxxxxx3xxxxxxxxx2xxxxxxxx26xxxxx48x9xxxxxxxx47xxx13xxx5xxxxxxxxxxxxxxxxxxxxxx",
        "6666333333677135889367113589936713358922671355892667135489966713544476671355557667777777766666666666",
        10,
        10,
    ),
    (
        "xxx4xxxxx9x2xx7xxxxxxxxxxx8xxxx785xxxxxx6xxxx5xx4x1xx6xxxxxxxxxxxxxxxxxxxxxx9xxxx3xxxx312xxxxxxxxxxx",
        "7774444449727772224972222282497785558249668885824916668882291111111129999999912993333331299999999999",
        10,
        10,
    ),
]

results = []
for init, complete, h, w in tests:
    print(f"solving {init}")
    solved = solve_puzzle(init, h, w)
    print(f"complete {complete}")
    print(f"solved {solved["board"]}")
    print(solved["stats"])
    results.append((h, w, init, complete, solved, solved == complete))
