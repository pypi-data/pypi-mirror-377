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
import argparse
from collections import defaultdict
from typing import Dict, List, Union, Tuple, Set, Optional
import copy

import numpy as np
import onnx
import mct_quantizers as mctq
from onnx import onnx_ml_pb2
import onnxruntime as ort

from uni.common.core.connectivity_map import ConnectivityMap
from uni.common.core.multigraph.edge import Edge
from uni.common.core.multigraph.graph import MultiDiGraph
from uni.common.logger import get_logger, MessageCodes
from uni.common.parsers.base_reader import MetaOpType
from uni.pytorch.onnx_parser.onnx_mct_reader_helper import MCT_QUANTIZERS_DOMAIN, OnnxMctQWeightsQuantizer
from uni.pytorch.onnx_parser.onnx_reader import OnnxReader
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode, OnnxOpType

logger = get_logger(__name__)


class OnnxSimplifierException(Exception):
    pass


class OnnxSimplifier:
    """
    Simplify ONNX model by constant folding

    onnx_nodel is the important graph add remove in it
    meta_graph is only for eazy calculation and is reflecting the onnx graph

    Partial description of onnx model:
    onnx_model: onnx.ModelProto
    onnx_model.graph: onnx.onnx_ml_pb2.GraphProto
    onnx_model.graph.node: onnx.onnx_ml_pb2.NodeProto - properties: name op_type input output
    onnx_model.graph.node.input - "list" of inputs str
    onnx_model.graph.node.output - "list" of outputs str
    onnx_model.graph.initializer: onnx.onnx_ml_pb2.TensorProto
    onnx_model.graph.value_info - "list" of onnx.onnx_ml_pb2.ValueInfoProto
    """
    start_pattern_ops = [OnnxOpType.Shape, OnnxOpType.Constant, OnnxOpType.Range]

    def __init__(self, model_path):
        self.model_path = model_path
        self.onnx_model, self.meta_graph, self.tensors = self._build_meta_graph(self.model_path)
        self.deleted_ops: Dict[str, List[str]] = defaultdict(list)

    def simplify(self):
        self._constant_folding()
        self.rebuild_onnx_model()
        self._remove_transpose_after_mctq_const()
        self.rebuild_onnx_model()
        self._mct_infer()
        self.rebuild_onnx_model()
        self.shape_inference()
        self.rebuild_onnx_model()
        return self.onnx_model

    def rebuild_onnx_model(self):
        onnx.checker.check_model(self.onnx_model, full_check=True)
        self.onnx_model, self.meta_graph, self.tensors = self._build_meta_graph(self.onnx_model)

    def shape_inference(self):
        # fix a problem that onnx shape_inference.infer_shapes not infer shapes for nodes (mct_quantizers for example)
        onnx_nodes = []
        for node in self.onnx_model.graph.node:
            for tensor_id in node.output:
                shape = self.tensors[tensor_id].shape
                if shape is None or None in shape:
                    onnx_nodes.append(node)
                    break

        inferred_vals = self._ort_infer_vals(onnx_nodes)
        inferred_shapes = {k: [v.shape for v in vls] for k, vls in inferred_vals.items()}
        node_output_dict = {
            n.name: [o for o in n.output if o]
            for n in self.onnx_model.graph.node if n.name in inferred_shapes
        }
        value_info = []
        graph_output = {}
        elem_type = {
            n.name: n.type.tensor_type.elem_type
            for n in list(self.onnx_model.graph.value_info) + list(self.onnx_model.graph.output)
        }
        ignore_vals = []
        graph_output_names = [v.name for v in self.onnx_model.graph.output]
        for node_name, shapes in inferred_shapes.items():
            for out_name, shape, in zip(node_output_dict[node_name], shapes):
                org_shape = self.tensors[out_name].shape
                if len(shape) != len(org_shape):
                    ignore_vals.append(out_name)
                    logger.warning(f"val info: {out_name} org shape: {org_shape} vs onnxruntime shape: {shape}",
                                   message_code=MessageCodes.INVALID_MODEL)
                    continue
                tensor_value_info = onnx.helper.make_tensor_value_info(out_name, elem_type[out_name], shape)
                if out_name in graph_output_names:
                    graph_output[tensor_value_info.name] = tensor_value_info
                else:
                    value_info.append(tensor_value_info)

        all_out_names = {v for vls in node_output_dict.values() for v in vls if v not in ignore_vals}
        to_remove_value_info = [v for v in self.onnx_model.graph.value_info if v.name in all_out_names]
        for v in to_remove_value_info:
            self.onnx_model.graph.value_info.remove(v)
        self.onnx_model.graph.value_info.extend(value_info)
        to_remove_value_info = [v for v in self.onnx_model.graph.output if v.name in all_out_names]
        for v in to_remove_value_info:
            idx = list(self.onnx_model.graph.output).index(v)
            self.onnx_model.graph.output.remove(v)
            self.onnx_model.graph.output.insert(idx, graph_output[v.name])

    def _mct_infer(self):
        nodes: List[OnnxMetaNode] = list(self.meta_graph.topological_sort(data=True))
        mct_quant_nodes = [node for node in nodes if node.op_type in set(OnnxMctQWeightsQuantizer)]
        quant_out_vals = self._infer_vals(mct_quant_nodes)
        quant_const_map = {}
        for q_node in mct_quant_nodes:
            in_nodes: List[OnnxMetaNode] = self.meta_graph.get_ordered_in_nodes(q_node, data=True)
            assert in_nodes[0].op_type == OnnxOpType.Constant
            quant_const_map[q_node.name] = in_nodes[0]

        constant_to_add = []
        nodes_to_delete = {}
        new_edges: List[Edge] = []
        for quant_name, const_node in quant_const_map.items():
            const_outputs = self.meta_graph.get_out_nodes(const_node, by_output=False, data=False)
            data = quant_out_vals[quant_name][0]
            new_node_name = f"{const_node.name}_{const_outputs.index(quant_name)}"
            new_node = self._create_onnx_constant(new_node_name, data, [f"{new_node_name}_out"])
            constant_to_add.append(new_node)
            new_edges.append(Edge(new_node_name, quant_name, 0, 0))
            if all(n in quant_const_map for n in const_outputs):
                nodes_to_delete[const_node.name] = const_node

        self._apply_on_onnx(nodes_to_delete, constant_to_add, new_edges)

    def get_deleted_ops_count(self) -> Dict[str, int]:
        """ Deleted nodes count per op """
        return {k: len(v) for k, v in self.deleted_ops.items()}

    def get_deleted_nodes_count(self) -> int:
        """ Total deleted nodes count """
        return sum([len(v) for v in self.deleted_ops.values()])

    @staticmethod
    def _build_meta_graph(fw_model: Union[str, onnx.ModelProto]) -> \
            Tuple[onnx.ModelProto, MultiDiGraph, ConnectivityMap]:
        reader = OnnxReader(fw_model)
        meta_graph = reader.build_meta_graph()
        return reader.model, meta_graph, reader.tensors

    def _constant_folding(self):
        """ Find static sections of the graph beginning with one of the ops defined in start_pattern_ops,
         and fold them into constant """
        nodes_to_delete = self._find_nodes_to_fold()
        constant_to_add = self._obtain_folded_constants_to_add(nodes_to_delete)
        self._update_consts_to_delete(nodes_to_delete)
        self._apply_on_onnx(nodes_to_delete, constant_to_add)

    def _remove_transpose_after_mctq_const(self):
        nodes_to_delete, new_consts, nodes_to_update_map = self._find_nodes_transpose_after_mctq_const()
        self._apply_on_onnx(nodes_to_delete=nodes_to_delete,
                            constant_to_add=new_consts,
                            update_nodes_inputs_map=nodes_to_update_map)

    def _get_real_topological_sort_meta_nodes(self):
        nodes: List[OnnxMetaNode] = list(self.meta_graph.topological_sort(data=True))
        nodes = [n for n in nodes if n.op_type not in list(MetaOpType)]
        return nodes

    def _find_nodes_to_fold(self) -> Dict[str, OnnxMetaNode]:
        """ find nodes that can be folded into/replaced by consts """
        nodes = self._get_real_topological_sort_meta_nodes()
        nodes_to_delete = {}
        for node in nodes:
            if node.domain == MCT_QUANTIZERS_DOMAIN:
                continue
            if node.op_type in self.start_pattern_ops:
                if not node.is_const(check_quant=False):
                    nodes_to_delete[node.name] = node
            else:
                in_nodes: List[OnnxMetaNode] = self.meta_graph.get_ordered_in_nodes(node, data=True)
                needed_nodes = any(n for n in in_nodes
                                   if n.op_type not in self.start_pattern_ops and n.name not in nodes_to_delete)
                if not needed_nodes:
                    nodes_to_delete[node.name] = node
        return nodes_to_delete

    def _find_nodes_transpose_after_mctq_const(self):
        """
            weight:Initializer (const) -> :0
            threshold:Constant (const) -> :1
                Weight{type}Quantizer: mct_quantizers -> :0
                    Transpose -> :0
            remove the Transpose by transposing the weight
        """

        def get_onnx_node(meta_node: OnnxMetaNode):
            return [n for n in self.onnx_model.graph.node if n.name == meta_node.original_name][0]

        def update_channel_axis(quant_onnx_node, axes):
            if quant_node.get_attr("per_channel") == 1:
                old_channel_axis = quant_node.get_attr("channel_axis")
                new_channel_axis = axes.index(old_channel_axis)
                channel_axis_attr = [attr for attr in quant_onnx_node.attribute if attr.name == "channel_axis"][0]
                channel_axis_attr.i = new_channel_axis

        nodes = self._get_real_topological_sort_meta_nodes()
        nodes_to_delete = {}
        new_consts = []
        nodes_to_update_map = {}
        for quant_node in nodes:
            if quant_node.op_type not in list(OnnxMctQWeightsQuantizer):
                continue
            out_nodes: List[OnnxMetaNode] = self.meta_graph.get_out_nodes(quant_node, data=True, by_output=False)
            transpose_nodes = [n for n in out_nodes if n.op_type in ["Transpose"]]
            if not transpose_nodes or len(out_nodes) != len(transpose_nodes) or any(
                    not t_node.is_dup_of(transpose_nodes[0]) for t_node in transpose_nodes):
                continue

            # else, all transpose nodes are duplicates, using the first and removing all after computation:
            transpose_node = transpose_nodes[0]
            axes = transpose_node.attr["perm"]
            onnx_quant_node = get_onnx_node(quant_node)
            update_channel_axis(onnx_quant_node, axes)
            onnx_quant_node.output[0] = transpose_node.output[0]

            # remove duplicated transpose nodes
            for t_node in transpose_nodes:
                out_node = self.meta_graph.get_out_nodes(t_node, data=True, by_output=False)[0]
                out_node_inputs = out_node.input
                input_indices = tuple(
                    [i for i in range(len(out_node_inputs)) if out_node_inputs[i] == t_node.output[0]])
                nodes_to_update_map[out_node.name] = (input_indices, onnx_quant_node.output[0])
                nodes_to_delete[t_node.name] = t_node

            # replacing old initializer with new const after applying transpose
            old_const_node: OnnxMetaNode = self.meta_graph.get_ordered_in_nodes(quant_node, data=True)[0]
            old_value = old_const_node.get_const_data()
            new_value = np.transpose(old_value, axes=axes)
            new_const_node = self._create_onnx_constant(f"{old_const_node.name}_transposed", new_value,
                                                        [quant_node.input[0]])
            new_consts.append(new_const_node)
            nodes_to_delete[old_const_node.name] = old_const_node

        return nodes_to_delete, new_consts, nodes_to_update_map

    def _get_list_obtain_folded_constants_to_add(self, nodes_to_delete: Dict[str, OnnxMetaNode]) -> List[OnnxMetaNode]:
        """
        get list of nodes that can replaced by constant
            for static sections of the graph that can be replaced
        """
        needs_infer_nodes = {}
        for name, node in nodes_to_delete.items():
            out_nodes = self.meta_graph.get_out_nodes(node, by_output=False, data=True)
            ok_nodes = [n for n in out_nodes if n.name not in nodes_to_delete]
            if ok_nodes:
                if name not in needs_infer_nodes:
                    needs_infer_nodes[name] = node
        return list(needs_infer_nodes.values())

    @staticmethod
    def _get_node_by_name(name, nodes: Union[List[OnnxMetaNode]]):
        return [n for n in nodes if n.name == name][0]

    def _obtain_folded_constants_to_add(self, nodes_to_delete: Dict[str, OnnxMetaNode]):
        """
        generate constants for static sections of the graph that can be replaced
        """
        needs_infer_nodes = self._get_list_obtain_folded_constants_to_add(nodes_to_delete)
        inferred_nodes = self._infer_vals(needs_infer_nodes)
        nodes = self._get_real_topological_sort_meta_nodes()
        constant_to_add = []
        for name, data_list in inferred_nodes.items():
            node = self._get_node_by_name(name, nodes)
            for data in data_list:
                onnx_node = self._create_onnx_constant(node.name, data, list(node.output))
                constant_to_add.append(onnx_node)
        return constant_to_add

    @staticmethod
    def _unique_nodes_by_name(nodes: List[OnnxMetaNode]) -> List[OnnxMetaNode]:
        # list is returned instead of set so that the node is not required to be hashable
        res = []
        names: Set[str] = set()
        for node in nodes:
            if node.name not in names:
                res.append(node)
                names.update(node.name)
        return res

    def _infer_vals(self, meta_nodes: List[OnnxMetaNode]) -> Dict[str, List[np.ndarray]]:
        """
         infer values for nodes in graph on random model input

        inputs:
            meta_nodes: list of node that don't effected by model input data
                because all nodes inputs are constants recursively (like in constant folding)
                MetaOpType nodes are not supported, because the node don't exist in model.graph.node
        output:
            dict with key as node name and value list of numpy arrays with value of the node

        example
            if model have
            op: constant name: c1 = np.array([1])
            op: constant name: c2 = np.array([2])
            op: add name: add_node = c1 + c3
            the result of _infer_vals([add_meta_node]) will be
                {'add_node': [np.array([3])]}
        """

        assert all([n.op_type not in list(MetaOpType) for n in meta_nodes]), "Can't infer val for MetaOpType"

        res = {}
        meta_nodes = self._unique_nodes_by_name(meta_nodes)
        meta_nodes_names = [n.name for n in meta_nodes]
        nodes = [
            n for n in self.onnx_model.graph.node if n.op_type != OnnxOpType.Constant and n.name in meta_nodes_names
        ]
        if nodes:
            res.update(self._ort_infer_vals(nodes))
        return res

    def _ort_infer_vals(self, onnx_nodes: List[onnx_ml_pb2.NodeProto]) -> Dict[str, List[np.ndarray]]:
        """
         infer values for nodes in graph on random model input

        inputs:
            onnx_nodes: list of node that don't effected by model input data
                because all nodes inputs are constants recursively (like in constant folding)
        output:
            dict with key as node name and value list of numpy arrays with value of the node

        example
            if model have
            op: constant name: c1 = np.array([1])
            op: constant name: c2 = np.array([2])
            op: add name: add_node = c1 + c3
            the result of _infer_vals([add_onnx_node]) will be
                {'add_node': [np.array([3])]}
        """

        def fix_dynamic_batch(shape: tuple):
            return (1, *shape[1:]) if shape[0] is None else shape

        def get_input_feed(model):
            r = {}
            for j in range(len(model.graph.input)):
                input_name = model.graph.input[j].name
                input_shape = self.tensors[input_name].shape
                if input_shape is None or len(input_shape) == 1:
                    raise ValueError(f"Invalid input {input_name} with shape {input_shape}")
                assert input_shape is not None
                input_shape = fix_dynamic_batch(input_shape)
                if None in input_shape:
                    raise ValueError(f"Model input most have static shape (except batch size) got {input_shape}")
                elem_type = model.graph.input[j].type.tensor_type.elem_type
                np_type = onnx.helper.tensor_dtype_to_np_dtype(elem_type)
                input_data = np.random.randn(*input_shape).astype(np_type)
                r[input_name] = input_data
            return r

        input_feed = get_input_feed(self.onnx_model)
        vals_info_to_node = {}
        shapes_model = copy.deepcopy(self.onnx_model)
        graph_value_info = {v.name: v for v in shapes_model.graph.value_info}
        output_value_info = {v.name for v in shapes_model.graph.output}
        for n in onnx_nodes:
            for i, v_name in enumerate(n.output):
                if v_name in graph_value_info:
                    shapes_model.graph.output.append(graph_value_info[v_name])
                    vals_info_to_node[v_name] = n.name
                elif v_name in output_value_info:
                    vals_info_to_node[v_name] = n.name
                elif not v_name:
                    shapes_model_node = [m for m in shapes_model.graph.node if m.name == n.name][0]
                    shapes_model_node.output[i] = f"{n.name}_out_{i}"
                else:
                    raise ValueError(f"Can't find value_info for {v_name}")

        vals_info_names = list(vals_info_to_node.keys())
        if not vals_info_names:
            return {}
        try:
            # https://github.com/microsoft/onnxruntime/issues/21571
            # https://github.com/microsoft/onnxruntime/issues/17061
            # when enable_mem_reuse is True some models can exit with sigkill that can't be caught by except
            sess_options = self._get_ort_session_options()
            sess_options.enable_mem_reuse = False
            sess = ort.InferenceSession(shapes_model.SerializeToString(), sess_options)
            model_res = sess.run(vals_info_names, input_feed)
        except Exception as e:
            raise self.onnx_runtime_exception_handler(e, input_feed)
        res: Dict[str, List[np.ndarray]] = defaultdict(list)
        for val_info, val in zip(vals_info_names, model_res):
            res[vals_info_to_node[val_info]].append(val)
        return res

    @staticmethod
    def _get_ort_session_options():
        # trigger ort registration (before setting up session options obj)
        from uni.pytorch.onnx_parser import custom_layer_ort    # noqa: F401
        # the is a single custom library in ort-extensions so session options set by mctq includes custom layers as well
        so = mctq.get_ort_session_options()
        return so

    def onnx_runtime_exception_handler(self, modified_model_error: Exception,
                                       input_feed: Dict[str, np.ndarray]) -> Exception:
        try:
            sess = ort.InferenceSession(self.model_path, self._get_ort_session_options())
            sess.run(None, input_feed)
        except Exception as org_model_error:
            logger.error("ONNX Runtime failed to run model", message_code=MessageCodes.EXECUTION)
            return org_model_error
        return OnnxSimplifierException(modified_model_error)

    def _update_consts_to_delete(self, nodes_to_delete: Dict[str, OnnxMetaNode]):
        nodes = [n for n in self.meta_graph.get_nodes(True) if n.is_const(check_quant=False)]
        for node in nodes:
            out_nodes = self.meta_graph.get_out_nodes(node, by_output=False, data=True)
            if any(n for n in out_nodes if n.name not in nodes_to_delete):
                continue
            nodes_to_delete[node.name] = node

    def _apply_on_onnx(self,
                       nodes_to_delete: dict,
                       constant_to_add: list,
                       new_edges: Optional[list] = None,
                       update_nodes_inputs_map: Optional[dict] = None):

        def get_new_onnx_nodes(to_delete, graph_nodes):
            org_names = {node.original_name: node for node in to_delete.values()}
            onnx_to_del = [(onnx_node, org_names[onnx_node.name]) for onnx_node in graph_nodes
                           if onnx_node.name in org_names]
            for onnx_node_, meta_node in onnx_to_del:
                self.deleted_ops[meta_node.op_type].append(meta_node.name)
            return [n for n in graph_nodes if n.name not in org_names]

        def update_edges(edges: List[Edge], graph_nodes):
            nodes = {n.name: n for n in graph_nodes}
            for e in edges:
                if e.dest in nodes:
                    nodes[e.dest].input[e.dest_index] = nodes[e.src].output[e.src_index]

        def update_nodes_inputs(graph_nodes):
            if update_nodes_inputs_map is not None:
                for node in graph_nodes:
                    if node.name in update_nodes_inputs_map.keys():
                        indices = update_nodes_inputs_map[node.name][0]
                        new_input_val = update_nodes_inputs_map[node.name][1]
                        for i in indices:
                            node.input[i] = new_input_val

        new_nodes = constant_to_add + get_new_onnx_nodes(nodes_to_delete, self.onnx_model.graph.node)
        update_nodes_inputs(new_nodes)
        initializer = get_new_onnx_nodes(nodes_to_delete, self.onnx_model.graph.initializer)
        if new_edges is not None:
            update_edges(new_edges, new_nodes)
            update_edges(new_edges, initializer)
        new_graph = onnx.helper.make_graph(nodes=new_nodes,
                                           name=self.onnx_model.graph.name,
                                           inputs=self.onnx_model.graph.input,
                                           outputs=self.onnx_model.graph.output,
                                           initializer=initializer,
                                           doc_string=self.onnx_model.graph.doc_string,
                                           value_info=self.onnx_model.graph.value_info,
                                           sparse_initializer=self.onnx_model.graph.sparse_initializer)

        metadata_props = {p.key: p.value for p in self.onnx_model.metadata_props}
        producer_name = self.onnx_model.producer_name
        producer_version = self.onnx_model.producer_version
        self.onnx_model = onnx.helper.make_model(new_graph, opset_imports=self.onnx_model.opset_import)
        self.onnx_model.producer_name = producer_name
        self.onnx_model.producer_version = producer_version
        onnx.helper.set_model_props(self.onnx_model, metadata_props)

    @staticmethod
    def _create_onnx_constant(name, data, outputs):
        tensor = onnx.numpy_helper.from_array(data, name=name)
        return onnx.helper.make_node(OnnxOpType.Constant, [], outputs, name=name, value=tensor)

    def save(self, save_path=None):
        if not save_path:
            save_path = str(self.model_path).replace(".onnx", "_sim.onnx")
        onnx.save(self.onnx_model, save_path)
        return save_path


def main(args=None):
    import time
    s1 = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Path to the model", required=True)
    parser.add_argument("--output", help="Path to the output model")
    args = parser.parse_args(args)
    onnx_sim = OnnxSimplifier(args.model)
    b_nodes = len(onnx_sim.meta_graph.nx_graph.nodes)
    s2 = time.time()
    onnx_sim.simplify()
    s3 = time.time()
    print(f"load takes {s2 - s1} seconds")
    print(f"simplify takes {s3 - s2} seconds")
    print("Deleted Ops")
    print(list(onnx_sim.deleted_ops.keys()))
    print(f"before {b_nodes} nodes, deleted {onnx_sim.get_deleted_nodes_count()} nodes"
          f" after {len(onnx_sim.meta_graph.nx_graph.nodes)} nodes")
    output_path = onnx_sim.save(args.output)
    print(f"Saved to {output_path}")


if "__main__" == __name__:
    main()
