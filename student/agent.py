"""Điểm bắt đầu của bài nộp — sinh viên chỉ cần sửa file này."""

from __future__ import annotations

import numpy as np

from game2048.observation import Observation
from game2048.rules import move_board
from game2048.types import Move


SNAKE_WEIGHTS = np.array([
    [2**0,  2**1,  2**2,  2**3],
    [2**7,  2**6,  2**5,  2**4],
    [2**8,  2**9,  2**10, 2**11],
    [2**15, 2**14, 2**13, 2**12],
], dtype=float)


class Agent:
    name = "AI3_Group_011"

    def reset(self, seed: int | None = None) -> None:
        """Xóa cache/trạng thái giữa hai ván nếu thuật toán có dùng."""

    @staticmethod
    def evaluate(board: np.ndarray, merge_score: int) -> float:
        empty_cells = int(np.count_nonzero(board == 0))
        # Dùng vdot thay cho sum(board * SNAKE_WEIGHTS) để tránh tạo mảng trung gian, tăng tốc tính toán
        snake_score = float(np.vdot(board, SNAKE_WEIGHTS))
        return snake_score + 1000.0 * empty_cells + merge_score * 10.0

    def choose_move(self, obs: Observation, time_limit_ms: float) -> Move:
        if not obs.legal_moves:
            raise ValueError("choose_move được gọi ở trạng thái kết thúc")

        best_move = obs.legal_moves[0]
        best_value = float("-inf")

        # Chốt chặn an toàn: nếu ngân sách cả ván còn dưới 150ms thì hạ xuống nhìn trước 1 nước để tránh timeout
        if time_limit_ms < 150.0:
            for move in obs.legal_moves:
                ban_co_nhap_1, merge_score_1, _ = move_board(obs.board, move)
                gia_tri_cua_move = self.evaluate(ban_co_nhap_1, merge_score_1)
                if gia_tri_cua_move > best_value:
                    best_value = gia_tri_cua_move
                    best_move = move
            return best_move

        # 1. Vòng lặp chọn lần lượt một move trong legal_moves
        for move in obs.legal_moves:
            # 2. Nháp: trạng thái bàn cờ tiếp theo, đưa xuống bot_turn
            ban_co_nhap_1, merge_score_1, _ = move_board(obs.board, move)

            # 3. Tầng trung gian: có k ô trống thì lần lượt xét các ô trống
            cac_o_trong = np.argwhere(ban_co_nhap_1 == 0)
            k = len(cac_o_trong)

            if k == 0:
                gia_tri_cua_move = self.evaluate(ban_co_nhap_1, merge_score_1)
            else:
                tong_diem_k_o = 0.0

                for r, c in cac_o_trong:
                    # --- TRƯỜNG HỢP SINH SỐ 2 ---
                    ban_co_nhap_1[r, c] = 2
                    score2 = float("-inf")
                    co_nuoc_di_2 = False
                    for move_2 in (Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT):
                        ban_co_nhap_2, merge_score_2, changed = move_board(ban_co_nhap_1, move_2)
                        if changed:
                            co_nuoc_di_2 = True
                            diem_nhap_2 = self.evaluate(ban_co_nhap_2, merge_score_1 + merge_score_2)
                            if diem_nhap_2 > score2:
                                score2 = diem_nhap_2
                    if not co_nuoc_di_2:
                        score2 = self.evaluate(ban_co_nhap_1, merge_score_1)

                    # --- TRƯỜNG HỢP SINH SỐ 4 ---
                    ban_co_nhap_1[r, c] = 4
                    score4 = float("-inf")
                    co_nuoc_di_4 = False
                    for move_2 in (Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT):
                        ban_co_nhap_2, merge_score_2, changed = move_board(ban_co_nhap_1, move_2)
                        if changed:
                            co_nuoc_di_4 = True
                            diem_nhap_2 = self.evaluate(ban_co_nhap_2, merge_score_1 + merge_score_2)
                            if diem_nhap_2 > score4:
                                score4 = diem_nhap_2
                    if not co_nuoc_di_4:
                        score4 = self.evaluate(ban_co_nhap_1, merge_score_1)

                    # Trả lại ô trống về 0 sau khi nháp xong ô (r, c)
                    ban_co_nhap_1[r, c] = 0

                    # 6. Tính kỳ vọng theo xác suất 0.9 (số 2) và 0.1 (số 4)
                    diem_1_o_trong = 0.9 * score2 + 0.1 * score4
                    tong_diem_k_o += diem_1_o_trong

                # 7. Trung bình cộng qua k ô trống
                gia_tri_cua_move = tong_diem_k_o / k

            # 8. So sánh lấy nước đi có giá trị cao nhất
            if gia_tri_cua_move > best_value:
                best_value = gia_tri_cua_move
                best_move = move

        return best_move