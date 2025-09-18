# -------------------------------------------------------------------------------
# (c) Copyright 2023 Sony Semiconductor Israel, Ltd. All rights reserved.
#
#      This software, in source or object form (the "Software"), is the
#      property of Sony Semiconductor Israel Ltd. (the "Company") and/or its
#      licensors, which have all right, title and interest therein, You
#      may use the Software only in accordance with the terms of written
#      license agreement between you and the Company (the "License").
#      Except as expressly stated in the License, the Company grants no
#      licenses by implication, estoppel, or otherwise. If you are not
#      aware of or do not agree to the License terms, you may not use,
#      copy or modify the Software. You may use the source code of the
#      Software only for your internal purposes and may not distribute the
#      source code of the Software, any part thereof, or any derivative work
#      thereof, to any third party, except pursuant to the Company's prior
#      written consent.
#      The Software is the confidential information of the Company.
# -------------------------------------------------------------------------------
import os
from dataclasses import fields

from uni_model import UniModelGenerator, UniModelToGraphDefConverter, ValidationCfg, Layout, Semantic
from uni_model import UniModelFileNameAssistant
from uni_model.converter.const_saving_method import ConstSavingMethod
from uni_model.validation.validation_cfg import ValidationCfgForViolations

from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_edge import NnirEdge    # noqa: F401
from uni.common.core.nnir_graph.nnir_nodes import NnirNode    # noqa: F401
from uni.common.core.nnir_graph.semantics import TensorSemantics, AxisSemantics
from uni.common.util.dev import is_dev, is_strict_validation
from uni.common.logger import get_logger

logger = get_logger(__name__)


class UniModelExporter:

    @classmethod
    def export(cls, graph_id: str, component_name: str, g: NnirGraph, out_dir, metadata) -> None:
        os.makedirs(out_dir, exist_ok=True)
        validation_cfg = cls.get_validation_cfg()
        model = UniModelGenerator.generate_model(validation_cfg=validation_cfg)
        # this is a feature request to log metadata to debug logger
        logger.debug(f"model metadata: {metadata}")
        UniModelGenerator.generate_graph_in_model(model, graph_id, graph_id, ordinal=0, metadata=metadata)
        nodes = {}
        for node in g.get_nodes(data=True):    # type: NnirNode
            uni_node = node.export_uni_model()
            nodes[node.name] = uni_node
            UniModelGenerator.add_layer_to_graph_in_model(model, graph_id, uni_node)
        for edge in g.get_edges():    # type: NnirEdge
            # convert edge.src_index and edge.dest_index to int for case they are IntEnum
            UniModelGenerator.add_edge(model,
                                       graph_id,
                                       nodes[edge.src],
                                       nodes[edge.dest],
                                       from_index=int(edge.src_index),
                                       to_index=int(edge.dest_index))
        model = model.build()
        generate_path = UniModelFileNameAssistant.generate_uni_model_path
        uni_model_path = generate_path(out_dir, graph_id, component_name, txt_format=False)
        UniModelToGraphDefConverter.convert(model,
                                            uni_model_path,
                                            const_saving_method=ConstSavingMethod.IN_MODEL_FILE,
                                            skip_compaction=True)
        logger.info(f'Wrote outputs to {uni_model_path.to_absolute_file_name()}')
        if is_dev():
            uni_model_path = generate_path(out_dir, graph_id, component_name, txt_format=True)
            UniModelToGraphDefConverter.convert(model, uni_model_path)
            logger.info(f'Wrote outputs to {uni_model_path.to_absolute_file_name()}')

    @staticmethod
    def get_validation_cfg() -> ValidationCfg:
        # validation_cfg is the validation tool configuration of uni_model
        # ValidationCfg() is checking the default configuration
        if is_strict_validation():
            validation_for_violation = ValidationCfgForViolations()
            for field in fields(validation_for_violation):
                if isinstance(getattr(validation_for_violation, field.name), bool):
                    setattr(validation_for_violation, field.name, True)
            validation_cfg = ValidationCfg(throw_errors_as_expected=True,
                                           validation_for_violation=validation_for_violation)
        else:
            validation_cfg = ValidationCfg()
        return validation_cfg

    @staticmethod
    def get_uni_semantic(axis_semantics: AxisSemantics) -> Semantic:
        axis_map = {
            AxisSemantics.BATCH: Semantic.B,
            AxisSemantics.HEIGHT: Semantic.H,
            AxisSemantics.WIDTH: Semantic.W,
            AxisSemantics.CHANNELS: Semantic.C,
            AxisSemantics.IN_CHANNELS: Semantic.CI,
            AxisSemantics.OUT_CHANNELS: Semantic.CO,
            AxisSemantics.KERNEL_H: Semantic.KH,
            AxisSemantics.KERNEL_W: Semantic.KW,
        }
        if axis_semantics not in axis_map:
            raise NotImplementedError(f"The AxisSemantics: {axis_semantics} is not supported")
        return axis_map[axis_semantics]

    @classmethod
    def tensor_semantics_to_layout(cls, tensor_semantics: TensorSemantics) -> Layout:
        return Layout([cls.get_uni_semantic(axis) for axis in tensor_semantics])
