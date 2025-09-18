# -------------------------------------------------------------------------------
# (c) Copyright 2022 Sony Semiconductor Israel, Ltd. All rights reserved.
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
from typing import List, Set, Dict
from packaging.version import Version

import tensorflow as tf

from mct_quantizers.keras.load_model import keras_load_quantized_model
from mct_quantizers.keras.metadata import MetadataLayer

from uni.common.core.connectivity_map import ConnectivityMap, Tensor
from uni.common.core.error import UnsupportedModelInputError, ModelErrorInputMessages
from uni.common.core.nnir_graph.semantics import DataFormat
from uni.common.core.uid_generator import UIDGenerator
from uni.common.parsers.base_reader import BaseReader, MetaOpType
from uni.common.util.dev import is_dev, is_skip_validate_input
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.tf_reader_helper import get_tensor_index, clone_layer, \
    get_inbound_nodes, get_layer_output_shapes, layer_is_model
from uni.common.logger import get_logger

logger = get_logger(__name__)


def get_model_keras_ver(model_path) -> str:
    model_path = str(model_path)
    if model_path.endswith('.h5'):
        import h5py
        return h5py.File(model_path).attrs['keras_version']
    elif model_path.endswith('.keras'):
        import json
        import zipfile
        with zipfile.ZipFile(model_path, 'r') as z:
            with z.open('metadata.json') as metadata_file:
                metadata = json.load(metadata_file)
        return metadata['keras_version']
    else:
        raise ValueError(f'Unsupported model format: {model_path}')


class TensorflowReader(BaseReader[TFMetaNode]):

    def validate_model_input(self):
        if is_skip_validate_input():
            return
        # BATCH_SIZE_ERR is not relevant for tensorflow
        for i, input_ in enumerate(self.model.inputs):
            input_shape = input_.shape

            if None in input_shape[1:]:
                raise UnsupportedModelInputError(i, ModelErrorInputMessages.DYNAMIC_INPUT_ERR)

    def get_metadata(self) -> Dict:
        from mct_quantizers.keras.metadata import get_metadata
        return get_metadata(self.model)

    @staticmethod
    def _load_model(model_path) -> tf.keras.Model:
        if not str(model_path).endswith(".keras"):
            raise ValueError("Only .keras file extension is supported")
        try:
            from edgemdt_cl.keras import custom_layers_scope
        except ImportError:
            import contextlib
            custom_layers_scope = contextlib.nullcontext
        try:
            with custom_layers_scope():
                model = keras_load_quantized_model(model_path, compile=False)
        except Exception as e:
            msg = 'Failed to load the model.'
            if isinstance(e, ValueError) and 'Quantize' in str(e):
                msg += ' unsupported format'

            try:
                # get get_model_keras_ver can fail in unsupported versions like windows < 2.16
                model_ver = Version(get_model_keras_ver(model_path))
                tf_ver = Version(tf.__version__)
                if model_ver.major != tf_ver.major or model_ver.minor != tf_ver.minor:
                    msg += f" Tensorflow version mismatch trying to load model created in {model_ver} with {tf_ver}."
            except Exception:    # pragma:
                pass
            raise RuntimeError(msg) from e

        try:
            logger.debug(f'Loaded keras model: keras_version={get_model_keras_ver(model_path)}')
        except Exception:    # pragma: no cover
            if os.getenv('DEV'):
                raise
        return model

    def get_data_format(self) -> DataFormat:
        return DataFormat.HWC

    @staticmethod
    def get_tf_op(tf_layer):
        """ this op is used in factory look-up """
        return tf_layer.__class__

    def _get_meta_node(self, layer, model):
        """
        Args:
            layer: the layer to convert
            model: the current model (can be different from self.model in case of nested model)
        Returns:
            TFMetaNode
        model used only in case of nested model to make sure that layer name is unique
        adding the model name to the layer name make it more clear in the graph but still not unique
        because the model name is not unique in a nested model this is why we add UIDGenerator.next()
        """
        tf_op = self.get_tf_op(layer)
        extra = None
        if layer.name in model.input_names:
            extra = {'ordinal': model.input_names.index(layer.name)}
        node_name = layer.name
        if node_name in self.nodes_names:
            node_name = f"{model.name}_{node_name}_{UIDGenerator.next()}"
        shared_group_id = layer.name if len(get_inbound_nodes(layer)) > 1 else None
        return TFMetaNode(node_name, tf_op, layer, extra=extra, inbound_node_index=0, shared_group_id=shared_group_id)

    @staticmethod
    def _copy_meta_node(op, layer, new_name, shared_group_id, inbound_node_index, extra=None):
        if layer is not None:
            layer = clone_layer(layer, new_name)
        return TFMetaNode(new_name,
                          op,
                          layer,
                          shared_group_id=shared_group_id,
                          inbound_node_index=inbound_node_index,
                          extra=extra)

    def _build_nodes_and_connectivity(self):
        """
        Partial description of the tensorflow model (self.model)
        model
              input_names: list[str] of input names
              layers: list[`KerasLayer`]
              outputs: list[`KerasTensor`]

        KerasLayer
              inbound_nodes: list[`Node`], this is the actual node.
                      contains more than one node, in case of layer sharing
              outbound_nodes: list[`Node`] list of nodes that are connected to output of the `KerasLayer`
                      can be empty when node output is connected to model output or disconnected
              input: `KerasTensor` CANNOT be trusted, because in layer sharing return only the first `KerasTensor`
              output: `KerasTensor` CANNOT be trusted, because in layer sharing return only the first `KerasTensor`
              input_shape: CANNOT be trusted, because in layer sharing with different shape can throw exception
              output_shape: CANNOT be trusted, because in layer sharing with different shape can throw exception
        Node
                  flat_input_ids: list[str] of the node inputs id(`KerasTensor`) object
                  flat_output_ids: list[str] of the node outputs id(`KerasTensor`) object
                  output_shapes: Optional[list[tuple[int...]], tuple[int...]]
        KerasTensor
              name: str, can't be used as id to find edges.
                      Because it is NOT unique in layer sharing, when node output is connected to node input
              _keras_history.tensor_index: int, use in `model.outputs` to get the `id` of `KerasTensor`
                      instead of using the python func "id".
                      In tensors that not in "model.outputs" "_keras_history" attr may not exist.
        """
        tf_meta_nodes: List[TFMetaNode] = []

        self.nodes_names: Set[str] = set()
        # __add_nodes and __add_output_nodes are called recursively for nested model
        self._add_nodes(self.model, tf_meta_nodes, self.tensors)
        self._add_output_nodes(self.model, tf_meta_nodes, self.tensors)
        return tf_meta_nodes

    def _build_dummy_node(self, name, op: MetaOpType, tensor: Tensor) -> TFMetaNode:
        return TFMetaNode(name, op, None, None)

    def _add_nodes(self, model, tf_meta_nodes: List[TFMetaNode], tensors: ConnectivityMap):
        """
            add nodes + duplicate nodes for layer sharing
            nested model is handled in _handle_layer_is_model
            layer sharing is handled in inbound_node_index
            layer sharing of nested model is handled in both inbound_node_index and _handle_layer_is_model
            this function is called recursively for nested model
            this is the reason for the complexity of this function and getting all the parameters instead of using self

        """
        for layer in model.layers:
            if isinstance(layer, MetadataLayer):
                continue
            if layer_is_model(layer):
                self._handle_layer_is_model(layer, tf_meta_nodes, tensors)
                continue

            meta_node = self._get_meta_node(layer, model)
            tf_meta_nodes.append(meta_node)
            self.nodes_names.add(meta_node.name)
            original_node_name = meta_node.name
            for inbound_node_index, inbound_node in enumerate(get_inbound_nodes(layer)):
                if inbound_node_index > 0:    # layer sharing
                    meta_node = self._copy_meta_node(meta_node.op,
                                                     layer,
                                                     new_name=f"{layer.name}_inbound_node_{inbound_node_index}",
                                                     shared_group_id=original_node_name,
                                                     inbound_node_index=inbound_node_index)
                    tf_meta_nodes.append(meta_node)
                    self.nodes_names.add(meta_node.name)
                for i, in_id in enumerate(inbound_node.flat_input_ids):
                    tensors.add_dest(tensor_id=in_id, node_name=meta_node.name, index=i)
                for i, out_id in enumerate(inbound_node.flat_output_ids):
                    tensors.add_source(tensor_id=out_id, node_name=meta_node.name, index=i)
                    tensors.add_shape(out_id, get_layer_output_shapes(layer, inbound_node_index)[i])

    def _handle_layer_is_model(self, layer, tf_meta_nodes, tensors: ConnectivityMap):
        internal_tf_meta_nodes: List[TFMetaNode] = []
        internal_tensors: ConnectivityMap = ConnectivityMap()
        self._add_nodes(layer, internal_tf_meta_nodes, internal_tensors)
        self._add_output_nodes(layer, internal_tf_meta_nodes, internal_tensors)
        tensors.update(internal_tensors)
        inputs_nodes = {
            n.extra['ordinal']: n    # type: ignore
            for n in internal_tf_meta_nodes if n.op == tf.keras.layers.InputLayer
        }
        output_nodes = {
            n.extra['ordinal']: n    # type: ignore
            for n in internal_tf_meta_nodes if n.op == MetaOpType.Output
        }
        #  set internal model inputs and outputs as NoOp
        for node in inputs_nodes.values():
            node.op = MetaOpType.NoOp
        for node in output_nodes.values():
            node.op = MetaOpType.NoOp

        tf_meta_nodes.extend(internal_tf_meta_nodes)
        for n in internal_tf_meta_nodes:
            self.nodes_names.add(n.name)

        org_input_names = {n.name: key for key, n in inputs_nodes.items()}
        org_output_names = {n.name: key for key, n in output_nodes.items()}
        for inbound_node_index, inbound_node in enumerate(get_inbound_nodes(layer)):
            for i, in_id in enumerate(inbound_node.flat_input_ids):
                if inbound_node_index > 0:
                    inputs_nodes, output_nodes = self._handle_sharing_nested_model(inbound_node_index, tf_meta_nodes,
                                                                                   internal_tf_meta_nodes, tensors,
                                                                                   internal_tensors, org_input_names,
                                                                                   org_output_names)
                tensors.add_dest(tensor_id=in_id, node_name=inputs_nodes[i].name, index=i)
            for i, out_id in enumerate(inbound_node.flat_output_ids):
                tensors.add_source(tensor_id=out_id, node_name=output_nodes[i].name, index=i)
                tensors.add_shape(out_id, get_layer_output_shapes(layer, inbound_node_index)[i])

    def _handle_sharing_nested_model(self, inbound_node_index, tf_meta_nodes, internal_tf_meta_nodes, tensors,
                                     internal_tensors, org_input_names, org_output_names):
        # node name is not unique in a nested model
        new_ending = f"_shared_model_{inbound_node_index}_uid{UIDGenerator.next()}"
        inputs_nodes = {}
        output_nodes = {}
        map_names = {}
        for node in internal_tf_meta_nodes:
            if node.shared_group_id is None:
                node.shared_group_id = node.name
            shared_group_id = node.shared_group_id
            new_node = self._copy_meta_node(node.op,
                                            node.keras_layer,
                                            new_name=f"{node.name}{new_ending}",
                                            shared_group_id=shared_group_id,
                                            inbound_node_index=node.inbound_node_index,
                                            extra=node.extra)
            map_names[node.name] = new_node.name
            tf_meta_nodes.append(new_node)
            #  maps input/output nodes with original names for the connectivity map
            if node.name in org_input_names:
                inputs_nodes[org_input_names[node.name]] = new_node
            if node.name in org_output_names:
                output_nodes[org_output_names[node.name]] = new_node
        tensors.update(internal_tensors.clone_with_new_names(map_names, new_ending))
        return inputs_nodes, output_nodes

    def _add_output_nodes(self, model, tf_meta_nodes, tensors: ConnectivityMap):
        # add output nodes
        for i, tensor in enumerate(model.outputs):
            # needs model name for model in model
            output_name = f"Output{i}"
            if output_name in self.nodes_names:
                # model name is not unique in a nested model
                output_name = f"{model.name}_{output_name}_{UIDGenerator.next()}"
            assert output_name not in self.nodes_names, f"Duplicate node name {output_name}"
            tensor_index = get_tensor_index(tensor)
            out_id = tensor.node.flat_output_ids[tensor_index]
            if is_dev():
                assert id(tensor) == int(out_id), "Tensorflow internal change"
            extra = {'ordinal': i, 'shape': tensors[out_id].shape}
            meta_node = TFMetaNode(output_name, MetaOpType.Output, None, extra=extra, inbound_node_index=None)
            tf_meta_nodes.append(meta_node)
            self.nodes_names.add(output_name)
            tensors.add_dest(tensor_id=out_id, node_name=output_name, index=0)
