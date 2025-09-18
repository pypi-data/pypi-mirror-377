# ---------------------------------------------------------------------
# Copyright (c) 2025 Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------


from __future__ import annotations

import warnings

from qai_hub_models.models._shared.llm.export import export_model
from qai_hub_models.models._shared.llm.model import determine_precision_from_checkpoint
from qai_hub_models.models.common import Precision, TargetRuntime
from qai_hub_models.models.falcon_v3_7b_instruct import (
    MODEL_ID,
    FP_Model,
    Model,
    PositionProcessor,
)
from qai_hub_models.models.falcon_v3_7b_instruct.model import (
    DEFAULT_PRECISION,
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
        supported_precision_runtimes={
            Precision.w4a16: [
                TargetRuntime.GENIE,
                TargetRuntime.ONNXRUNTIME_GENAI,
            ],
        },
        default_export_device=DEFAULT_EXPORT_DEVICE,
        uses_link_job=True,
    )
    parser.add_argument(
        "--synchronous",
        action="store_true",
        help="Wait for each command to finish before submitting new.",
    )
    parser = enable_model_caching(parser)
    parser.set_defaults(
        _skip_quantsim_creation=True,
        precision=DEFAULT_PRECISION,
        target_runtime=TargetRuntime.GENIE,
    )
    args = parser.parse_args()
    additional_model_kwargs = vars(args)
    if not args.skip_inferencing:
        additional_model_kwargs["_skip_quantsim_creation"] = False
    fp_model_params = dict(
        sequence_length=additional_model_kwargs["sequence_length"],
        context_length=additional_model_kwargs["context_length"],
    )
    if isinstance(
        additional_model_kwargs["checkpoint"], str
    ) and additional_model_kwargs["checkpoint"].startswith("DEFAULT"):
        additional_model_kwargs["fp_model"] = FP_Model.from_pretrained(  # type: ignore[index]
            **fp_model_params
        )
        additional_model_kwargs["precision"] = (
            determine_precision_from_checkpoint(additional_model_kwargs["checkpoint"])
            or DEFAULT_PRECISION
        )
    export_model(
        model_cls=Model,
        position_processor_cls=PositionProcessor,
        model_name=MODEL_ID,
        model_asset_version=MODEL_ASSET_VERSION,
        num_splits=NUM_SPLITS,
        num_layers_per_split=NUM_LAYERS_PER_SPLIT,
        **additional_model_kwargs,
    )


if __name__ == "__main__":
    main()
