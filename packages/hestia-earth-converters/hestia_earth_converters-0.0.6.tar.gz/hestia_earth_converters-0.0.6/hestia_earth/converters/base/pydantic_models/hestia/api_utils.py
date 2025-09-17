from functools import cache
from typing import TypeVar
from hestia_earth.utils.api import download_hestia as api_download_hestia
from hestia_earth.schema.pydantic import Node
import hestia_earth.schema.pydantic as schema

AnyNode = TypeVar("AnyNode", bound="Node")

download_hestia = cache(api_download_hestia)


def _node_type(node: dict):
    node_type = node.get('@type') or node.get('type')
    return node_type if isinstance(node_type, str) else node_type.value


def update_hestia_node(node: Node) -> AnyNode:
    downloaded_node_d = download_hestia(node.id, node_type=str(node.type)) or {}

    original_node_d = node.model_dump(by_alias=True, exclude_none=True)
    node_type = _node_type(original_node_d)
    updated_node_d = (
        {'dataPrivate': False} if node_type not in ['Term'] else {}
    ) | downloaded_node_d | original_node_d

    try:
        updated_node_d = updated_node_d | {"flow_metadata": node.flow_metadata}
    except Exception:
        pass

    try:
        return getattr(schema, node_type)(**updated_node_d)
    except Exception as e:
        print(e)
        return type(node)(**updated_node_d)
