import pulumi
import pytest
from pulumi.runtime import set_mocks
from mocks import HirundoMocks

# Fixture to register Pulumi Mocks before each test
@pytest.fixture(autouse=True)
def register_mocks():
    set_mocks(HirundoMocks())

# Fixture to import and run the Pulumi program
@pytest.fixture
def pulumi_program():
    from infrastructure_home_test import __main__ as pulumi_main
    return pulumi_main

# Test if the network is created
def test_network_created(pulumi_program):
    def check_network(args):
        _, auto_create_subnetworks = args
        assert auto_create_subnetworks is False

    pulumi.Output.all(pulumi_program.network.id, pulumi_program.network.auto_create_subnetworks).apply(check_network)

# Test if the subnetwork is created
def test_subnetwork_created(pulumi_program):
    def check_subnetwork(args):
        _, ip_cidr_range, private_ip_google_access = args
        assert ip_cidr_range == "10.0.0.0/24"
        assert private_ip_google_access is True

    pulumi.Output.all(
        pulumi_program.subnetwork.id,
        pulumi_program.subnetwork.ip_cidr_range,
        pulumi_program.subnetwork.private_ip_google_access,
    ).apply(check_subnetwork)

# Test if GKE cluster is created
def test_gke_cluster_created(pulumi_program):
    def check_gke_cluster(args):
        _, enable_autopilot, remove_default_node_pool = args
        assert enable_autopilot is False
        assert remove_default_node_pool is True

    pulumi.Output.all(
        pulumi_program.gke_cluster.id,
        pulumi_program.gke_cluster.enable_autopilot,
        pulumi_program.gke_cluster.remove_default_node_pool,
    ).apply(check_gke_cluster)

# Test if Cloud SQL instance is created
def test_cloud_sql_instance_created(pulumi_program):
    def check_cloud_sql(args):
        _, settings = args
        assert settings["database_version"] == "POSTGRES_15"
        assert settings["backup_configuration"]["enabled"] is True
        assert settings["backup_configuration"]["start_time"] == "05:00"
        assert settings["backup_configuration"]["retained_backups"] == 7
        assert settings["ip_configuration"]["require_ssl"] is True

    pulumi.Output.all(
        pulumi_program.cloud_sql_instance.id,
        pulumi_program.cloud_sql_instance.settings,
    ).apply(check_cloud_sql)

# Test if Kubernetes Namespace is created
def test_k8s_namespace_created(pulumi_program):
    def check_namespace(args):
        _, namespace_name = args
        assert namespace_name == "hirundo"

    pulumi.Output.all(
        pulumi_program.hirundo_namespace.id,
        pulumi_program.hirundo_namespace.metadata["name"],
    ).apply(check_namespace)

# Test if Kubernetes Secret is created
def test_k8s_secret_created(pulumi_program):
    def check_secret(args):
        _, secret_name = args
        assert secret_name == "hirundo-secret"

    pulumi.Output.all(
        pulumi_program.k8s_secret.id,
        pulumi_program.k8s_secret.metadata["name"],
    ).apply(check_secret)

# Test if Helm Chart is deployed
def test_helm_chart_deployed(pulumi_program):
    def check_helm_chart(args):
        _, chart_name = args
        assert chart_name == "nginx"

    pulumi.Output.all(
        pulumi_program.helm_chart.id,
        pulumi_program.helm_chart.chart,
    ).apply(check_helm_chart)