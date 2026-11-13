"""Điểm bắt đầu của bài nộp — sinh viên chỉ cần sửa file này.

Baseline bên dưới nhìn trước đúng một nước. Nó minh họa API và cách mô phỏng
nước đi, nhưng cố ý chưa xử lý ô ngẫu nhiên và chưa phải một thuật toán mạnh.
"""

from __future__ import annotations

import numpy as np

from game2048.observation import Observation
from game2048.rules import move_board
from game2048.types import Move


SNAKE_WEIGHTS = np.array([
        [2**0,  2**1,  2**2,  2**3],
        [2**7,  2**6,  2**5,  2**4],
        [2**8,  2**9,  2**10, 2**11],
        [2**15, 2**14, 2**13, 2**12]
    ], dtype=float)

class Agent:
    # Đổi tên này thành tên đội; nó sẽ xuất hiện trong UI và file kết quả.
    name = "AI3_Group_03"

    def reset(self, seed: int | None = None) -> None:
        """Xóa cache/trạng thái giữa hai ván nếu thuật toán của bạn có dùng."""

    
    @staticmethod
    def evaluate(board: np.ndarray, merge_score: int) -> float:
        # 1. Giữ nguyên nền tảng hàm mẫu của giảng viên
        empty_cells = int(np.count_nonzero(board == 0))
        
        # 2. Nhân TRỰC TIẾP bàn cờ với ma trận 2^15..2^0 (Tuyệt đối KHÔNG dùng log2)
        snake_score = float(np.sum(board * SNAKE_WEIGHTS))
        
        # Kết hợp: Điểm con rắn + Thưởng ô trống + Điểm gộp
        return snake_score + 1000.0 * empty_cells + merge_score * 10.0
    
    
        
    '''
    def choose_move(self, obs: Observation, time_limit_ms: float) -> Move:
        """Trả về đúng một phần tử ``Move`` có trong ``obs.legal_moves``.

        Khi chấm theo tổng thời gian, ``time_limit_ms`` và
        ``obs.time_remaining_ms`` là ngân sách còn lại của cả ván — không phải
        lời hứa rằng mỗi nước được phép dùng hết số đó.
        """
        if not obs.legal_moves:
            raise ValueError("choose_move được gọi ở trạng thái kết thúc")

        best_move = obs.legal_moves[0]
        best_value = float("-inf")
        for move in obs.legal_moves:
            next_board, merge_score, _changed = move_board(obs.board, move)
            value = self.evaluate(next_board, merge_score)
            if value > best_value:
                best_value, best_move = value, move
        return best_move
        '''
    def choose_move(self, obs: Observation, time_limit_ms: float) -> Move:
        if not obs.legal_moves:
            raise ValueError("choose_move được gọi ở trạng thái kết thúc")

        best_move = obs.legal_moves[0]
        best_value = float("-inf")

        # 1. "Vòng lặp chọn lần lượt một move trong legal_moves:"
        for move in obs.legal_moves:
            
            # 2. "Nháp : trạng thái bàn cờ tiếp theo , đưa xuống bot_turn"
            ban_co_nhap_1, merge_score_1, _ = move_board(obs.board, move)

            # 3. "Tầng trung gian : có k ô trống thì lần lượt xét các ô trống"
            cac_o_trong = np.argwhere(ban_co_nhap_1 == 0) # Tìm tọa độ các ô có số 0
            k = len(cac_o_trong)
            
            # Nếu không còn ô trống nào (k == 0), chấm điểm bàn cờ nháp 1 luôn
            if k == 0:
                gia_tri_cua_move = self.evaluate(ban_co_nhap_1, merge_score_1)
            else:
                tong_diem_k_o = 0.0 # Giỏ gom điểm của tầng trung gian

                for r, c in cac_o_trong:
                    # 4. "Bot_turn : lấy bàn cờ nháp và sinh số 2 hoặc 4 vào ô trống"
                    
                   
                    ban_co_nhap_1[r, c] = 2
                    
                    # 5. "My-turn : vòng lặp các hướng của bàn cờ nháp -> sinh bàn cờ nháp 2"
                    # "tính evaluate() của bàn cờ nháp 2, so sánh lấy max, đưa lên tầng 2"
                    score2 = float("-inf")
                    co_nuoc_di_2 = False
                    for move_2 in (Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT):
                        ban_co_nhap_2, merge_score_2, changed = move_board(ban_co_nhap_1, move_2)
                        if changed: # changed == True nghĩa là move_2 hợp lệ!
                            co_nuoc_di_2 = True
                            diem_nhap_2 = self.evaluate(ban_co_nhap_2,merge_score_1 + merge_score_2)
                            if diem_nhap_2 > score2:
                                score2 = diem_nhap_2
                    if not co_nuoc_di_2: # Nếu kẹt cả 4 hướng, lấy điểm bàn cờ hiện tại
                        score2 = self.evaluate(ban_co_nhap_1, 0)

                    # --- TRƯỜNG HỢP SINH SỐ 4 (Làm y hệt số 2) ---
                    ban_co_nhap_1[r, c] = 4
                    
                    score4 = float("-inf")
                    co_nuoc_di_4 = False
                    for move_2 in (Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT):
                        ban_co_nhap_2, merge_score_2, changed = move_board(ban_co_nhap_1, move_2)
                        if changed:
                            co_nuoc_di_4 = True
                            diem_nhap_2 = self.evaluate(ban_co_nhap_2,merge_score_1 + merge_score_2)
                            if diem_nhap_2 > score4:
                                score4 = diem_nhap_2
                    if not co_nuoc_di_4:
                        score4 = self.evaluate(ban_co_nhap_1, 0)

                    # Trả lại ô trống về 0 sau khi nháp xong ô (r, c) này
                    ban_co_nhap_1[r, c] = 0

                    # 6. "Tầng 2 lấy điểm của 2 và 4, tính điểm trường hợp ô trống đó"
                    # (Sửa 2*score2 + 4*score4 thành xác suất 0.9*score2 + 0.1*score4)
                    diem_1_o_trong = 0.9 * score2 + 0.1 * score4
                    
                    # Đưa lên tầng trung gian (cộng dồn vào giỏ)
                    tong_diem_k_o += diem_1_o_trong

                # 7. "Tầng trung gian gom hết điểm lại rồi chia cho k ô trống, đưa lên làm giá trị của move"
                gia_tri_cua_move = tong_diem_k_o / k

            # 8. "Cuối cùng so sánh các giá trị lấy best_value , trả về move cần tìm"
            if gia_tri_cua_move > best_value:
                best_value = gia_tri_cua_move
                best_move = move

        return best_move