#!/usr/bin/env python
# coding: utf-8

from container_manager_mcp.container_manager import (
    container_manager,
    create_manager,
    ContainerManagerBase,
    DockerManager,
    PodmanManager,
)
from container_manager_mcp.container_manager_mcp import container_manager_mcp

"""
container-manager

Manage your containers using docker, podman, compose, or docker swarm!
"""

__all__ = [
    "container_manager_mcp",
    "create_manager",
    "container_manager",
    "ContainerManagerBase",
    "DockerManager",
    "PodmanManager",
]
