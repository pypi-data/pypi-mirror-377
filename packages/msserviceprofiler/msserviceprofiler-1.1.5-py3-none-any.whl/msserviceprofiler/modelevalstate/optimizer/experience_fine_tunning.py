# -*- coding: utf-8 -*-
# Copyright (c) 2025-2025 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from itertools import cycle
from typing import Optional, Tuple

import numpy as np

from msserviceprofiler.modelevalstate.config.config import default_support_field, PerformanceIndex, \
    map_param_with_value


class StopFineTune(Exception):
    pass


class MindIeFineTune:
    def __init__(self, ttft_penalty: float = 0, tpot_penalty: float = 0, target_field: Optional[Tuple] = None,
                 ttft_slo: float = 0.5, tpot_slo: float = 0.05, slo_coefficient: float = 0.1, step_size: float = 0.5):
        self.ttft_penalty = ttft_penalty  # 优化算法中惩罚系数
        self.tpot_penalty = tpot_penalty
        self.ttft_slo = ttft_slo
        self.tpot_slo = tpot_slo
        self.slo_coefficient = slo_coefficient
        self.target_field = target_field if target_field else default_support_field
        self.fine_tune_target = ["REQUESTRATE"]
        self.fine_tune_type = cycle(self.fine_tune_target)
        self.step_size = step_size
        self.ttft_lower_bound = self.ttft_slo * (1 - self.slo_coefficient)
        self.ttft_upper_bound = self.ttft_slo * (1 + self.slo_coefficient)
        self.tpot_lower_bound = self.tpot_slo * (1 - self.slo_coefficient)
        self.tpot_upper_bound = self.tpot_slo * (1 + self.slo_coefficient)
        if self.ttft_penalty == 0 and self.tpot_penalty == 0:
            raise StopFineTune("No penalties, no need to fine-tune.")
        ttft_flag = self.ttft_penalty != 0 and self.ttft_slo == 0
        tpot_flag = self.tpot_penalty != 0 and self.tpot_slo == 0
        if ttft_flag or tpot_flag:
            raise ValueError("Penalty is set but SLO is zero.")

    @staticmethod
    def update_request_rate(simulate_run_info, signed_factor) -> bool:
        if signed_factor == 0:
            return False
        for _field in simulate_run_info:
            if _field.name.upper().strip() == "REQUESTRATE":
                if _field.min == _field.max:
                    return False
                original_value = _field.value
                _field.value *= (1 + signed_factor)
                _field.value = max(_field.min, min(_field.max, _field.value))
                # 检查值是否发生了有影响的变化(>=0.1)
                return abs(_field.value - original_value) >= 0.1
        return False

    def mindie_fine_tune_with_cycle(self, params: np.ndarray, performance_index: PerformanceIndex):
        # 对mindie 参数进行微调
        if performance_index.time_per_output_token is None:
            raise ValueError("Missing performance data for TPOT.")
        if self.ttft_penalty != 0 and performance_index.time_to_first_token is None:
            raise ValueError("Missing performance data for TTFT.")

        actual_tpot = performance_index.time_per_output_token
        actual_ttft = performance_index.time_to_first_token

        ttft_over_slo = False
        ttft_under_lower_bound = False
        tpot_over_slo = actual_tpot > self.tpot_upper_bound
        tpot_under_lower_bound = actual_tpot < self.tpot_lower_bound

        # 同时约束ttft
        if self.ttft_penalty != 0:
            ttft_over_slo = actual_ttft > self.ttft_upper_bound
            ttft_under_lower_bound = actual_ttft < self.ttft_lower_bound

        # 主流程 初始化保证self.tpoy_slo 和 self.ttft_slo不为0
        if ttft_over_slo or tpot_over_slo:
            tpot_diff = (actual_tpot - self.tpot_slo) / self.tpot_slo
            ttft_diff = (actual_ttft - self.ttft_slo) / self.ttft_slo
            worst_diff = max(tpot_diff, ttft_diff)
            signed_factor = -worst_diff * self.step_size
        elif (self.ttft_penalty == 0 or ttft_under_lower_bound) and tpot_under_lower_bound:
            tpot_diff = (self.tpot_slo - actual_tpot) / self.tpot_slo
            ttft_diff = (self.ttft_slo - actual_ttft) / self.ttft_slo if self.ttft_penalty != 0 else float('inf')
            # 选择离SLO更近的提升空间
            best_diff = min(tpot_diff, ttft_diff)
            signed_factor = best_diff * self.step_size
        else:
            raise StopFineTune("No need to fine-tune.")
        simulate_run_info = map_param_with_value(params, self.target_field)
        was_updated = self.update_request_rate(simulate_run_info, signed_factor)
        if not was_updated:
            raise StopFineTune("Parameter value reached its boundary or did not change.")

        return simulate_run_info