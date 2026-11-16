"""운론천하: 주사위로 영토를 넓히는 2인 턴제 보드게임."""
import random
import sys
import tkinter as tk
from pathlib import Path


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
        self.last_message = "방향과 출정 병력을 정하고 이동하세요."
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
            self.players[defender_id]["position"] = (0, 0) if defender_id == 1 else (6, 6)
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

    def advance_turn(self):
        """차례를 넘기고 다음 플레이어의 본성·거점 수입을 지급한다."""
        if self.winner is not None:
            return
        if self.turn >= MAX_TURNS:
            lands1, _ = self.territory_count(1)
            lands2, _ = self.territory_count(2)
            if lands1 != lands2:
                self.winner = 1 if lands1 > lands2 else 2
            else:
                troops1 = self.players[1]["troops"]
                troops2 = self.players[2]["troops"]
                self.winner = 1 if troops1 > troops2 else 2 if troops2 > troops1 else 0
            return
        self.turn += 1
        self.current_player = 3 - self.current_player
        player_id = self.current_player
        income = sum(100 for row in self.board for tile in row
                     if tile["owner"] == player_id and tile["kind"] in ("base", "fort"))
        self.players[player_id]["troops"] += income

    def run(self):
        """터미널에서 두 사람이 번갈아 진행하는 게임을 실행한다."""
        print("운론천하 — 주사위로 펼치는 천하통일")
        while self.winner is None:
            self.display()
            player = self.players[self.current_player]
            if player["skip"]:
                player["skip"] = False
                print("안개 때문에 이번 차례는 쉽니다.")
                self.advance_turn()
                continue
            while True:
                direction = input("이동 방향 (북/남/동/서): ").strip()
                if direction in ("북", "남", "동", "서"):
                    break
                print("북, 남, 동, 서 중 하나를 입력하세요.")
            while True:
                try:
                    march = int(input(f"출정 병력 (100~{player['troops']}, 100명 단위): "))
                except ValueError:
                    print("병력은 숫자로 입력하세요.")
                    continue
                if 100 <= march <= player["troops"] and march % 100 == 0:
                    break
                print("보유 병력 범위 안에서 100명 단위로 입력하세요.")
            print(self.move(direction, march))
            self.advance_turn()
        self.display()
        if self.winner == 0:
            print("20차례 종료 · 영토와 병력 수가 같아 무승부입니다.")
        else:
            print(f"플레이어 {self.winner} 승리! 천하를 통일했습니다.")


class GameWindow:
    """Tkinter 보드와 두 플레이어의 조작 패널을 만든다."""

    def __init__(self, root):
        self.root = root
        self.game = UnRonCheonHa()
        self.root.title("운론천하 · 주사위 전략전")
        self.root.configure(bg="#172233")
        self.root.resizable(False, False)
        self.direction = tk.StringVar(value="동")
        self.march = tk.IntVar(value=100)
        self.board_image = tk.PhotoImage(file=str(Path(__file__).with_name("board.png"))).subsample(4, 4)
        self.canvas = tk.Canvas(root, width=525, height=525, highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=10, padx=18, pady=18)
        panel = tk.Frame(root, bg="#202e43", padx=18, pady=16)
        panel.grid(row=0, column=1, sticky="n", padx=(0, 18), pady=18)
        self.turn_label = tk.Label(panel, text="", font=("맑은 고딕", 16, "bold"), bg="#202e43", fg="#f5d58a")
        self.turn_label.pack(anchor="w")
        self.status_label = tk.Label(panel, text="", wraplength=245, justify="left", font=("맑은 고딕", 10), bg="#202e43", fg="white", height=3)
        self.status_label.pack(anchor="w", pady=(4, 12))
        self.stats = {}
        for pid in (1, 2):
            self.stats[pid] = tk.Label(panel, text="", justify="left", font=("맑은 고딕", 10, "bold"), bg="#2b3c53", fg="white", padx=9, pady=8)
            self.stats[pid].pack(fill="x", pady=4)
        tk.Label(panel, text="출정 병력 (100명 단위)", font=("맑은 고딕", 10, "bold"), bg="#202e43", fg="white").pack(anchor="w", pady=(13, 4))
        self.march_spin = tk.Spinbox(panel, from_=100, to=800, increment=100, textvariable=self.march, width=8, font=("맑은 고딕", 11))
        self.march_spin.pack(anchor="w")
        tk.Label(panel, text="이동 방향", font=("맑은 고딕", 10, "bold"), bg="#202e43", fg="white").pack(anchor="w", pady=(12, 4))
        for direction in ("북", "동", "남", "서"):
            tk.Radiobutton(panel, text=direction, variable=self.direction, value=direction, indicatoron=False,
                           width=6, pady=4, bg="#344963", fg="white", selectcolor="#247d77",
                           activebackground="#247d77", activeforeground="white").pack(side="left", padx=2)
        self.move_button = tk.Button(panel, text="주사위 굴리고 이동", command=self.on_move,
                                     font=("맑은 고딕", 11, "bold"), bg="#d9ae55", fg="#172233",
                                     relief="flat", pady=9, cursor="hand2")
        self.move_button.pack(fill="x", pady=(16, 10))
        tk.Label(panel, text="칸 안내\n◆ 본성   ★ 거점\n안 안개   + 보급   전 전염병",
                 justify="left", font=("맑은 고딕", 9), bg="#202e43", fg="#afbdd0").pack(anchor="w")
        self.render()

    def on_move(self):
        """이동 버튼을 처리하고 차례를 진행한다."""
        game = self.game
        player = game.players[game.current_player]
        if player["skip"]:
            player["skip"] = False
            game.last_message = "안개 때문에 이번 차례는 쉽니다."
            game.advance_turn()
        else:
            try:
                march = int(self.march.get())
            except (ValueError, tk.TclError):
                game.last_message = "출정 병력을 100명 단위로 입력하세요."
                self.render()
                return
            result = game.move(self.direction.get(), march)
            if result.startswith(("방향은", "출정 병력은")):
                game.last_message = result
                self.render()
                return
            game.last_message = result
            game.advance_turn()
        self.render()
        if game.winner is not None:
            self.move_button.config(state="disabled")
            winner = "무승부" if game.winner == 0 else f"플레이어 {game.winner} 승리"
            game.last_message += f"\n{winner}!"
            self.status_label.config(text=game.last_message)

    def render(self):
        """보드 이미지 위에 영토, 특수 칸, 장수를 그린다."""
        game = self.game
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.board_image, anchor="nw")
        cell, margin = 72.15, 10.5
        effect_labels = {"안개": "安", "보급": "+", "전염병": "疫"}
        for r, row in enumerate(game.board):
            for c, tile in enumerate(row):
                x, y = margin + c * cell, margin + r * cell
                color = {0: "#65748a", 1: "#23a99b", 2: "#df725e"}[tile["owner"]]
                if tile["owner"]:
                    self.canvas.create_rectangle(x + 4, y + 4, x + cell - 4, y + cell - 4,
                                                 fill=color, stipple="gray25", outline=color, width=2)
                label = effect_labels.get(tile["effect"], {"land": "", "base": "◆", "fort": "★"}[tile["kind"]])
                if label:
                    self.canvas.create_text(x + cell/2, y + 20, text=label,
                                             fill="#a3392f" if tile["effect"] == "전염병" else "#8e671f",
                                             font=("맑은 고딕", 17, "bold"))
                if tile["garrison"]:
                    self.canvas.create_text(x + cell - 13, y + cell - 13, text=str(tile["garrison"] // 100),
                                             fill="#27364b", font=("맑은 고딕", 9, "bold"))
                for pid, player in game.players.items():
                    if player["position"] == (r, c):
                        self.canvas.create_oval(x + 20, y + 32, x + 51, y + 63,
                                                fill="#1c3937" if pid == 1 else "#562b2b", outline="white", width=2)
                        self.canvas.create_text(x + 35.5, y + 47.5, text=str(pid), fill="white",
                                                font=("맑은 고딕", 13, "bold"))
        self.turn_label.config(text=f"차례 {game.turn} / {MAX_TURNS} · P{game.current_player}")
        self.status_label.config(text=game.last_message)
        for pid, player in game.players.items():
            lands, forts = game.territory_count(pid)
            self.stats[pid].config(text=f"플레이어 {pid}   병력 {player['troops']:,}명\n영토 {lands}곳 · 거점 {forts}/3 · 수입 +{sum(100 for row in game.board for t in row if t['owner']==pid and t['kind'] in ('base','fort'))}명",
                                   fg="#72d4c5" if pid == 1 else "#ff9b88")
        maximum = max(100, game.players[game.current_player]["troops"] // 100 * 100)
        self.march_spin.config(to=maximum)
        if self.march.get() > maximum:
            self.march.set(maximum)


def main():
    if "--cli" in sys.argv:
        UnRonCheonHa().run()
        return
    root = tk.Tk()
    GameWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
