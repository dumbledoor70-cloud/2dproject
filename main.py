"""운론천하: 주사위로 영토를 넓히는 2인 턴제 보드게임."""
import random


BOARD_SIZE = 7
MAX_TURNS = 20
EFFECTS = ("안개", "보급", "전염병")


class UnRonCheonHa:
    """게임 보드와 플레이어 상태를 보관한다."""

    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.turn = 1
        self.current_player = 1
        self.winner = None
        self.players = {
            1: {"position": (0, 0), "troops": 800, "skip": False, "forts": 0},
            2: {"position": (6, 6), "troops": 800, "skip": False, "forts": 0},
        }
        self.board = [[{"kind": "land", "owner": 0, "effect": None, "garrison": 0}
                       for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.setup_board()

    def setup_board(self):
        """본성, 거점, 특수 칸을 무작위로 배치한다."""
        self.board[0][0].update(kind="base", owner=1)
        self.board[6][6].update(kind="base", owner=2)
        available = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                     if (r, c) not in ((0, 0), (6, 6))]
        self.rng.shuffle(available)
        for r, c in available[:3]:
            self.board[r][c]["kind"] = "fort"
        special = available[3:9]
        for i, (r, c) in enumerate(special):
            self.board[r][c]["effect"] = EFFECTS[i // 2]


def main():
    game = UnRonCheonHa()
    print("운론천하 — 7×7 주사위 전략전")
    print(f"보드가 준비되었습니다. 거점 {sum(t['kind'] == 'fort' for row in game.board for t in row)}곳")


if __name__ == "__main__":
    main()
