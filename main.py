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

    def move(self, direction, march):
        """병력을 정한 뒤 주사위를 굴려 이동하고 도착 칸을 처리한다."""
        if self.winner is not None:
            return "게임이 이미 끝났습니다."
        player_id = self.current_player
        player = self.players[player_id]
        if direction not in ("북", "남", "동", "서"):
            return "방향은 북, 남, 동, 서 중에서 골라야 합니다."
        if not isinstance(march, int) or march < 100 or march % 100 or march > player["troops"]:
            return "출정 병력은 보유 병력 안에서 100명 단위로 정하세요."
        if player["skip"]:
            player["skip"] = False
            return "안개 때문에 이번 차례는 이동할 수 없습니다."

        dice = self.rng.randint(1, 6)
        dr, dc = {"북": (-1, 0), "남": (1, 0), "동": (0, 1), "서": (0, -1)}[direction]
        r, c = player["position"]
        destination = (r + dr * dice, c + dc * dice)
        if not (0 <= destination[0] < BOARD_SIZE and 0 <= destination[1] < BOARD_SIZE):
            return f"주사위 {dice} · 남은 칸보다 커서 이동하지 못했습니다."

        source = self.board[r][c]
        target = self.board[destination[0]][destination[1]]
        force = march
        if target["owner"] not in (0, player_id):
            defender_id = 3 - player_id
            defense = target["garrison"]
            if self.players[defender_id]["position"] == destination:
                defense += self.players[defender_id]["troops"]
            if force <= defense:
                return f"주사위 {dice} · 수비 병력 {defense}명에게 막혔습니다."
            force -= defense
            target["garrison"] = 0
            self.players[defender_id]["troops"] = 0
            target["owner"] = player_id
        elif target["owner"] == player_id:
            force += target["garrison"]
            target["garrison"] = 0
        else:
            target["owner"] = player_id

        source["garrison"] += player["troops"] - march
        player["position"] = destination
        player["troops"] = force
        result = f"주사위 {dice} · {direction}으로 이동했습니다."
        effect = target["effect"]
        if effect == "보급":
            player["troops"] += 100
            result += " 보급 +100명."
        elif effect == "전염병":
            player["troops"] = max(0, player["troops"] - 100)
            result += " 전염병 -100명."
        elif effect == "안개":
            player["skip"] = True
            result += " 안개에 갇혀 다음 차례를 쉽니다."
        target["effect"] = None

        own_base = (0, 0) if player_id == 1 else (6, 6)
        if target["kind"] == "base" and destination != own_base:
            self.winner = player_id
            result += f" 적 본성을 함락해 플레이어 {player_id} 승리!"
        _, forts = self.territory_count(player_id)
        if forts >= 2:
            self.winner = player_id
            result += f" 거점 2곳을 확보해 플레이어 {player_id} 승리!"
        return result


def main():
    game = UnRonCheonHa()
    print("운론천하 — 7×7 주사위 전략전")
    game.display()


if __name__ == "__main__":
    main()
