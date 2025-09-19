from dataclasses import field
import os
from uuid import UUID
from typing import Any, Optional

from _pytest.compat import cached_property

from vellum import ApiVersionEnum, Vellum, VellumEnvironment
from vellum.client.core import UniversalBaseModel
from vellum.workflows.context import ExecutionContext
from workflow_server.config import IS_VPC, VELLUM_API_URL_HOST, VELLUM_API_URL_PORT

DEFAULT_TIMEOUT_SECONDS = 60 * 30


def create_vellum_client(
    api_key: str,
    api_version: Optional[ApiVersionEnum] = None,
) -> Vellum:
    """
    Create a VellumClient with proper environment configuration.

    Args:
        api_key: The API key for the Vellum client
        api_version: Optional API version to use

    Returns:
        Configured Vellum client instance

    Note: Ideally we replace this with `vellum.workflows.vellum_client.create_vellum_client`
    """
    if IS_VPC:
        environment = VellumEnvironment(
            default=os.getenv("VELLUM_DEFAULT_API_URL", VellumEnvironment.PRODUCTION.default),
            documents=os.getenv("VELLUM_DOCUMENTS_API_URL", VellumEnvironment.PRODUCTION.documents),
            predict=os.getenv("VELLUM_PREDICT_API_URL", VellumEnvironment.PRODUCTION.predict),
        )
    elif os.getenv("USE_LOCAL_VELLUM_API") == "true":
        VELLUM_API_URL = f"http://{VELLUM_API_URL_HOST}:{VELLUM_API_URL_PORT}"
        environment = VellumEnvironment(
            default=VELLUM_API_URL,
            documents=VELLUM_API_URL,
            predict=VELLUM_API_URL,
        )
    else:
        environment = VellumEnvironment.PRODUCTION

    return Vellum(
        api_key=api_key,
        environment=environment,
        api_version=api_version,
    )


class BaseExecutorContext(UniversalBaseModel):
    inputs: dict
    state: Optional[dict] = None
    timeout: int = DEFAULT_TIMEOUT_SECONDS
    files: dict[str, str]
    environment_api_key: str
    api_version: Optional[ApiVersionEnum] = None
    execution_id: UUID
    module: str
    execution_context: ExecutionContext = field(default_factory=ExecutionContext)
    request_start_time: int
    stream_start_time: int = 0
    vembda_public_url: Optional[str] = None
    node_output_mocks: Optional[list[Any]] = None
    environment_variables: Optional[dict[str, str]] = None
    previous_execution_id: Optional[UUID] = None
    feature_flags: Optional[dict[str, bool]] = None

    @property
    def container_overhead_latency(self) -> int:
        return self.stream_start_time - self.request_start_time if self.stream_start_time else -1

    @property
    def trace_id(self) -> UUID:
        return self.execution_context.trace_id

    @cached_property
    def vellum_client(self) -> Vellum:
        return create_vellum_client(
            api_key=self.environment_api_key,
            api_version=self.api_version,
        )

    def __hash__(self) -> int:
        # do we think we need anything else for a unique hash for caching?
        return hash(str(self.execution_id))


class WorkflowExecutorContext(BaseExecutorContext):
    node_id: Optional[UUID] = None  # Sent during run from node UX


class NodeExecutorContext(BaseExecutorContext):
    node_module: str
    node_name: str
