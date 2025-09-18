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
from pathlib import PosixPath, WindowsPath
from typing import List, Any, Union, Generic, Dict
import abc
from enum import Enum

from uni.common.core.connectivity_map import ConnectivityMap, Tensor
from uni.common.core.multigraph.graph import MultiDiGraph
from uni.common.core.multigraph.edge import Edge
from uni.common.core.multigraph.typing import NodeObj
from uni.common.core.nnir_graph.semantics import DataFormat
from uni.common.logger import get_logger

logger = get_logger(__name__)


class MetaOpType(str, Enum):
    """
        special op types for meta nodes
        can't use same value as OnnxOpType because it is conflict in OnnxMetaNode.op_type
     """
    Placeholder = 'Placeholder'
    Output = 'Output'
    # for optional input
    DummyInput = 'DummyInput'
    # disconnected output
    DummyOutput = 'DummyOutput'
    Variable = 'Variable'
    NoOp = 'NoOp'


class BaseReader(abc.ABC, Generic[NodeObj]):

    def __init__(self, fw_model: Union[PosixPath, str, Any]):
        """
        fw_model can an str file path or fw model object
        """
        if isinstance(fw_model, (PosixPath, WindowsPath, str)):
            self.model = self._load_model(fw_model)
        else:
            self.model = fw_model

        self.tensors = ConnectivityMap()

    @staticmethod
    @abc.abstractmethod
    def _load_model(model_path) -> Any:
        pass

    @abc.abstractmethod
    def get_data_format(self) -> DataFormat:
        pass

    @abc.abstractmethod
    def get_metadata(self) -> Dict:
        pass

    @abc.abstractmethod
    def validate_model_input(self):
        pass

    def build_meta_graph(self) -> MultiDiGraph[NodeObj, Edge]:
        """ Build intermediate graph """
        nodes: list = self._build_nodes_and_connectivity()
        nodes.extend(self._build_dummy_nodes())
        edges: list = self._build_edges()
        self.validate_model_input()
        g = MultiDiGraph(nodes, edges)
        return g

    @abc.abstractmethod
    def _build_nodes_and_connectivity(self) -> List[NodeObj]:
        """ Returns a list of meta node objects.
            self.tensors are expected to be filled during this pass.
        """
        raise NotImplementedError()

    def _build_dummy_nodes(self) -> List[NodeObj]:
        """
        Create DummyOutput/DummyInput nodes for disconnected tensors and update tensors info

        Returns:
            A list of dummy output nodes
        """
        nodes = []
        for tid, t in self.tensors.items():
            assert t.dest or t.src
            if not t.dest:
                name = f'{t.src.name}_dummy_output_{t.src.index}'
                dummy_node: NodeObj = self._build_dummy_node(name, MetaOpType.DummyOutput, t)
                nodes.append(dummy_node)
                self.tensors.add_dest(tensor_id=tid, node_name=dummy_node.key, index=0)
            if not t.src:
                assert len(t.dest) == 1, 'dummy tensor is not expected to be shared'
                name = f'{t.dest[0].name}_dummy_input_{t.dest[0].index}'
                dummy_node = self._build_dummy_node(name, MetaOpType.DummyInput, t)
                nodes.append(dummy_node)
                self.tensors.add_source(tensor_id=tid, node_name=dummy_node.key, index=0)
        return nodes

    @abc.abstractmethod
    def _build_dummy_node(self, name: str, op: MetaOpType, tensor: Tensor) -> NodeObj:
        raise NotImplementedError()

    def _build_edges(self) -> List[Edge]:
        """ build edges from connectivity map """
        edges = []
        for tid, t in self.tensors.items():
            assert t.src, tid
            if not t.dest:
                logger.debug(f'output {t.src.index} of node {t.src} is not connected anywhere')
                continue
            for dest in t.dest:
                edge = Edge(src=t.src.name,
                            dest=dest.name,
                            src_index=t.src.index,
                            dest_index=dest.index,
                            shape=t.shape,
                            np_dtype=t.np_dtype)
                edges.append(edge)
        return edges
