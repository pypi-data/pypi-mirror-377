# ---------------------------------------------------------------------
# Copyright (c) 2025 Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------


from __future__ import annotations

import warnings

from qai_hub_models.models._shared.llm.export import export_model
from qai_hub_models.models.common import Precision, TargetRuntime
from qai_hub_models.models.qwen2_5_7b_instruct import MODEL_ID, Model
from qai_hub_models.models.qwen2_5_7b_instruct.model import (
    MODEL_ASSET_VERSION,
    NUM_LAYERS_PER_SPLIT,
    NUM_SPLITS,
)
from qai_hub_models.utils.args import enable_model_caching, export_parser

DEFAULT_EXPORT_DEVICE = "Snapdragon 8 Elite QRD"


def main():
    warnings.filterwarnings("ignore")
    parser = export_parser(
        model_cls=Model,
        supported_precision_runtimes={Precision.w8a16: [TargetRuntime.GENIE]},
        default_export_device=DEFAULT_EXPORT_DEVICE,
        uses_link_job=True,
    )
    parser.add_argument(
        "--synchronous",
        action="store_true",
        help="Wait for each command to finish before submitting new.",
    )
    parser = enable_model_caching(parser)
    args = parser.parse_args()
    export_model(
        model_cls=Model,
        model_name=MODEL_ID,
        model_asset_version=MODEL_ASSET_VERSION,
        num_splits=NUM_SPLITS,
        num_layers_per_split=NUM_LAYERS_PER_SPLIT,
        **vars(args),
    )


if __name__ == "__main__":
    main()
