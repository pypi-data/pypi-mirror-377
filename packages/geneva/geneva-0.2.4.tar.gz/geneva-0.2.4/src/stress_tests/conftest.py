# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import contextlib
import logging
import random
import warnings

import kubernetes
import pytest

from geneva.cluster import K8sConfigMethod
from geneva.config import override_config_kv
from geneva.runners.ray._mgr import ray_cluster
from geneva.runners.ray.raycluster import (
    ExitMode,
    _HeadGroupSpec,
    _WorkerGroupSpec,
)
from geneva.utils import dt_now_utc

kubernetes.config.load_kube_config()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# it's okay, we are in a test
warnings.filterwarnings(
    "ignore", "Using port forwarding for Ray cluster is not recommended for production"
)
_LOG = logging.getLogger(__name__)


@pytest.fixture(autouse=True, scope="session")
def geneva_k8s_service_account() -> str:
    """
    A preconfigured service account for the test session.
    This service account should have all the permissions needed to run the tests.
    """
    return "geneva-integ-test"


@pytest.fixture(autouse=True, scope="session")
def geneva_test_bucket(csp) -> str:
    if csp == "gcp":
        return "gs://geneva-integ-test/data"
    elif csp == "aws":
        return "s3://geneva-integ-test-devland-us-east-1/data"
    else:
        raise ValueError(f"Unsupported --csp arg: {csp}")


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--csp",
        action="store",
        default="gcp",
        choices=["gcp", "aws"],
        help="CSP to deploy to for integ tests (e.g., 'gcp', 'aws')",
    )
    parser.addoption(
        "--test-slug",
        action="store",
        default=None,
        help="Test slug to identify a test run. Typically used to "
        "cleanup external resources like rayclusters",
    )


@pytest.fixture(scope="session")
def csp(request) -> str:
    csp = request.config.getoption("--csp")
    # integ test specific config overrides
    if csp == "aws":
        override_config_kv(
            {
                "job.checkpoint.mode": "object_store",
                "uploader.upload_dir": "s3://geneva-integ-test-devland-us-east-1/zips",
                "job.checkpoint.object_store.path": "s3://geneva-integ-test-devland-us-east-1/checkpoints",
            }
        )
    else:
        override_config_kv(
            {
                "uploader.upload_dir": "gs://geneva-integ-test/zips",
                "job.checkpoint.mode": "object_store",
                "job.checkpoint.object_store.path": "gs://geneva-integ-test/checkpoints",
            }
        )

    return csp


@pytest.fixture(scope="session")
def slug(request) -> str | None:
    return request.config.getoption("--test-slug") or random.randint(0, 10000)


@pytest.fixture(scope="session")
def region(csp) -> str:
    return "us-east-1" if csp == "aws" else "us-central1"


@pytest.fixture(scope="session")
def k8s_config_method(csp) -> K8sConfigMethod:
    return K8sConfigMethod.EKS_AUTH if csp == "aws" else K8sConfigMethod.LOCAL


@pytest.fixture(scope="session")
def k8s_namespace(csp) -> str:
    # only used for EKS auth currently
    return "geneva"


@pytest.fixture(scope="session")
def k8s_cluster_name(csp) -> str:
    # only used for EKS auth currently
    return "lancedb"


@pytest.fixture(scope="session")
def head_node_selector(csp: str, node_group: str) -> dict:
    # todo: make node selectors consistent between EKS/GKS. This requires
    # a breaking change for GKS
    # https://linear.app/lancedb/issue/GEN-60/make-node-selectors-consistent-between-eksgks
    return (
        {"geneva.lancedb.com/ray-head": "true"}
        if csp == "aws"
        else {"_PLACEHOLDER": "true"}
    )


@pytest.fixture(scope="session")
def worker_node_selector(csp: str, node_group: str) -> dict:
    return (
        {"geneva.lancedb.com/ray-worker-cpu": "true"}
        if csp == "aws"
        else {"_PLACEHOLDER": "true"}
    )


@pytest.fixture(scope="session")
def node_group(num_gpus: int) -> str:
    # These NGs are defined in base infra aws-enterprise eks.tf
    return (
        "lancedb-nodegroup-geneva-gpu" if num_gpus > 0 else "lancedb-nodegroup-geneva"
    )


@pytest.fixture(scope="session")
def num_gpus() -> int:
    return 0


@pytest.fixture
def beefy_cluster(
    geneva_k8s_service_account: str,
    k8s_config_method: K8sConfigMethod,
    k8s_namespace: str,
    csp: str,
    region: str,
    head_node_selector: dict,
    worker_node_selector: dict,
    k8s_cluster_name: str,
    slug: str | None,
) -> contextlib.AbstractContextManager:
    ray_cluster_name = "geneva-stress-test"
    ray_cluster_name += f"-{dt_now_utc().strftime('%Y-%m-%d-%H-%M')}-{slug}"

    _LOG.info(f"creating ray cluster {ray_cluster_name}")

    head_spec = _HeadGroupSpec(
        service_account=geneva_k8s_service_account,
        num_cpus=1,
        memory=3 * 1024**3,
        node_selector=head_node_selector,
    )

    worker_spec = _WorkerGroupSpec(
        name="worker",
        min_replicas=0,
        service_account=geneva_k8s_service_account,
        num_cpus=14,
        memory=56 * 1024**3,
        node_selector=worker_node_selector,
    )

    return ray_cluster(
        name=ray_cluster_name,
        namespace=k8s_namespace,
        config_method=k8s_config_method,
        region=region,
        use_portforwarding=True,
        head_group=head_spec,
        # allocate at least a single worker so the test runs faster
        # that we save time on waiting for the actor to start
        worker_groups=[worker_spec],
        cluster_name=k8s_cluster_name,
        role_name="geneva-client-role",
        on_exit=ExitMode.DELETE,
    )
