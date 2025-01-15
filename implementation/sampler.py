# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Class for sampling new programs."""
from __future__ import annotations
from abc import ABC, abstractmethod

from typing import Collection, Sequence, Type
import numpy as np
import time

from implementation import evaluator
from implementation import programs_database


class LLM(ABC):
    """Language model that predicts continuation of provided source code.
    """

    def __init__(self, samples_per_prompt: int) -> None:
        self._samples_per_prompt = samples_per_prompt

    def _draw_sample(self, prompt: str) -> str:
        """Returns a predicted continuation of `prompt`."""
        raise NotImplementedError('Must provide a language model.')

    @abstractmethod
    def draw_samples(self, prompt: str,count_list) -> Collection[str]:
        """Returns multiple predicted continuations of `prompt`."""
        return [self._draw_sample(prompt) for _ in range(self._samples_per_prompt)]


class Sampler:
    """Node that samples program continuations and sends them for analysis.
    """
    _global_samples_nums: int = 1  # RZ: this variable records the global sample nums

    def __init__(
            self,
            # database: programs_database.ProgramsDatabase,
            databases: list[programs_database.ProgramsDatabase],
            # evaluators: Sequence[evaluator.Evaluator],
            evaluators_list: list[Sequence[evaluator.Evaluator]],
            samples_per_prompt: int,
            max_sample_nums: int | None = None,
            llm_class: Type[LLM] = LLM,
            functions_num: int = 0
    ):
        self._samples_per_prompt = samples_per_prompt
        # self._database = database
        # self._evaluators = evaluators
        self._databases = databases
        self._evaluators_list = evaluators_list
        self._llm = llm_class(samples_per_prompt)
        self._max_sample_nums = max_sample_nums
        self._functions_num = functions_num
        self._database_index = 0
        self._evaluator_index = 0
        self._switch_counter = 0

    # def sample(self, count_list,score_list, **kwargs):
    #     """Continuously gets prompts, samples programs, sends them for analysis.
    #     """
    #     while True:
    #         # stop the search process if hit global max sample nums
    #         if self._max_sample_nums and self.__class__._global_samples_nums >= self._max_sample_nums:
    #             break
            
    #         prompt = self._database.get_prompt()
    #         reset_time = time.time()
            
    #         samples = self._llm.draw_samples(prompt.code, count_list)
            
    #         sample_time = (time.time() - reset_time) / self._samples_per_prompt
    #         new_code = ""
    #         for sample in samples:
    #             new_code += sample
    #         self._global_sample_nums_plus_one()  # RZ: add _global_sample_nums
    #         cur_global_sample_nums = self._get_global_sample_nums()
    #         chosen_evaluator: evaluator.Evaluator = np.random.choice(self._evaluators)
            
    #         chosen_evaluator.analyse(
    #             new_code,
    #             prompt.island_id,
    #             prompt.version_generated,
    #             **kwargs,
    #             global_sample_nums=cur_global_sample_nums,
    #             sample_time=sample_time,
    #             score_list_score=score_list.score,
    #             exec_size=score_list.parallel_size,
    #             score_list=score_list,

    #         )

    def sample(self, count_list, score_list, **kwargs):
        """Continuously gets prompts, samples programs, sends them for analysis."""
        while True:
            # Stop the search process if hit global max sample nums
            if self._max_sample_nums and self._get_global_sample_nums() >= self._max_sample_nums:
                break

            # Switch database and evaluator every 3 samples
            if self._switch_counter % 3 == 0:
                self._database_index = (self._database_index + 1) % len(self._databases)
                self._evaluator_index = (self._evaluator_index + 1) % len(self._evaluators_list)
            
            self._switch_counter += 1
            
            current_database = self._databases[self._database_index]
            current_evaluators = self._evaluators_list[self._evaluator_index]
            chosen_evaluator = np.random.choice(current_evaluators)

            # NOTE: multifunc需要改这条路get_prompt->_generate_prompt->_generate_prompt
            prompt = current_database.get_prompt()
            reset_time = time.time()
            samples = self._llm.draw_samples(prompt.code, count_list,self._database_index)
            sample_time = (time.time() - reset_time) / self._samples_per_prompt
            new_code = "".join(samples)
            self._global_sample_nums_plus_one()
            cur_global_sample_nums = self._get_global_sample_nums()
            chosen_evaluator.analyse(
                new_code,
                prompt.island_id,
                prompt.version_generated,
                **kwargs,
                global_sample_nums=cur_global_sample_nums,
                sample_time=sample_time,
                score_list_score=score_list.score,
                # exec_size=score_list.parallel_size,
                score_list=score_list,
                current_index=self._database_index
            )

    def _get_global_sample_nums(self) -> int:
        return self.__class__._global_samples_nums

    def set_global_sample_nums(self, num):
        self.__class__._global_samples_nums = num

    def _global_sample_nums_plus_one(self):
        self.__class__._global_samples_nums += 1
