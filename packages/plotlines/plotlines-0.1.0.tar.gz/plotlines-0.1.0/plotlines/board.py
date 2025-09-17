#! /usr/bin/env python3
# encoding: UTF-8

# This file is part of Plotlines.

# Plotlines is free software: You can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

# Plotlines is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the
# GNU General Public License along with Plotlines.
# If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations  # Until Python 3.14 is everywhere

from collections import defaultdict
from collections import deque
from collections import UserDict
from collections.abc import Generator
import dataclasses
import datetime
import functools
import logging
from numbers import Number
import string
import typing
import uuid
import weakref

from plotlines.coordinates import Coordinates


@dataclasses.dataclass(unsafe_hash=True)
class Item:
    store: typing.ClassVar[set] = defaultdict(weakref.WeakSet)

    number:     int = dataclasses.field(init=False)
    contents:   list = dataclasses.field(default_factory=list, compare=False, kw_only=True)

    def __post_init__(self, *args):
        self.number = max([j.number for i in self.__class__.store.values() for j in i], default=0) + 1
        self.__class__.store[self.__class__].add(self)


@dataclasses.dataclass(unsafe_hash=True)
class Link:
    joins:  set[Item] = dataclasses.field(default_factory=weakref.WeakSet, compare=False, kw_only=True)


@dataclasses.dataclass(unsafe_hash=True)
class Pin(Item):
    pos:        Coordinates = None
    shape:      str = dataclasses.field(default="", kw_only=True)
    label:      str = dataclasses.field(default="", kw_only=True)


@dataclasses.dataclass(unsafe_hash=True)
class Port(Pin, Link):
    pass


@dataclasses.dataclass(unsafe_hash=True)
class Node(Pin):
    ports:  dict[int, Port] = dataclasses.field(default_factory=dict, compare=False)

    def __post_init__(self, *args):
        super().__post_init__(*args)
        if not self.pos:
            return
        self.pos = Coordinates(*self.pos)

    @property
    def nearby(self):
        edges = [e for port in self.ports.values() for e in port.joins if isinstance(e, Edge)]
        return [n for edge in edges for p in edge.ports for n in p.joins if isinstance(n, Node) and n is not self]

    @property
    def density(self):
        "Degree of node divided by number of neighbours"
        return []

    @property
    def edges(self):
        return [i for p in self.ports.values() for i in p.joins if isinstance(i, Edge)]

    def connect(self, other: Pin, edge=None):
        rv = edge or Edge()
        rv.ports[0].joins.add(self)
        self.ports[len(self.ports)] = rv.ports[0]

        rv.ports[1].joins.add(other)
        other.ports[len(other.ports)] = rv.ports[1]
        return rv

    @functools.singledispatch
    def spacing(self, other: Node, edge=None) -> dict[tuple[Pin, Pin], Number]:
        mine = {i: i.pos for i in self.ports.values()} | {self: self.pos}
        others = {i: i.pos for i in other.ports.values()} | {other: other.pos}
        rv = {(mk, ok): abs(ov - mv) for (mk, mv), (ok, ov) in zip(mine.items(), others.items())}
        return rv


@dataclasses.dataclass(unsafe_hash=True)
class Edge(Item):
    pos_0: dataclasses.InitVar[Coordinates | None] = None
    pos_1: dataclasses.InitVar[Coordinates | None] = None
    trail: str = ""
    ports: list[Port] = dataclasses.field(default_factory=list, compare=False)

    def __post_init__(self, pos_0: tuple, pos_1: tuple, *args):
        super().__post_init__(*args)
        coords = [Coordinates(*c) for c in (pos_0, pos_1) if c is not None]
        if coords:
            self.ports = [
                Port(joins={self}, pos=coords[0]),
                Port(joins={self}, pos=coords[-1]),
            ]
        else:
            self.ports = [Port(joins={self}), Port(joins={self})]


class Board:

    @staticmethod
    def build_graph(ending: list[str], loading: list[int], trails: int, **kwargs) -> Generator[int, Edge]:
        frame = deque([Node(label=name) for name in ending])

        while len(Pin.store[Node]) + len(Pin.store[Edge]) < max(loading):
            # Connect each node to one or more trail edges
            try:
                node = frame.popleft()
            except IndexError:
                break
            else:
                frame.append(Node())
                edge = node.connect(frame[-1])
                yield edge.number, edge
        else:
            # Finish with start node
            start = Node(label="start")
            for node in frame:
                edge = start.connect(node)
                yield edge.number, edge


    @staticmethod
    def layout_graph(graph: dict) -> dict:
        return graph


    @staticmethod
    def toml_graph(graph: dict) -> Generator[str]:
        yield "[[nodes]]"
        yield "[[links]]"
