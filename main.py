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

    def territory_count(self, player_id):
        """플레이어가 소유한 전체 영토 수와 거점 수를 반환한다."""
        owned = [tile for row in self.board for tile in row if tile["owner"] == player_id]
        forts = sum(tile["kind"] == "fort" for tile in owned)
        return len(owned), forts

    def display(self):
        """현재 보드와 두 플레이어의 주요 수치를 출력한다."""
        symbols = {"land": "·", "base": "城", "fort": "★"}
        effects = {"안개": "안", "보급": "+", "전염병": "전"}
        print(f"\n차례 {self.turn}/{MAX_TURNS} · 플레이어 {self.current_player}")
        for r, row in enumerate(self.board):
            cells = []
            for c, tile in enumerate(row):
                symbol = effects.get(tile["effect"], symbols[tile["kind"]])
                for pid, player in self.players.items():
                    if player["position"] == (r, c):
                        symbol = f"P{pid}"
                cells.append(f"{symbol:^3}")
            print("|" + "|".join(cells) + "|")
        for pid, player in self.players.items():
            lands, forts = self.territory_count(pid)
            print(f"P{pid}: 병력 {player['troops']}명 · 영토 {lands}곳 · 거점 {forts}/3")


def main():
    game = UnRonCheonHa()
    print("운론천하 — 7×7 주사위 전략전")
    game.display()


if __name__ == "__main__":
    main()
