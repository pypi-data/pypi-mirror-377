"""
Messaging Core - Python gRPC client for Messaging Core service.

This package provides generated gRPC client code for interacting with the Messaging Core service.
"""

# Version of the package
__version__ = "0.1.0"

# Import key modules to make them available at the package level
from messaging_core import users_pb2 as users
from messaging_core import auth_pb2 as auth
from messaging_core import messaging_pb2 as messaging
from messaging_core import conversation_pb2 as conversation
from messaging_core import attachment_pb2 as attachment

# Re-export the gRPC stubs for easier access
from messaging_core.users_pb2_grpc import *
from messaging_core.auth_pb2_grpc import *
from messaging_core.messaging_pb2_grpc import *
from messaging_core.conversation_pb2_grpc import *
from messaging_core.attachment_pb2_grpc import *

# Define what gets imported with 'from messaging_core import *'
__all__ = [
    'users',
    'auth',
    'messaging',
    'conversation',
    'attachment',
]