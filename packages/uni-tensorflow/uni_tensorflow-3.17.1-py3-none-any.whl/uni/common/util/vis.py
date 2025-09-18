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
# FIXME ignoring the whole file for mypy
# must appear before the first non-comment line
# type: ignore

# FIXME
import dataclasses
import json
from typing import List, Union

import os
import itertools
from uni.common.logger import get_logger

logger = get_logger(__name__)

# for vis graph: create json in this structure:
# {"nodes": [{ "id": "", "group": "", "label": "", "title": "", "properties": {}],
#  "edges": [{"id": "", "from": "", "to": "", "label": "", "title": "", "properties": { }} ],
#  "options": {}}


@dataclasses.dataclass
class VisNode:
    id: Union[str, int]
    label: str
    title: str
    properties: dict
    group = ""

    def asdict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class VisEdge(VisNode):
    from_: str
    to: str

    def asdict(self):
        d = dataclasses.asdict(self)
        d['from'] = d['from_']
        del d['from_']
        return d


class VisConverter:
    counter = itertools.count(1)

    @classmethod
    def convert(cls, graph):
        nodes = [n.asdict() for n in cls.convert_nodes(graph)]
        edges = [e.asdict() for e in cls.convert_edges(graph)]
        return {"nodes": nodes, "edges": edges, "options": {}}

    @staticmethod
    def convert_nodes(graph) -> List[VisNode]:
        raise NotImplementedError

    @staticmethod
    def convert_edges(graph) -> List[VisEdge]:
        raise NotImplementedError

    @staticmethod
    def _get_label(node):
        label = node.__class__.__name__
        return label

    @staticmethod
    def _get_prop(node):
        d = node.__dict__ if hasattr(node, '__dict__') else {}
        d = dict((str(k), str(v)) for k, v in d.items() if not k.startswith('_'))
        return d

    @classmethod
    def dump_vis_json(cls, graph, path, auto_prefix=True):
        dirname = os.path.dirname(path)
        if auto_prefix:
            filename = os.path.basename(path)
            filename = f'{next(cls.counter)}_{filename}'
            path = os.path.join(dirname, filename)

        os.makedirs(dirname, exist_ok=True)

        vis_graph = cls.convert(graph)

        def default(a):
            try:    # pragma: no cover
                return a.tolist()
            except Exception:    # pragma: no cover
                pass
            try:    # pragma: no cover
                return a.__dict__
            except Exception:    # pragma: no cover
                return 'unknown'

        with open(path, 'w') as f:
            json.dump(vis_graph, f, default=default)
        logger.debug(f'Wrote {path}')


class MultigraphVis(VisConverter):

    @classmethod
    def convert_nodes(cls, graph):
        nodes = [
            VisNode(id=n.name, label=cls._get_label(n), title=n.name, properties=cls._get_prop(n))
            for n in graph.get_nodes(data=True)
        ]

        return nodes

    @classmethod
    def convert_edges(cls, graph):
        edges = [
            VisEdge(id=i, from_=e.src, to=e.dest, label="", title="", properties=cls._get_prop(e))
            for i, e in enumerate(graph.get_edges())
        ]
        return edges


class OnnxMetaGraphVis(MultigraphVis):

    @classmethod
    def _get_label(cls, n):
        return super()._get_label(n) + '::' + n.op_type
