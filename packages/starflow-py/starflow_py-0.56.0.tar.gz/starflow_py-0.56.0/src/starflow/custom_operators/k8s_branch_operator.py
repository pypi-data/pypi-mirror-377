from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.utils.context import Context
from kubernetes.client import models as k8s
from kubernetes import client, config
from kubernetes.stream import stream as kubernetes_stream
from typing import Dict, Iterable, Optional, Any
from contextlib import closing
import ast
import copy

from airflow.operators.python import BranchPythonOperator
from starflow.utils import dict_deep_update
from starflow.client.starflow_backend_client import starflowBackendRestClient
from starflow.schemas import WorkflowSharedStorage, ContainerResourcesModel
from starflow.storage.s3 import S3StorageRepository
from starflow.logger import get_configured_logger
from airflow.exceptions import AirflowException
from airflow.providers.cncf.kubernetes.utils.xcom_sidecar import PodDefaults
import json
import os
from airflow.operators.branch import BaseBranchOperator

class starflowKubernetesBranchPodOperator(KubernetesPodOperator, BaseBranchOperator):
    def __init__(
        self,
        dag_id: str,
        task_id: str,
        piece_name: str,
        deploy_mode: str, # TODO enum
        repository_url: str,
        repository_version: str,
        workspace_id: int,
        task_id_main_branch: str | Iterable[str],
        task_id_else_branch: str | Iterable[str],
        username: Optional[str] = None,
        piece_input_kwargs: Optional[Dict] = None,
        workflow_shared_storage: WorkflowSharedStorage = None,
        container_resources: Optional[Dict] = None,
        **k8s_operator_kwargs
    ):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("=" * 80)
        logger.info(f"[StarflowK8sBranchOperator] INIT METHOD CALLED - task_id: {task_id}")
        logger.info(f"[StarflowK8sBranchOperator] dag_id: {dag_id}")
        logger.info(f"[StarflowK8sBranchOperator] piece_name: {piece_name}")
        logger.info(f"[StarflowK8sBranchOperator] repository_url: {repository_url}")
        logger.info(f"[StarflowK8sBranchOperator] repository_version: {repository_version}")
        logger.info(f"[StarflowK8sBranchOperator] workspace_id: {workspace_id}")
        logger.info("=" * 80)
        
        self.logger = get_configured_logger("starflowKubernetesBranchPodOperator")
        self.task_id = task_id
        self.piece_name = piece_name
        self.deploy_mode = deploy_mode
        self.repository_url = repository_url
        self.repository_version = repository_version
        self.workspace_id = workspace_id
        self.piece_input_kwargs = piece_input_kwargs
        self.workflow_shared_storage = workflow_shared_storage
        self.piece_source_image = k8s_operator_kwargs["image"]
        self.username_var = username
        self.task_id_main_branch = task_id_main_branch
        self.task_id_else_branch = task_id_else_branch

        # Environment variables
        pod_env_vars = {
            "STARFLOW_PIECE": piece_name,
            "WORKSPACE_ID": str(workspace_id),
            "STARFLOW_INSTANTIATE_PIECE_KWARGS": str({
                "deploy_mode": deploy_mode,
                "task_id": task_id,
                "dag_id": dag_id,
            }),
            "STARFLOW_RUN_PIECE_KWARGS": str(piece_input_kwargs),
            "STARFLOW_WORKFLOW_SHARED_STORAGE": workflow_shared_storage.model_dump_json() if workflow_shared_storage else "",
            "AIRFLOW_CONTEXT_EXECUTION_DATETIME": "{{ dag_run.logical_date | ts_nodash }}",
            "AIRFLOW_CONTEXT_DAG_RUN_ID": "{{ run_id }}",
            # "OPEN_ID_SERVER_URL": os.environ['OPEN_ID_SERVER_URL'],
            # "OPEN_ID_CLIENT_ID": os.environ['OPEN_ID_CLIENT_ID'],
            # "OPEN_ID_REALM_NAME": os.environ['OPEN_ID_REALM_NAME'],
            # "OPEN_ID_CLIENT_SECRET": os.environ['OPEN_ID_CLIENT_SECRET'],
            # "URL_PUT_START_DOCK": os.environ['URL_PUT_START_DOCK'],
            # "URL_GET_FLEET_MOVEMENT_CALCULATION": os.environ['URL_GET_FLEET_MOVEMENT_CALCULATION'],
            # "URL_GET_FLEET_MINING_CALCULATION": os.environ['URL_GET_FLEET_MINING_CALCULATION'],
            # "URL_PUT_LOAD_CARGO": os.environ['URL_PUT_LOAD_CARGO'],
            # "URL_PUT_LOAD_AMMO": os.environ['URL_PUT_LOAD_AMMO'],
            # "URL_PUT_LOAD_FUEL": os.environ['URL_PUT_LOAD_FUEL'],
            # "URL_PUT_UNLOAD_CARGO": os.environ['URL_PUT_UNLOAD_CARGO'],
            # "URL_PUT_UNLOAD_AMMO": os.environ['URL_PUT_UNLOAD_AMMO'],
            # "URL_PUT_UNLOAD_FUEL": os.environ['URL_PUT_UNLOAD_FUEL'],
            # "URL_PUT_START_MINING": os.environ['URL_PUT_START_MINING'],
            # "URL_PUT_STOP_MINING": os.environ['URL_PUT_STOP_MINING'],
            # "URL_PUT_START_DOCK": os.environ['URL_PUT_START_DOCK'],
            # "URL_PUT_START_UNDOCK": os.environ['URL_PUT_START_UNDOCK'],
            # "URL_PUT_START_SUBWARP": os.environ['URL_PUT_START_SUBWARP'],
            # "URL_PUT_START_EXITSUBWARP": os.environ['URL_PUT_START_EXITSUBWARP'],
            # "URL_PUT_START_WARP": os.environ['URL_PUT_START_WARP'],
            # "URL_PUT_START_EXITWARP": os.environ['URL_PUT_START_EXITWARP'],
            # "URL_GET_LIST_FLEET": os.environ['URL_GET_LIST_FLEET'],
            # "OPEN_ID_USERNAME_SERVICE_USER": os.environ['OPEN_ID_USERNAME_SERVICE_USER'],
            # "OPEN_ID_PASSWORD_SERVICE_USER": os.environ['OPEN_ID_PASSWORD_SERVICE_USER']
        }

        # Container resources
        if container_resources is None:
            container_resources = {}
        base_container_resources_model = ContainerResourcesModel(
            requests={"cpu": "100m", "memory": "128Mi",},
            limits={"cpu": "100m", "memory": "128Mi"},
            use_gpu=False,
        )
        basic_container_resources = base_container_resources_model.model_dump()
        updated_container_resources = dict_deep_update(basic_container_resources, container_resources)
        use_gpu = updated_container_resources.pop("use_gpu", False)
        if use_gpu:
            updated_container_resources["limits"]["nvidia.com/gpu"] = "1"
        container_resources_obj = k8s.V1ResourceRequirements(**updated_container_resources)

        # Extra volume and volume mounts - for DEV mode only
        # volumes_dev, volume_mounts_dev = None, None
        # if self.deploy_mode == 'local-k8s-dev':
        #     volumes_dev, volume_mounts_dev = self._make_volumes_and_volume_mounts_dev()

        super().__init__(
            task_id=task_id,
            env_vars=pod_env_vars,
            container_resources=container_resources_obj,
            # volumes=volumes_dev,
            # volume_mounts=volume_mounts_dev,
            **k8s_operator_kwargs
        )

        self.isMainBranchSelected = True

    def choose_branch(self, context: Context) -> str | Iterable[str]:
        if self.isMainBranchSelected:
            return self.task_id_main_branch
        else:
            return self.task_id_else_branch

    def _make_volumes_and_volume_mounts_dev(self):
        """
        Make volumes and volume mounts for the pod when in DEVELOPMENT mode.
        """
        config.load_incluster_config()
        k8s_client = client.CoreV1Api()

        all_volumes = []
        all_volume_mounts = []

        repository_raw_project_name = str(self.piece_source_image).split('/')[-1].split(':')[0]
        persistent_volume_claim_name = 'pvc-{}'.format(str(repository_raw_project_name.lower().replace('_', '-')))
        persistent_volume_name = 'pv-{}'.format(str(repository_raw_project_name.lower().replace('_', '-')))

        pvc_exists = False
        try:
            k8s_client.read_namespaced_persistent_volume_claim(name=persistent_volume_claim_name, namespace='default')
            pvc_exists = True
        except client.rest.ApiException as e:
            if e.status != 404:
                raise e

        pv_exists = False
        try:
            k8s_client.read_persistent_volume(name=persistent_volume_name)
            pv_exists = True
        except client.rest.ApiException as e:
            if e.status != 404:
                raise e

        if pv_exists and pvc_exists:
            volume_dev_pieces = k8s.V1Volume(
                name='dev-op-{path_name}'.format(path_name=str(repository_raw_project_name.lower().replace('_', '-'))),
                persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
                    claim_name=persistent_volume_claim_name
                ),
            )
            volume_mount_dev_pieces = k8s.V1VolumeMount(
                name='dev-op-{path_name}'.format(path_name=str(repository_raw_project_name.lower().replace('_', '-'))),
                mount_path=f'/home/starflow/pieces_repository',
                sub_path=None,
                read_only=True
            )
            all_volumes.append(volume_dev_pieces)
            all_volume_mounts.append(volume_mount_dev_pieces)

        ######################## For local starflow-py dev ###############################################
        starflow_package_local_claim_name = 'starflow-dev-volume-claim'
        pvc_exists = False
        try:
            k8s_client.read_namespaced_persistent_volume_claim(name=starflow_package_local_claim_name, namespace='default')
            pvc_exists = True
        except client.rest.ApiException as e:
            if e.status != 404:
                raise e

        if pvc_exists:
            volume_dev = k8s.V1Volume(
                name='jobs-persistent-storage-dev',
                persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name=starflow_package_local_claim_name),
            )
            """
            # TODO
            Remove deprecated_volume_mount_dev once we have all the pieces repositories updated
            with the new base pod image
            """
            volume_mount_pkg = k8s.V1VolumeMount(
                name='jobs-persistent-storage-dev',
                mount_path='/usr/local/lib/python3.10/site-packages/starflow/',
                sub_path=None,
                read_only=True
            )
            all_volumes.append(volume_dev)
            all_volume_mounts.append(volume_mount_pkg)

        return all_volumes, all_volume_mounts

    def build_pod_request_obj(self, context: Optional['Context'] = None) -> k8s.V1Pod:
        """
        We override this method to add the shared storage to the pod.
        This function runs after our own self.execute, by super().execute()
        """
        pod = super().build_pod_request_obj(context)
        self.task_id_replaced = self.task_id.lower().replace("_", "-") # doing this because airflow doesn't allow underscores and upper case in mount names and max len is 63
        self.shared_storage_base_mount_path = '/home/shared_storage'

        # Fix pod name to comply with Kubernetes naming rules (no underscores)
        if pod.metadata.name:
            # Replace underscores with hyphens and ensure it's lowercase
            pod.metadata.name = pod.metadata.name.lower().replace("_", "-")
            # Ensure it starts and ends with alphanumeric characters
            pod.metadata.name = pod.metadata.name.strip("-")
            if not pod.metadata.name[0].isalnum():
                pod.metadata.name = "pod-" + pod.metadata.name
            if not pod.metadata.name[-1].isalnum():
                pod.metadata.name = pod.metadata.name + "-pod"

        pod.metadata.namespace = "airflow"
        pod.spec.image_pull_secrets = [k8s.V1LocalObjectReference('ghcr-login-secret')]

        # Override xcom sidecar image to use Harbor registry instead of quay.io
        if pod.spec.containers:
            for container in pod.spec.containers:
                if container.name == "airflow-xcom-sidecar":
                    container.image = "harbor.atlassistant.com/public/alpine:latest"
                    self.logger.info(f"[StarflowK8sBranchOperator] Updated xcom sidecar image to: {container.image}")

        # if not self.workflow_shared_storage or self.workflow_shared_storage.mode.name == 'none':
        #     return pod
        # if self.workflow_shared_storage.source.name in ["aws_s3", "gcs"]:
        #     pod = self.add_shared_storage_sidecar(pod)
        # elif self.workflow_shared_storage.source.name == "local":
        #     pod = self.add_local_shared_storage_volumes(pod)

        return pod

    def add_local_shared_storage_volumes(self, pod: k8s.V1Pod) -> k8s.V1Pod:
        """Adds local shared storage volumes to the pod."""
        pod_cp = copy.deepcopy(pod)
        pod_cp.spec.volumes = pod.spec.volumes or []
        pod_cp.spec.volumes.append(
            k8s.V1Volume(
                name=f'workflow-shared-storage-volume-{self.task_id_replaced}'[0:63], # max resource name in k8s is 63 chars
                persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name="starflow-workflow-shared-storage-volume-claim")
            )
        )
        # Add volume mounts for upstream tasks, using subpaths
        pod_cp.spec.containers[0].volume_mounts = pod_cp.spec.containers[0].volume_mounts or []
        for tid in self.shared_storage_upstream_ids_list:
            pod_cp.spec.containers[0].volume_mounts.append(
                k8s.V1VolumeMount(
                    name=f'workflow-shared-storage-volume-{self.task_id_replaced}'[0:63], # max resource name in k8s is 63 chars
                    mount_path=f"{self.shared_storage_base_mount_path}/{tid}",  # path inside main container
                    mount_propagation="HostToContainer",
                    read_only=True,
                )
            )
        # Add volume mount for this task
        pod_cp.spec.containers[0].volume_mounts.append(
            k8s.V1VolumeMount(
                name=f'workflow-shared-storage-volume-{self.task_id_replaced}'[0:63],  # max resource name in k8s is 63 chars
                mount_path=f"{self.shared_storage_base_mount_path}/{self.task_id}",  # path inside main container
                mount_propagation="Bidirectional",
                read_only=True,
            )
        )
        return pod_cp

    def _validate_storage_piece_secrets(self, storage_piece_secrets: Dict[str, Any]):
        validated = False
        if self.workflow_shared_storage.source.name == 'aws_s3':
            s3_storage_repository = S3StorageRepository()
            validated = s3_storage_repository.validate_s3_credentials_access(
                access_key=storage_piece_secrets.get('AWS_ACCESS_KEY_ID'),
                secret_key=storage_piece_secrets.get('AWS_SECRET_ACCESS_KEY'),
                bucket=self.workflow_shared_storage.bucket,
            )
        return validated

    def add_shared_storage_sidecar(self, pod: k8s.V1Pod) -> k8s.V1Pod:
        """
        - add shared storage sidecar container to the pod
        - add shared storage volume mounts to the sidecar container
        - add FUSE mounts configuration as env vars to the sidecar container
        """
        # Set up pod Volumes and containers VolumemMounts from Upstream tasks
        volume_mounts_main_container = list()
        volume_mounts_sidecar_container = list()
        pod_volumes_list = list()
        for tid in self.shared_storage_upstream_ids_list:
            tid_replaced = tid.lower().replace("_", "-") # Doing this because k8s doesn't allow underscores in volume names
            volume_mounts_main_container.append(
                k8s.V1VolumeMount(
                    name=f'workflow-shared-storage-volume-{tid_replaced}'[0:63], # max resource name in k8s is 63 chars
                    mount_path=f"{self.shared_storage_base_mount_path}/{tid}",  # path inside main container
                    mount_propagation="HostToContainer",
                    read_only=True,
                )
            )
            volume_mounts_sidecar_container.append(
                k8s.V1VolumeMount(
                    name=f'workflow-shared-storage-volume-{tid_replaced}'[0:63], # max resource name in k8s is 63 chars
                    mount_path=f"{self.shared_storage_base_mount_path}/{tid}",  # path inside sidecar container
                    mount_propagation="Bidirectional",
                )
            )
            pod_volumes_list.append(
                k8s.V1Volume(
                    name=f'workflow-shared-storage-volume-{tid_replaced}'[0:63], # max resource name in k8s is 63 chars
                    empty_dir=k8s.V1EmptyDirVolumeSource()
                )
            )
        # Set up pod Volumes and containers VolumemMounts for this Operator results
        volume_mounts_main_container.append(
            k8s.V1VolumeMount(
                name=f'workflow-shared-storage-volume-{self.task_id_replaced}'[0:63], # max resource name in k8s is 63 chars
                mount_path=f"{self.shared_storage_base_mount_path}/{self.task_id}",  # path inside main container
                mount_propagation="HostToContainer",
                read_only=False,
            )
        )
        volume_mounts_sidecar_container.append(
            k8s.V1VolumeMount(
                name=f'workflow-shared-storage-volume-{self.task_id_replaced}'[0:63], # max resource name in k8s is 63 chars
                mount_path=f"{self.shared_storage_base_mount_path}/{self.task_id}",  # path inside sidecar container
                mount_propagation="Bidirectional",
            )
        )
        pod_volumes_list.append(
            k8s.V1Volume(
                name=f'workflow-shared-storage-volume-{self.task_id_replaced}'[0:63], # max resource name in k8s is 63 chars
                empty_dir=k8s.V1EmptyDirVolumeSource()
            )
        )
        pod_cp = copy.deepcopy(pod)
        pod_cp.spec.volumes = pod.spec.volumes or []
        pod_cp.spec.volumes.extend(pod_volumes_list)
        pod_cp.spec.containers[0].volume_mounts = pod_cp.spec.containers[0].volume_mounts or []
        pod_cp.spec.containers[0].volume_mounts.extend(volume_mounts_main_container)

        # Create and add sidecar container to pod
        storage_piece_secrets = {}
        if self.workflow_shared_storage.source != "local":
            storage_piece_secrets = self._get_piece_secrets(
                repository_url="starflow-default/default_storage_repository",
                repository_version="0.0.1",
                piece_name=self.workflow_shared_storage.storage_piece_name,
                source='default',
            )
        if not self._validate_storage_piece_secrets(storage_piece_secrets):
            self.logger.error("Invalid storage piece secrets. Aborting pod creation.")
            raise Exception("Invalid storage piece secrets. Aborting pod creation.")

        self.workflow_shared_storage.source = self.workflow_shared_storage.source.name
        sidecar_env_vars = {
            'STARFLOW_WORKFLOW_SHARED_STORAGE': self.workflow_shared_storage.model_dump_json() if self.workflow_shared_storage else "",
            'STARFLOW_WORKFLOW_SHARED_STORAGE_SECRETS': str(storage_piece_secrets),
            'STARFLOW_INSTANTIATE_PIECE_KWARGS': str({
                "deploy_mode": self.deploy_mode,
                "task_id": self.task_id,
                "dag_id": self.dag_id,
            }),
            'STARFLOW_WORKFLOW_RUN_SUBPATH': self.workflow_run_subpath,
            'AIRFLOW_UPSTREAM_TASKS_IDS_SHARED_STORAGE': str(self.shared_storage_upstream_ids_list),
        }
        self.shared_storage_sidecar_container_name = f"starflow-shared-storage-sidecar-{self.task_id_replaced}"[0:63]
        sidecar_container = k8s.V1Container(
            name=self.shared_storage_sidecar_container_name,
            command=['bash', '-c', './sidecar_lifecycle.sh'],
            image='ghcr.io/prochain-star-atlas/starflow-shared-storage-sidecar:latest',
            volume_mounts=volume_mounts_sidecar_container,
            security_context=k8s.V1SecurityContext(privileged=True),
            env=[k8s.V1EnvVar(name=k, value=v) for k, v in sidecar_env_vars.items()],
            resources=k8s.V1ResourceRequirements(
                requests={
                    "cpu": "1m",
                    "memory": "128Mi",
                },
                limits={
                    "cpu": "1000m",
                    "memory": "1024Mi",
                }
            ),
        )
        pod_cp.spec.containers.append(sidecar_container)
        return pod_cp

    def _get_piece_secrets(
        self,
        repository_url: str,
        repository_version: str,
        piece_name: str,
        source: str = 'github'
    ) -> Dict[str, Any]:
        """Get piece secrets values from starflow API"""
        params = {
            "workspace_id": self.workspace_id,
            "url": repository_url,
            "version": repository_version,
            'source': source,
            "page": 0,
            "page_size": 1,
        }
        piece_repository_data = self.starflow_client.get_piece_repositories_from_workspace_id(
            params=params
        ).json()
        
        # Check if any piece repositories were found
        if not piece_repository_data.get("data") or len(piece_repository_data["data"]) == 0:
            return {}
        
        secrets_response = self.starflow_client.get_piece_secrets(
            piece_repository_id=piece_repository_data["data"][0]["id"],
            piece_name=piece_name
        )
        if secrets_response.status_code != 200:
            raise Exception(f"Error getting piece secrets: {secrets_response.json()}")

        piece_secrets = {}
        for e in secrets_response.json():
            if not e.get('value') and not e.get('required'):
                continue
            piece_secrets[e.get('name')] = e.get('value')
        return piece_secrets


    @staticmethod
    def _get_upstream_xcom_data_from_task_ids(task_ids: list, context: Context):
        upstream_xcoms_data = dict()
        for tid in task_ids:
            upstream_xcoms_data[tid] = context['ti'].xcom_pull(task_ids=tid)
        return upstream_xcoms_data

    def _get_piece_kwargs_value_from_upstream_xcom(
        self,
        value: Any
    ):
        if isinstance(value, dict) and value.get("type") == "fromUpstream":
            upstream_task_id = value["upstream_task_id"]
            output_arg = value["output_arg"]
            if upstream_task_id not in self.shared_storage_upstream_ids_list:
                self.shared_storage_upstream_ids_list.append(upstream_task_id)
            return self.upstream_xcoms_data[upstream_task_id][output_arg]
        elif isinstance(value, list):
            return [self._get_piece_kwargs_value_from_upstream_xcom(item) for item in value]
        elif isinstance(value, dict):
            return {
                k: self._get_piece_kwargs_value_from_upstream_xcom(v)
                for k, v in value.items()
            }
        return value

    def _update_piece_kwargs_with_upstream_xcom(self):
        self.shared_storage_upstream_ids_list = list()
        if not self.piece_input_kwargs:
            self.piece_input_kwargs = dict()

        updated_piece_kwargs = {
            k: self._get_piece_kwargs_value_from_upstream_xcom(
                value=v
            ) for k, v in self.piece_input_kwargs.items()
        }
        self.piece_input_kwargs = updated_piece_kwargs
        self.env_vars.append({
            'name': 'AIRFLOW_UPSTREAM_TASKS_IDS_SHARED_STORAGE',
            'value': str(self.shared_storage_upstream_ids_list),
            'value_from': None
        })

    def _update_env_var_value_from_name(self, name: str, value: str):
        for env_var in self.env_vars:
            if env_var.name == name:
                env_var.value = value
                break


    def _prepare_execute_environment(self, context: Context):
        """
        Runs at the begining of the execute method.
        Pass extra arguments and configuration as environment variables to the pod
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Fetch upstream tasks ids and save them in an ENV var
        # Check if operator is properly assigned to a DAG
        try:
            # Try to access the dag property - this will raise RuntimeError if not assigned
            dag = self.dag
            if dag is None:
                logger.warning("[StarflowK8sBranchOperator] Operator DAG is None, skipping upstream task IDs")
                upstream_task_ids = []
            else:
                upstream_task_ids = [t.task_id for t in self.get_direct_relatives(upstream=True)]
                logger.info(f"[StarflowK8sBranchOperator] Upstream task IDs: {upstream_task_ids}")
        except RuntimeError as e:
            if "has not been assigned to a DAG yet" in str(e):
                logger.warning("[StarflowK8sBranchOperator] Operator not assigned to a DAG, skipping upstream task IDs")
                upstream_task_ids = []
            else:
                raise
        self.env_vars.append({
            'name': 'AIRFLOW_UPSTREAM_TASKS_IDS',
            'value': str(upstream_task_ids),
            'value_from': None
        })
        # Pass forward the workflow shared storage source name
        self.env_vars.append({
            'name': 'STARFLOW_WORKFLOW_SHARED_STORAGE_SOURCE_NAME',
            'value': str(self.workflow_shared_storage.source.name) if self.workflow_shared_storage else None,
            'value_from': None
        })
        # Save updated piece input kwargs with upstream data to environment variable
        self.upstream_xcoms_data = self._get_upstream_xcom_data_from_task_ids(task_ids=upstream_task_ids, context=context)
        self._update_piece_kwargs_with_upstream_xcom()
        self._update_env_var_value_from_name(name='STARFLOW_RUN_PIECE_KWARGS', value=str(self.piece_input_kwargs))

        # # Add pieces secrets to environment variables
        # piece_secrets = self._get_piece_secrets(
        #     repository_url=self.repository_url,
        #     repository_version=self.repository_version,
        #     piece_name=self.piece_name,
        # )
        # self.env_vars.append({
        #     "name": "STARFLOW_PIECE_SECRETS",
        #     "value": str(piece_secrets),
        #     "value_from": None
        # })

        # Include workflow run subpath from dag run id, taken from context
        dag_id = context["dag_run"].dag_id
        dag_run_id = context['run_id']
        dag_run_id_path = dag_run_id.replace("-", "_").replace(".", "_").replace(" ", "_").replace(":", "_").replace("+", "_")
        self.workflow_run_subpath = f"{dag_id}/{dag_run_id_path}"
        self.env_vars.append({
            'name': 'STARFLOW_WORKFLOW_RUN_SUBPATH',
            'value': self.workflow_run_subpath,
            'value_from': None
        })
        self.env_vars.append({
            'name': 'OPEN_ID_USERNAME_TARGET',
            'value': str(self.username_var),
            'value_from': None
        })


    def execute(self, context: Context):
        """
        Code from here onward is executed by the Worker and not by the Scheduler.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Log at the very beginning to confirm execute method is called
        logger.info("=" * 80)
        logger.info(f"[StarflowK8sBranchOperator] EXECUTE METHOD CALLED - task_id: {self.task_id}")
        logger.info(f"[StarflowK8sBranchOperator] Context type: {type(context)}")
        logger.info(f"[StarflowK8sBranchOperator] Context keys: {list(context.keys()) if hasattr(context, 'keys') else 'No keys method'}")
        logger.info("=" * 80)
        
        try:
            logger.info(f"[StarflowK8sBranchOperator] Starting execution for task_id: {self.task_id}")
            
            # Initialize remote_pod early to avoid UnboundLocalError in finally block
            remote_pod = None
            
            # TODO change url based on platform configuration
            logger.info("[StarflowK8sBranchOperator] Initializing Starflow backend client...")
            self.starflow_client = starflowBackendRestClient(base_url="http://starflow-rest-service.starflow:8000/")
            logger.info("[StarflowK8sBranchOperator] Starflow backend client initialized successfully")
            
            logger.info("[StarflowK8sBranchOperator] Preparing execute environment...")
            self._prepare_execute_environment(context=context)
            logger.info("[StarflowK8sBranchOperator] Execute environment prepared successfully")
            logger.info("[StarflowK8sBranchOperator] Building pod request object...")
            self.pod_request_obj = self.build_pod_request_obj(context)
            logger.info("[StarflowK8sBranchOperator] Pod request object built successfully")
            
            logger.info("[StarflowK8sBranchOperator] Creating/getting pod...")
            self.pod = self.get_or_create_pod(  # must set `self.pod` for `on_kill`
                pod_request_obj=self.pod_request_obj,
                context=context,
            )
            logger.info(f"[StarflowK8sBranchOperator] Pod created successfully: {self.pod.metadata.name}")
            
            # get remote pod for use in cleanup methods
            logger.info("[StarflowK8sBranchOperator] Finding remote pod...")
            remote_pod = self.find_pod(self.pod.metadata.namespace, context=context)
            logger.info("[StarflowK8sBranchOperator] Remote pod found successfully")
            
            logger.info("[StarflowK8sBranchOperator] Awaiting pod start...")
            self.await_pod_start(pod=self.pod)
            logger.info("[StarflowK8sBranchOperator] Pod started successfully")

            if self.get_logs:
                self.pod_manager.fetch_container_logs(
                    pod=self.pod,
                    container_name=self.BASE_CONTAINER_NAME,
                    follow=True,
                )
            else:
                self.pod_manager.await_container_completion(
                    pod=self.pod, container_name=self.BASE_CONTAINER_NAME
                )

            if self.do_xcom_push:
                result = self.extract_xcom(pod=self.pod)

                print(result)

                if "branch_main" in result and result['branch_main'] == True:
                    self.isMainBranchSelected = True
                else: 
                    self.isMainBranchSelected = False

            if self.workflow_shared_storage and self.workflow_shared_storage.mode.name != 'none':
                self._kill_shared_storage_sidecar(pod=self.pod)
            remote_pod = self.pod_manager.await_pod_completion(self.pod)
        finally:
            self.cleanup(
                pod=self.pod or self.pod_request_obj,
                remote_pod=remote_pod,
            )
        ti = context['ti']
        ti.xcom_push(key='pod_name', value=self.pod.metadata.name)
        ti.xcom_push(key='pod_namespace', value=self.pod.metadata.namespace)

        self._shared_storage_usage_in_bytes = result.get('_shared_storage_usage_in_bytes', 0)

        return BaseBranchOperator.execute(self, context)



    def _kill_shared_storage_sidecar(self, pod: k8s.V1Pod):
        """
        This method is used to send a signal to stop and delete the sidecar container with the shared storage mounts.
        """
        with closing(
            kubernetes_stream(
                self.pod_manager._client.connect_get_namespaced_pod_exec,
                pod.metadata.name,
                pod.metadata.namespace,
                container=self.shared_storage_sidecar_container_name,
                command=['/bin/bash'],
                stdin=True,
                stdout=True,
                stderr=True,
                tty=False,
                _preload_content=False,
            )
        ) as resp:
            self.log.info('Sending signal to unmount shared storage sidecar container')
            self.pod_manager._exec_pod_command(resp, 'python mount.py unmount')
            self.log.info('Sending signal to delete shared storage sidecar container')
            self.pod_manager._exec_pod_command(resp, 'kill -s SIGINT 1')

    def extract_xcom(self, pod: k8s.V1Pod):
        """Retrieves xcom value and kills xcom sidecar container"""
        result = self.pod_manager_extract_xcom(pod)
        if isinstance(result, str) and result.rstrip() == "__airflow_xcom_result_empty__":
            self.log.info("Result file is empty.")
            return None
        else:
            self.log.info('xcom result is not empty, parsing to json')
            return json.loads(result)

    def pod_manager_extract_xcom(self, pod: k8s.V1Pod) -> str:
        client = kubernetes_stream(
            self.pod_manager._client.connect_get_namespaced_pod_exec,
            pod.metadata.name,
            pod.metadata.namespace,
            container=PodDefaults.SIDECAR_CONTAINER_NAME,
            command=[
                '/bin/sh',
                '-c',
                f"if [ -s {PodDefaults.XCOM_MOUNT_PATH}/return.json ]; then cat {PodDefaults.XCOM_MOUNT_PATH}/return.json; else echo __airflow_xcom_result_empty__; fi",
            ],
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
            _preload_content=False,
            _request_timeout=10,
        )
        client.run_forever(timeout=10)
        result = client.read_all()

        _ = kubernetes_stream(
            self.pod_manager._client.connect_get_namespaced_pod_exec,
            pod.metadata.name,
            pod.metadata.namespace,
            container=PodDefaults.SIDECAR_CONTAINER_NAME,
            command=[
                '/bin/sh',
                '-c',
                'kill -s SIGINT 1',
            ],
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
            _preload_content=True,
            _request_timeout=10,
        )
        client.close()

        if result is None:
            raise AirflowException(f"Failed to extract xcom from pod: {pod.metadata.name}")

        return result



