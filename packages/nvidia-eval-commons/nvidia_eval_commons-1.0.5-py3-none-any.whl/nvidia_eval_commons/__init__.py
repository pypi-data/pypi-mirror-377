# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
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

from nvidia_eval_commons.api import evaluate, show_available_tasks
from nvidia_eval_commons.api.api_dataclasses import (
    ApiEndpoint,
    ConfigParams,
    EndpointType,
    Evaluation,
    EvaluationConfig,
    EvaluationResult,
    EvaluationTarget,
    GroupResult,
    MetricResult,
    Score,
    ScoreStats,
    TaskResult,
)
from nvidia_eval_commons.api.run import run_eval

__all__ = [
    "ApiEndpoint",
    "ConfigParams",
    "EndpointType",
    "Evaluation",
    "EvaluationConfig",
    "EvaluationResult",
    "EvaluationTarget",
    "GroupResult",
    "MetricResult",
    "Score",
    "ScoreStats",
    "TaskResult",
    "run_eval",
    "evaluate",
    "show_available_tasks",
]

# Import logging to ensure centralized logging is configured
from nvidia_eval_commons import logging  # noqa: F401
