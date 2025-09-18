import os
import tomli
import tomli_w
import yaml
import subprocess
import re
import shutil
import requests
import time
from concurrent.futures import ThreadPoolExecutor
import base64
from pathlib import Path
from rich.console import Console
from yaml.resolver import BaseResolver
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from tempfile import NamedTemporaryFile, TemporaryDirectory
from kubernetes import client, config

from starflow.cli.utils.constants import COLOR_PALETTE, STARFLOW_HELM_PATH, STARFLOW_HELM_VERSION, STARFLOW_HELM_REPOSITORY


class AsLiteral(str):
    pass


def represent_literal(dumper, data):
    return dumper.represent_scalar(BaseResolver.DEFAULT_SCALAR_TAG, data, style="|")


yaml.add_representer(AsLiteral, represent_literal)


console = Console()


def create_ssh_pair_key() -> None:
    # Create SSH key pair for GitHub Workflows
    console.print("Generating SSH key pair for GitHub Workflows...")
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=4096
    )

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption()
    )
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    )
    return private_key, public_key


def prepare_platform(
    cluster_name: str,
    workflows_repository: str,
    github_workflows_ssh_private_key: str,
    github_default_pieces_repository_token: str,
    github_workflows_token: str,
    deploy_mode: str,
    local_pieces_repository_path: list,
    local_starflow_path: str,
    local_rest_image: str,
    local_frontend_image: str,
    local_airflow_image: str,
) -> None:
    # Create local configuration file updated with user-provided arguments
    config_file_path = Path(__file__).resolve().parent / "config-starflow-local.toml"
    with open(str(config_file_path), "rb") as f:
        config_dict = tomli.load(f)

    running_path = str(Path().cwd().resolve())
    config_dict["path"]["STARFLOW_LOCAL_RUNNING_PATH"] = running_path
    config_dict["kind"]["STARFLOW_KIND_CLUSTER_NAME"] = cluster_name
    config_dict['kind']['STARFLOW_DEPLOY_MODE'] = deploy_mode

    if deploy_mode == 'local-k8s-dev':
        config_dict['dev']['STARFLOW_AIRFLOW_IMAGE'] = local_airflow_image
        config_dict['dev']['STARFLOW_REST_IMAGE'] = local_rest_image
        config_dict['dev']['STARFLOW_FRONTEND_IMAGE'] = local_frontend_image
        config_dict['dev']['STARFLOW_LOCAL_STARFLOW_PACKAGE'] = local_starflow_path
        for local_pieces_repository in local_pieces_repository_path:
            # Read repo config.toml to get repo name to map it to cluster path
            repo_config_file_path = Path(local_pieces_repository).resolve() / "config.toml"
            with open(str(repo_config_file_path), "rb") as f:
                repo_toml = tomli.load(f)

            repo_name = repo_toml['repository']['REPOSITORY_NAME']
            config_dict['dev'][repo_name] = local_pieces_repository

    config_dict['github']['STARFLOW_GITHUB_WORKFLOWS_REPOSITORY'] = workflows_repository.split("github.com/")[-1].strip('/')

    if not github_workflows_ssh_private_key:
        private_key, public_key = create_ssh_pair_key()
        config_dict["github"]["STARFLOW_GITHUB_WORKFLOWS_SSH_PRIVATE_KEY"] = base64.b64encode(private_key).decode('utf-8')
        config_dict["github"]["STARFLOW_GITHUB_WORKFLOWS_SSH_PUBLIC_KEY"] = public_key.decode("utf-8")
    else:
        config_dict["github"]["STARFLOW_GITHUB_WORKFLOWS_SSH_PRIVATE_KEY"] = github_workflows_ssh_private_key

    config_dict['github']['STARFLOW_GITHUB_ACCESS_TOKEN_WORKFLOWS'] = github_workflows_token
    config_dict['github']['STARFLOW_DEFAULT_PIECES_REPOSITORY_TOKEN'] = github_default_pieces_repository_token

    with open("config-starflow-local.toml", "wb") as f:
        tomli_w.dump(config_dict, f)

    console.print("")
    console.print(f"starflow is prepared to run at: {running_path}")
    console.print(f"You can check and modify the configuration file at: {running_path}/config-starflow-local.toml")
    console.print("Next, run: `starflow platform create`")
    console.print("")


def create_platform(install_airflow: bool = True, use_gpu: bool = False) -> None:
    # Load configuration values
    with open("config-starflow-local.toml", "rb") as f:
        platform_config = tomli.load(f)

    # Create kind config file and run bash script to create Kind cluster
    kubeadm_config_patches = dict(
        kind="InitConfiguration",
        nodeRegistration=dict(
            kubeletExtraArgs={
                "node-labels": "ingress-ready=true"
            }
        )
    )
    extra_mounts_local_repositories = []

    starflow_dev_private_variables_list = [
        "STARFLOW_LOCAL_STARFLOW_PACKAGE",
        "STARFLOW_REST_IMAGE",
        "STARFLOW_FRONTEND_IMAGE",
        "STARFLOW_AIRFLOW_IMAGE"
    ]
    local_pieces_respositories = {key: value for key, value in platform_config['dev'].items() if key not in starflow_dev_private_variables_list}
    if platform_config['kind']['STARFLOW_DEPLOY_MODE'] == 'local-k8s-dev':
        for repo_name, repo_path in local_pieces_respositories.items():
            extra_mounts_local_repositories.append(
                dict(
                    hostPath=repo_path,
                    containerPath=f"/pieces_repositories/{repo_name}",
                    readOnly=True,
                    propagation='HostToContainer'
                )
            )
        if platform_config['dev'].get('STARFLOW_LOCAL_STARFLOW_PACKAGE'):
            starflow_local_package_absolute_path = Path(platform_config['dev']['STARFLOW_LOCAL_STARFLOW_PACKAGE']).resolve()
            extra_mounts_local_repositories.append(
                dict(
                    hostPath=str(starflow_local_package_absolute_path),
                    containerPath=f"/starflow/starflow_py/src/starflow",
                    readOnly=True,
                    propagation='HostToContainer'
                )
            )

    kubeadm_parsed = AsLiteral(yaml.dump(kubeadm_config_patches))
    use_gpu_dict = {} if not use_gpu else {"gpus": True}
    kind_config = dict(
        kind="Cluster",
        apiVersion="kind.x-k8s.io/v1alpha4",
        nodes=[
            dict(
                role="control-plane",
                kubeadmConfigPatches=[kubeadm_parsed],
                extraPortMappings=[
                    dict(
                        containerPort=80,
                        hostPort=80,
                        listenAddress="0.0.0.0",
                        protocol="TCP"
                    ),
                    dict(
                        containerPort=443,
                        hostPort=443,
                        listenAddress="0.0.0.0",
                        protocol="TCP"
                    )
                ]
            ),
            dict(
                role="worker",
                extraMounts=[
                    dict(
                        hostPath=platform_config["path"]["STARFLOW_LOCAL_RUNNING_PATH"] + "/workflow_shared_storage",
                        containerPath="/cluster_shared_storage",
                        readOnly=False,
                        propagation="Bidirectional"
                    ),
                    *extra_mounts_local_repositories
                ],
                **use_gpu_dict
            ),
        ]
    )
    with open("kind-cluster-config.yaml", "w") as f:
        yaml.dump(kind_config, f)

    cluster_name = platform_config["kind"]["STARFLOW_KIND_CLUSTER_NAME"]

    # Delete previous Kind cluster
    console.print("")
    console.print(f"Removing previous Kind cluster - {cluster_name}...")
    result = subprocess.run(["kind", "delete", "cluster", "--name", cluster_name], capture_output=True, text=True)
    if result.returncode != 0:
        error_message = result.stderr.strip() if result.stderr else result.stdout.strip()
        raise Exception(f"An error occurred while deleting previous Kind cluster - {cluster_name}: {error_message}")
    console.print("")

    # Create new Kind cluster
    console.print(f"Creating new Kind cluster - {cluster_name}...")
    result = subprocess.run(["kind", "create", "cluster", "--name", cluster_name, "--config", "kind-cluster-config.yaml"])
    if result.returncode != 0:
        error_message = result.stderr.strip() if result.stderr else result.stdout.strip()
        raise Exception(f"An error occurred while creating Kind cluster - {cluster_name}: {error_message}")
    console.print("")
    console.print("Kind cluster created successfully!", style=f"bold {COLOR_PALETTE.get('success')}")

    # Install Ingress NGINX controller
    console.print("")
    console.print("Installing NGINX controller...")
    subprocess.run(["kubectl", "apply", "-f", "https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml"], stdout=subprocess.DEVNULL)
    result = subprocess.run(["kubectl", "wait", "--namespace", "ingress-nginx", "--for", "condition=ready", "pod", "--selector=app.kubernetes.io/component=controller", "--timeout=660s"])
    if result.returncode != 0:
        error_message = result.stderr.strip() if result.stderr else result.stdout.strip()
        raise Exception("An error occurred while installing NGINX controller: {error_message}")
    console.print("NGINX controller installed successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
    console.print("")

    # Load local images to Kind cluster
    local_starflow_airflow_image = platform_config.get('dev', {}).get('STARFLOW_AIRFLOW_IMAGE', None)
    local_starflow_frontend_image = platform_config.get('dev', {}).get('STARFLOW_FRONTEND_IMAGE', None)
    local_starflow_rest_image = platform_config.get('dev', {}).get('STARFLOW_REST_IMAGE', None)

    starflow_airflow_image_tag = 'latest'
    starflow_airflow_image = "ghcr.io/prochain-star-atlas/starflow-airflow-base"
    if local_starflow_airflow_image:
        console.print(f"Loading local starflow Airflow image {local_starflow_airflow_image} to Kind cluster...")
        subprocess.run(["kind", "load", "docker-image", local_starflow_airflow_image , "--name", cluster_name, "--nodes", f"{cluster_name}-worker"])
        starflow_airflow_image = f'docker.io/library/{local_starflow_airflow_image}'
    elif platform_config['kind']["STARFLOW_DEPLOY_MODE"] == 'local-k8s-dev' and not local_starflow_airflow_image:
        starflow_airflow_image_tag = 'latest-dev'

    if local_starflow_frontend_image:
        console.print(f"Loading local frontend image {local_starflow_frontend_image} to Kind cluster...")
        subprocess.run(["kind", "load", "docker-image", local_starflow_frontend_image , "--name", cluster_name, "--nodes", f"{cluster_name}-worker"])
        starflow_frontend_image = f"docker.io/library/{local_starflow_frontend_image}"
    elif platform_config['kind']["STARFLOW_DEPLOY_MODE"] == 'local-k8s-dev':
        starflow_frontend_image = "ghcr.io/prochain-star-atlas/starflow-frontend:k8s-dev"
    else:
        starflow_frontend_image = "ghcr.io/prochain-star-atlas/starflow-frontend:k8s"

    if local_starflow_rest_image:
        console.print(f"Loading local REST image {local_starflow_rest_image} to Kind cluster...")
        subprocess.run(["kind", "load", "docker-image", local_starflow_rest_image , "--name", cluster_name, "--nodes", f"{cluster_name}-worker"])
        starflow_rest_image = f'docker.io/library/{local_starflow_rest_image}'
    elif platform_config['kind']["STARFLOW_DEPLOY_MODE"] == 'local-k8s-dev':
        starflow_rest_image = "ghcr.io/prochain-star-atlas/starflow-rest:latest-dev"
    else:
        starflow_rest_image = "ghcr.io/prochain-star-atlas/starflow-rest:latest"

    # In order to use nvidia gpu in our cluster we need nvidia plugins to be installed.
    # We can use nvidia operator to install nvidia plugins.
    # References:
    #     https://catalog.ngc.nvidia.com/orgs/nvidia/containers/gpu-operator
    #     https://jacobtomlinson.dev/posts/2022/quick-hack-adding-gpu-support-to-kind/
    if use_gpu:
        console.print("Installing NVIDIA GPU Operator...")
        nvidia_gpu_operator_add_repo_command = [
            "helm", "repo", "add", "nvidia", "https://nvidia.github.io/gpu-operator",
        ]
        subprocess.run(nvidia_gpu_operator_add_repo_command)
        helm_update_command = ["helm", "repo", "update"]
        subprocess.run(helm_update_command)

        # We don't need driver as we are using kind and our host machine already has nvidia driver that is why we are disabling it.
        nvidia_plugis_install_command = "helm install --wait --generate-name -n gpu-operator --create-namespace nvidia/gpu-operator --set driver.enabled=false"
        subprocess.run(nvidia_plugis_install_command, shell=True)


    # Override values for starflow Helm chart
    db_enabled = platform_config['starflow_db'].get("STARFLOW_CREATE_DATABASE", True)
    token_pieces = platform_config["github"]["STARFLOW_DEFAULT_PIECES_REPOSITORY_TOKEN"]
    token_workflows = platform_config["github"]["STARFLOW_GITHUB_ACCESS_TOKEN_WORKFLOWS"]
    starflow_values_override_config = {
        "github_access_token_pieces": token_pieces,
        "github_access_token_workflows": token_workflows,
        "frontend": {
            "enabled": True,
            "image": starflow_frontend_image,
            "apiEnv": "dev" if platform_config['kind']["STARFLOW_DEPLOY_MODE"] in ['local-k8s-dev', 'local-k8s'] else 'prod',
            "deployMode": platform_config['kind']["STARFLOW_DEPLOY_MODE"],
        },
        "rest": {
            "enabled": True,
            "image": starflow_rest_image,
            "workflowsRepository": platform_config['github']['STARFLOW_GITHUB_WORKFLOWS_REPOSITORY'],
            "createDefaultUser": platform_config['starflow_db'].get('STARFLOW_CREATE_DEFAULT_USER', True)
        },
        "database": {
            "enabled": db_enabled,
            "image": "postgres:13",
            "name": "postgres",
            "user": "postgres",
            "password": "postgres",
            "port": "5432",
        }
    }

    # Only add database values if database is enabled
    # If not enabled will use always the default values
    if not db_enabled:
        starflow_values_override_config['database'] = {
            **starflow_values_override_config['database'],
            "host": platform_config['starflow_db']["STARFLOW_DB_HOST"],
            "name":  platform_config['starflow_db']["STARFLOW_DB_NAME"],
            "user": platform_config['starflow_db']["STARFLOW_DB_USER"],
            "password": platform_config['starflow_db']["STARFLOW_DB_PASSWORD"],
            "port": str(platform_config['starflow_db'].get("STARFLOW_DB_PORT", 5432))
        }

    # Override values for Airflow Helm chart
    airflow_ssh_config = dict(
        gitSshKey=f"{platform_config['github']['STARFLOW_GITHUB_WORKFLOWS_SSH_PRIVATE_KEY']}",
    )
    airflow_ssh_config_parsed = AsLiteral(yaml.dump(airflow_ssh_config))

    workers_extra_volumes = []
    workers_extra_volumes_mounts = []
    workers = {}
    scheduler = {}
    if platform_config['kind']["STARFLOW_DEPLOY_MODE"] == 'local-k8s-dev' and platform_config['dev'].get('STARFLOW_LOCAL_STARFLOW_PACKAGE'):
        workers_extra_volumes = [
            {
                "name": "starflow-dev-extra",
                "persistentVolumeClaim": {
                    "claimName": "starflow-dev-volume-claim"
                }
            }
        ]
        workers_extra_volumes_mounts = [
            {
                "name": "starflow-dev-extra",
                "mountPath": "/opt/airflow/starflow/starflow_py/src/starflow"
            }
        ]
        workers = {
            "workers": {
                "extraVolumes": workers_extra_volumes,
                "extraVolumeMounts": workers_extra_volumes_mounts,
            }
        }
        scheduler = {
            "scheduler": {
                "extraVolumes": workers_extra_volumes,
                "extraVolumeMounts": workers_extra_volumes_mounts,
            }
        }

    airflow_values_override_config = {
        "env": [
            {
                "name": "STARFLOW_DEPLOY_MODE",
                "value": platform_config['kind']["STARFLOW_DEPLOY_MODE"]
            },
        ],
        "images": {
            "useDefaultImageForMigration": False,
            "airflow": {
                "repository": starflow_airflow_image,
                "tag": starflow_airflow_image_tag,
                "pullPolicy": "IfNotPresent"
            }
        },
        "extraSecrets": {
            "airflow-ssh-secret": {
                "data": airflow_ssh_config_parsed
            }
        },
        "config": {
            "api": {
                "auth_backends": "airflow.api.auth.backend.basic_auth"
            },
        },
        "dags": {
            "gitSync": {
                "enabled": True,
                "wait": 60,
                "repo": f"ssh://git@github.com/{platform_config['github']['STARFLOW_GITHUB_WORKFLOWS_REPOSITORY']}.git",
                "branch": "main",
                "subPath": "workflows",
                "sshKeySecret": "airflow-ssh-secret"
            },
        },
        "migrateDatabaseJob": {
            "jobAnnotations": {
                "sidecar.istio.io/inject": "false"
            },
            "annotations": {
                "sidecar.istio.io/inject": "false"
            },
        },
        "createUserJob": {
            "jobAnnotations": {
                "sidecar.istio.io/inject": "false"
            },
            "annotations": {
                "sidecar.istio.io/inject": "false"
            },
        },
        **workers,
        **scheduler,
    }

    # Update Helm repositories
    subprocess.run(["helm", "repo", "add", "starflow", STARFLOW_HELM_REPOSITORY])
    subprocess.run(["helm", "repo", "add", "apache-airflow", "https://airflow.apache.org/"])  # ref: https://github.com/helm/helm/issues/8036
    subprocess.run(["helm", "repo", "update"])

    # Install Airflow Helm Chart
    if install_airflow:
        console.print('Installing Apache Airflow...')
        # Create temporary file with airflow values
        with NamedTemporaryFile(suffix='.yaml', mode="w") as fp:
            yaml.dump(airflow_values_override_config, fp)
            commands = [
                "helm", "install",
                "-f", str(fp.name),
                "airflow",
                "apache-airflow/airflow",
                "--version", " 1.11.0",
            ]
            subprocess.run(commands)

    # Install starflow Helm Chart
    local_starflow_path = platform_config.get('dev', {}).get('STARFLOW_LOCAL_STARFLOW_PACKAGE')
    if platform_config.get('kind', {}).get('STARFLOW_DEPLOY_MODE') == 'local-k8s-dev' and local_starflow_path:
        console.print('Installing starflow using local helm...')
        helm_starflow_path = Path(local_starflow_path).parent.parent / "helm/starflow"
        with NamedTemporaryFile(suffix='.yaml', mode="w") as fp:
            yaml.dump(starflow_values_override_config, fp)
            commands = [
                "helm", "install",
                "-f", str(fp.name),
                "starflow",
                helm_starflow_path
            ]
            subprocess.run(commands)
    else:
        console.print('Installing starflow using remote helm...')
        with TemporaryDirectory() as tmp_dir:
            console.print("Downloading starflow Helm chart...")
            subprocess.run([
                "helm",
                "pull",
                STARFLOW_HELM_PATH,
                "--untar",
                "-d",
                tmp_dir
            ])
            with NamedTemporaryFile(suffix='.yaml', mode="w") as fp:
                yaml.dump(starflow_values_override_config, fp)
                console.print('Installing starflow...')
                commands = [
                    "helm", "install",
                    "-f", str(fp.name),
                    "starflow",
                    f"{tmp_dir}/starflow",
                ]
                subprocess.run(commands)

    # For each path create a pv and pvc
    if platform_config['kind']['STARFLOW_DEPLOY_MODE'] == 'local-k8s-dev':
        config.load_kube_config()
        k8s_client = client.CoreV1Api()
        v1 = client.RbacAuthorizationV1Api()

        # Create service account role binding with admin access for airflow worker
        role_binding_name_worker = "full-access-user-clusterrolebinding-worker"
        sa_name = "airflow-worker"
        cluster_role_binding_worker = client.V1ClusterRoleBinding(
            metadata=client.V1ObjectMeta(name=role_binding_name_worker),
            subjects=[
                client.V1Subject(
                    kind="ServiceAccount",
                    name=sa_name,
                    namespace="default"
                )
            ],
            role_ref=client.V1RoleRef(
                kind="ClusterRole",
                name="cluster-admin",
                api_group="rbac.authorization.k8s.io"
            )
        )
        console.print('Creating RBAC Worker Authorization for local dev')
        v1.create_cluster_role_binding(cluster_role_binding_worker)

        role_binding_name_scheduler = "full-access-user-clusterrolebinding-scheduler"
        sa_name = "airflow-scheduler"
        cluster_role_binding_scheduler = client.V1ClusterRoleBinding(
            metadata=client.V1ObjectMeta(name=role_binding_name_scheduler),
            subjects=[
                client.V1Subject(
                    kind="ServiceAccount",
                    name=sa_name,
                    namespace="default"
                )
            ],
            role_ref=client.V1RoleRef(
                kind="ClusterRole",
                name="cluster-admin",
                api_group="rbac.authorization.k8s.io"
            )
        )
        console.print('Creating RBAC Scheduler Authorization for local dev')
        v1.create_cluster_role_binding(cluster_role_binding_scheduler)

        for project_name in local_pieces_respositories.keys():
            console.log(f"Creating PV and PVC for {project_name}...")
            # Check if pv already exists
            persistent_volume_name = 'pv-{}'.format(str(project_name.lower().replace('_', '-')))
            persistent_volume_claim_name = 'pvc-{}'.format(str(project_name.lower().replace('_', '-')))
            pvc_exists = False
            try:
                k8s_client.read_namespaced_persistent_volume_claim(name=persistent_volume_claim_name, namespace='default')
                pvc_exists = True
            except client.rest.ApiException as e:
                if e.status != 404:
                    raise e

            if not pvc_exists:
                pvc = client.V1PersistentVolumeClaim(
                    metadata=client.V1ObjectMeta(name=persistent_volume_claim_name),
                    spec=client.V1PersistentVolumeClaimSpec(
                        access_modes=["ReadOnlyMany"],
                        volume_name=persistent_volume_name,
                        resources=client.V1ResourceRequirements(
                            requests={"storage": "300Mi"}
                        ),
                        storage_class_name="standard"
                    )
                )
                k8s_client.create_namespaced_persistent_volume_claim(namespace="default", body=pvc)

            pv_exists = False
            try:
                k8s_client.read_persistent_volume(name=persistent_volume_name)
                pv_exists = True
            except client.rest.ApiException as e:
                if e.status != 404:
                    raise e

            if not pv_exists:
                pv = client.V1PersistentVolume(
                    metadata=client.V1ObjectMeta(name=persistent_volume_name),
                    spec=client.V1PersistentVolumeSpec(
                        access_modes=["ReadWriteOnce"],
                        capacity={"storage": "1Gi"},
                        persistent_volume_reclaim_policy="Retain",
                        storage_class_name="standard",
                        host_path=client.V1HostPathVolumeSource(path=f"/pieces_repositories/{project_name}"),
                        claim_ref=client.V1ObjectReference(
                            namespace="default",
                            name=persistent_volume_claim_name,
                            kind="PersistentVolumeClaim"
                        ),
                        node_affinity=client.V1VolumeNodeAffinity(
                            required=client.V1NodeSelector(
                                node_selector_terms=[
                                    client.V1NodeSelectorTerm(
                                        match_expressions=[
                                            client.V1NodeSelectorRequirement(
                                                key="kubernetes.io/hostname",
                                                operator="In",
                                                values=["starflow-cluster-worker"]
                                            )
                                        ]
                                    )
                                ]
                            )
                        )
                    )
                )
                k8s_client.create_persistent_volume(body=pv)

        if platform_config['dev'].get('STARFLOW_LOCAL_STARFLOW_PACKAGE'):
            console.print("Creating PV's and PVC's for Local starflow Package...")
            # Create pv and pvc for local dev starflow
            pvc = client.V1PersistentVolumeClaim(
                metadata=client.V1ObjectMeta(name="starflow-dev-volume-claim"),
                spec=client.V1PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteMany"],
                    volume_name="starflow-dev-volume",
                    resources=client.V1ResourceRequirements(
                        requests={"storage": "300Mi"}
                    ),
                    storage_class_name="standard"
                )
            )
            k8s_client.create_namespaced_persistent_volume_claim(namespace="default", body=pvc)
            pv = client.V1PersistentVolume(
                metadata=client.V1ObjectMeta(name="starflow-dev-volume"),
                spec=client.V1PersistentVolumeSpec(
                    storage_class_name="standard",
                    access_modes=["ReadWriteMany"],
                    capacity={"storage": "2Gi"},
                    host_path=client.V1HostPathVolumeSource(path="/starflow/starflow_py/src/starflow"),
                    claim_ref=client.V1ObjectReference(
                        namespace="default",
                        name="starflow-dev-volume-claim",
                    ),
                    node_affinity=client.V1VolumeNodeAffinity(
                        required=client.V1NodeSelector(
                            node_selector_terms=[
                                client.V1NodeSelectorTerm(
                                    match_expressions=[
                                        client.V1NodeSelectorRequirement(
                                            key="kubernetes.io/hostname",
                                            operator="In",
                                            values=["starflow-cluster-worker"]
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )
            )
            k8s_client.create_persistent_volume(body=pv)

    console.print("")
    console.print("K8s resources created successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
    console.print("You can now access the starflow frontend at: http://localhost/")
    console.print("starflow's REST API: http://localhost/api/")
    console.print("starflow's REST API Swagger: http://localhost/api/docs")
    console.print("")


def destroy_platform() -> None:
    # Delete Kind cluster
    with open("config-starflow-local.toml", "rb") as f:
        platform_config = tomli.load(f)
    cluster_name = platform_config["kind"]["STARFLOW_KIND_CLUSTER_NAME"]
    console.print(f"Removing Kind cluster - {cluster_name}...")
    result = subprocess.run(["kind", "delete", "cluster", "--name", cluster_name], capture_output=True, text=True)
    if result.returncode != 0:
        error_message = result.stderr.strip() if result.stderr else result.stdout.strip()
        raise Exception(f"An error occurred while deleting Kind cluster - {cluster_name}: {error_message}")
    console.print("")
    console.print("Kind cluster removed successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
    console.print("")


def run_platform_compose(
    github_token: str,
    use_config_file: bool = False,
    dev: bool = False,
    debug: bool = False
) -> None:
    console.print("Starting starflow Platform using Docker Compose.")
    console.print("Please wait, this might take a few minutes...")
    # Database default settings
    create_database = True
    os.environ['STARFLOW_CREATE_DEFAULT_USER'] = 'true'
    os.environ['STARFLOW_DEFAULT_PIECES_REPOSITORY_TOKEN'] = github_token
    if use_config_file:
        console.print("Using config file...")
        with open("config-starflow-local.toml", "rb") as f:
            platform_config = tomli.load(f)
        create_database = platform_config['starflow_db'].get('STARFLOW_CREATE_DATABASE', True)
        os.environ['STARFLOW_CREATE_DEFAULT_USER'] = str(platform_config['starflow_db'].get('STARFLOW_CREATE_DEFAULT_USER', 'true')).lower()

        if not create_database:
            os.environ['STARFLOW_DB_HOST'] = platform_config['starflow_db'].get("STARFLOW_DB_HOST", 'postgres')
            os.environ['STARFLOW_DB_PORT'] = platform_config['starflow_db'].get("STARFLOW_DB_PORT", 5432)
            os.environ['STARFLOW_DB_USER'] = platform_config['starflow_db'].get("STARFLOW_DB_USER", 'postgres')
            os.environ['STARFLOW_DB_PASSWORD'] = platform_config['starflow_db'].get("STARFLOW_DB_PASSWORD", 'postgres')
            os.environ['STARFLOW_DB_NAME'] = platform_config['starflow_db'].get("STARFLOW_DB_NAME", 'postgres')
            os.environ['NETWORK_MODE'] = 'bridge'

        # If running database in an external local container, set network mode to host
        if platform_config['starflow_db'].get('STARFLOW_DB_HOST') in ['localhost', '0.0.0.0', '127.0.0.1']:
            os.environ['NETWORK_MODE'] = 'host'

    # Create local directories
    local_path = Path(".").resolve()
    starflow_dir = local_path / "starflow_data"
    starflow_dir.mkdir(parents=True, exist_ok=True)
    starflow_dir.chmod(0o777)

    airflow_base = local_path / 'airflow'
    airflow_logs_dir = airflow_base / "logs"
    airflow_logs_dir.mkdir(parents=True, exist_ok=True)
    airflow_dags_dir = airflow_base / "dags"
    airflow_dags_dir.mkdir(parents=True, exist_ok=True)
    airflow_plugins_dir = airflow_base / "plugins"
    airflow_plugins_dir.mkdir(parents=True, exist_ok=True)
    airflow_base.chmod(0o777)

    # Copy docker-compose.yaml file from package to local path
    if create_database:
        docker_compose_path = Path(__file__).resolve().parent / "docker-compose.yaml"
    else:
        docker_compose_path = Path(__file__).resolve().parent / "docker-compose-without-database.yaml"
    shutil.copy(str(docker_compose_path), "./docker-compose.yaml")

    # Environment variables
    environment = os.environ.copy()
    environment['STARFLOW_COMPOSE_DEV'] = ''
    if dev:
        environment['STARFLOW_COMPOSE_DEV'] = '-dev'

    # Run docker compose pull
    console.print("\nPulling Docker images...")
    pull_cmd = [
        "docker",
        "compose",
        "pull"
    ]
    pull_process = subprocess.Popen(pull_cmd, env=environment)
    pull_process.wait()
    if pull_process.returncode == 0:
        console.print(" \u2713 Docker images pulled successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
    else:
        console.print("Docker images pull failed.", style=f"bold {COLOR_PALETTE.get('error')}")

    # Run docker compose up
    console.print("\nStarting services...")
    cmd = [
        "docker",
        "compose",
        "up"
    ]

    if debug:
        subprocess.Popen(cmd, env=environment)
    else:
        airflow_redis_ready = False
        airflow_database_ready = False
        airflow_init_ready = False
        airflow_triggerer_ready = False
        airflow_worker_ready = False
        airflow_webserver_ready = False
        airflow_scheduler_ready = False
        starflow_database_ready = False

        process = subprocess.Popen(cmd, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Read and filter the output
        def customize_message(
            line: str,
            airflow_redis_ready: bool = False,
            airflow_database_ready: bool = False,
            airflow_init_ready: bool = False,
            airflow_triggerer_ready: bool = False,
            airflow_worker_ready: bool = False,
            airflow_webserver_ready: bool = False,
            airflow_scheduler_ready: bool = False,
            starflow_database_ready: bool = False,
        ):
            line = line.lower()
            line = re.sub(r'\s+', ' ', line)
            if not airflow_redis_ready and "airflow-redis" in line and "ready to accept connections tcp" in line:
                console.print(" \u2713 Airflow Redis service started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                airflow_redis_ready = True
            if not airflow_database_ready and "airflow-postgres" in line and ("ready" in line or "skipping" in line):
                console.print(" \u2713 Airflow database service started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                airflow_database_ready = True
            if not airflow_init_ready and "airflow-init" in line and "exited with code 0" in line:
                console.print(" \u2713 Airflow pre-initialization service completed successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                airflow_init_ready = True
            if not airflow_triggerer_ready and "airflow-triggerer" in line and "starting" in line:
                console.print(" \u2713 Airflow triggerer service started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                airflow_triggerer_ready = True
            if not airflow_worker_ready and "airflow-starflow-worker" in line and "execute_command" in line:
                console.print(" \u2713 Airflow worker service started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                airflow_worker_ready = True
            if not airflow_webserver_ready and "airflow-webserver" in line and "health" in line and "200" in line:
                console.print(" \u2713 Airflow webserver service started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                airflow_webserver_ready = True
            if not airflow_scheduler_ready and "airflow-starflow-scheduler" in line and "launched" in line:
                console.print(" \u2713 Airflow scheduler service started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                airflow_scheduler_ready = True
            if not starflow_database_ready and "starflow-postgres" in line and ("ready" in line or "skipping" in line):
                console.print(" \u2713 starflow database service started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                starflow_database_ready = True
            return airflow_redis_ready, airflow_database_ready, airflow_init_ready, airflow_triggerer_ready, airflow_worker_ready, airflow_webserver_ready, airflow_scheduler_ready, starflow_database_ready

        def check_starflow_processes():
            while True:
                frontend_response = requests.get("http://localhost:3000").status_code
                rest_response = requests.get("http://localhost:8000/health-check").status_code
                if frontend_response == 200 and rest_response == 200:
                    console.print(" \u2713 starflow REST service started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                    console.print(" \u2713 starflow frontend service started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                    break
                time.sleep(5)

        for line in process.stdout:
            airflow_redis_ready, airflow_database_ready, airflow_init_ready, airflow_triggerer_ready, airflow_worker_ready, airflow_webserver_ready, airflow_scheduler_ready, starflow_database_ready = customize_message(
                line, airflow_redis_ready, airflow_database_ready, airflow_init_ready, airflow_triggerer_ready,
                airflow_worker_ready, airflow_webserver_ready, airflow_scheduler_ready, starflow_database_ready)
            if all([
                airflow_redis_ready,
                airflow_database_ready,
                airflow_init_ready,
                airflow_triggerer_ready,
                airflow_worker_ready,
                airflow_webserver_ready,
                airflow_scheduler_ready,
                starflow_database_ready,
            ]):
                check_starflow_processes()
                console.print("\n \u2713 All services for starflow Platform started successfully!", style=f"bold {COLOR_PALETTE.get('success')}")
                console.print("")
                console.print("You can now access them at")
                console.print("starflow UI: http://localhost:3000")
                console.print("starflow REST API: http://localhost:8000")
                console.print("starflow REST API Docs: http://localhost:8000/docs")
                console.print("Airflow webserver: http://localhost:8080")
                console.print("")
                console.print("To stop the platform, run:")
                console.print("    $ starflow platform stop-compose")
                console.print("")
                break


def stop_platform_compose() -> None:
    # If "docker-compose.yaml" file is present in current working path, try run "docker compose down"
    docker_compose_path = Path.cwd().resolve() / "docker-compose.yaml"
    if docker_compose_path.exists():
        # Setting this environment variable to empty string just to print cleaner messages to terminal
        environment = os.environ.copy()
        environment['STARFLOW_COMPOSE_DEV'] = ''
        environment['STARFLOW_DEFAULT_PIECES_REPOSITORY_TOKEN'] = ''
        environment['AIRFLOW_UID'] = ''
        cmd = [
            "docker",
            "compose",
            "down"
        ]
        completed_process = subprocess.run(cmd, env=environment)
        # if completed_process.returncode == 0:
        #     print("starflow Platform stopped successfully. All containers were removed.")

    # Stop and remove containers by name
    def stop_and_remove_container(container_name):
        print(f"Stopping {container_name}...")
        process = subprocess.Popen(f"docker stop {container_name}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            # print(f"Command failed with error: {stderr.decode()}")
            pass
        else:
            print(stdout.decode())

        print(f"Removing {container_name}...")
        process = subprocess.Popen(f"docker rm {container_name}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            # print(f"Command failed with error: {stderr.decode()}")
            pass
        else:
            print(stdout.decode())

    try:
        container_names = [
            "starflow-frontend",
            "starflow-rest",
            "starflow-postgres",
            "starflow-docker-proxy",
            "airflow-starflow-scheduler",
            "airflow-starflow-worker",
            "airflow-webserver",
            "airflow-triggerer",
            "airflow-redis",
            "airflow-postgres",
            "airflow-flower",
            "airflow-cli",
            "airflow-init",
        ]
        with ThreadPoolExecutor() as executor:
            executor.map(stop_and_remove_container, container_names)
        console.print("\n \u2713 starflow Platform stopped successfully. All containers were removed.\n", style=f"bold {COLOR_PALETTE.get('success')}")
    except Exception as e:
        print(f"An error occurred: {e}")
