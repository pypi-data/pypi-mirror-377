from airflow import DAG
from airflow.models import BaseOperator
from datetime import datetime
from typing import Callable, Optional
import os

from kubernetes.client import models as k8s
from starflow.custom_operators.k8s_operator import starflowKubernetesPodOperator
from starflow.custom_operators.docker_operator import starflowDockerOperator
from starflow.custom_operators.python_operator import PythonOperator
from starflow.custom_operators.worker_operator import starflowWorkerOperator
from starflow.logger import get_configured_logger
from starflow.schemas import shared_storage_map, StorageSource


class Task(object):
    """
    The Task object represents a task in a workflow.
    It is only instantiated by processes parsing dag files in Airflow.
    """
    def __init__(
        self,
        dag: DAG,
        task_id: str,
        workspace_id: int,
        piece: dict,
        piece_input_kwargs: dict,
        workflow_shared_storage: dict = None,
        container_resources: dict = None,
        username: Optional[str] = None,
        trigger_rule="all_success",
        **kwargs
    ) -> None:
        # Task configuration and attributes
        self.task_id = task_id
        self.workspace_id = workspace_id
        self.logger = get_configured_logger(f"{self.__class__.__name__ }-{self.task_id}")
        self.logger.info('### Configuring task object ###')
        self.dag = dag
        self.dag_id = self.dag.dag_id
        self.repository_url = piece["repository_url"]
        self.repository_version = piece["repository_version"]
        self.piece = piece
        self.piece_input_kwargs = piece_input_kwargs
        self.username_var = username
        self.trigger_rule = trigger_rule
        if "execution_mode" not in self.piece:
            self.execution_mode = "docker"
        else:
            self.execution_mode = self.piece["execution_mode"]

        # Shared storage
        if not workflow_shared_storage:
            workflow_shared_storage = {}
        shared_storage_source_name = StorageSource(workflow_shared_storage.pop("source", "None")).name
        provider_options = workflow_shared_storage.pop("provider_options", {})
        if shared_storage_map[shared_storage_source_name]:
            self.workflow_shared_storage = shared_storage_map[shared_storage_source_name](
                **workflow_shared_storage,
                **provider_options
            )
        else:
            self.workflow_shared_storage = shared_storage_map[shared_storage_source_name]

        # Container resources
        self.container_resources = container_resources

        # Get deploy mode
        self.deploy_mode = os.environ.get('STARFLOW_DEPLOY_MODE', 'prod')

        # Set up task operator
        self._task_operator = self._set_operator()
    
    def _construct_image_url(self) -> str:
        """Construct the Docker image URL from repository_url and piece name"""
        # Extract the base image name from repository_url
        # repository_url is like: ghcr.io/prochain-star-atlas/prochain-starflow-pieces:0.1.75-group0
        # We need to construct: ghcr.io/prochain-star-atlas/prochain-starflow-pieces:0.1.75-group0
        
        # For now, use the repository_url as the base and append the piece name
        # This matches the pattern we see in the logs
        base_image = self.repository_url
        if ':' in base_image:
            # If it already has a tag, use it as is
            return base_image
        else:
            # If no tag, append the version
            return f"{base_image}:{self.repository_version}"

    def _set_operator(self) -> BaseOperator:
        """
        Set Airflow Operator according to deploy mode and Piece execution mode.
        """

        # References:
        # - https://airflow.apache.org/docs/apache-airflow/1.10.14/_api/airflow/contrib/operators/kubernetes_pod_operator/index.html
        # - https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html
        # - https://www.astronomer.io/guides/templating/
        # - good example: https://github.com/apache/airflow/blob/main/tests/system/providers/cncf/kubernetes/example_kubernetes.py
        # - commands HAVE to go in a list object: https://stackoverflow.com/a/55149915/11483674

        return starflowKubernetesPodOperator(
            dag_id=self.dag_id,
            task_id=self.task_id,
            piece_name=self.piece.get('name'),
            deploy_mode=self.deploy_mode,
            repository_url=self.repository_url,
            repository_version=self.repository_version,
            workspace_id=self.workspace_id,
            piece_input_kwargs=self.piece_input_kwargs,
            workflow_shared_storage=self.workflow_shared_storage,
            container_resources=self.container_resources,
            # ----------------- Kubernetes -----------------
            namespace='airflow',
            image=self.piece.get("source_image") or self._construct_image_url(),
            image_pull_policy='IfNotPresent',
            name=f"airflow-worker-pod-{self.task_id}",
            startup_timeout_seconds=600,
            annotations={"sidecar.istio.io/inject": "false"}, # TODO - remove this when istio is working with airflow k8s pod
            # cmds=["/bin/bash"],
            # arguments=["-c", "sleep 120;"],
            cmds=["starflow"],
            arguments=["run-piece-k8s"],
            do_xcom_push=True,
            in_cluster=True,
            username=self.username_var,
            volume_mounts=[
                k8s.V1VolumeMount(
                    name='volume-prod', mount_path='/var/mount_secrets', sub_path=None, read_only=True
                )
            ],
            volumes=[
                k8s.V1Volume(
                    name="volume-prod",
                    secret=k8s.V1SecretVolumeSource(
                        secret_name="airflow-worker-secrets"
                    )
                )
            ],
            trigger_rule=self.trigger_rule
        )
            

    def __call__(self) -> Callable:
        return self._task_operator
