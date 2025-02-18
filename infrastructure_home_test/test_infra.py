import pulumi
import pytest
from pulumi.runtime import set_mocks, test
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
    def check(args):
        _, auto_create_subnetworks = args
        assert auto_create_subnetworks is False

    test.run_test(
        lambda: pulumi.Output.all(
            pulumi_program.network.id,
            pulumi_program.network.auto_create_subnetworks,
        ).apply(check)
    )

# Test if the subnetwork is created
def test_subnetwork_created(pulumi_program):
    def check(args):
        _, ip_cidr_range, private_ip_google_access = args
        assert ip_cidr_range == "10.0.0.0/24"
        assert private_ip_google_access is True

    test.run_test(
        lambda: pulumi.Output.all(
            pulumi_program.subnetwork.id,
            pulumi_program.subnetwork.ip_cidr_range,
            pulumi_program.subnetwork.private_ip_google_access,
        ).apply(check)
    )

# Test if GKE cluster is created
def test_gke_cluster_created(pulumi_program):
    def check(args):
        _, enable_autopilot, remove_default_node_pool = args
        assert enable_autopilot is False
        assert remove_default_node_pool is True

    test.run_test(
        lambda: pulumi.Output.all(
            pulumi_program.gke_cluster.id,
            pulumi_program.gke_cluster.enable_autopilot,
            pulumi_program.gke_cluster.remove_default_node_pool,
        ).apply(check)
    )

# Test if Cloud SQL instance is created
def test_cloud_sql_instance_created(pulumi_program):
    def check(args):
        _, settings = args
        assert settings.database_version == "POSTGRES_15"
        assert settings.backup_configuration.enabled is True
        assert settings.backup_configuration.start_time == "05:00"
        assert settings.backup_configuration.backup_retention_settings.retained_backups == 7
        assert settings.ip_configuration.require_ssl is True

    test.run_test(
        lambda: pulumi.Output.all(
            pulumi_program.cloud_sql_instance.id,
            pulumi_program.cloud_sql_instance.settings,
        ).apply(check)
    )

# Test if Kubernetes Namespace is created
def test_k8s_namespace_created(pulumi_program):
    def check(args):
        _, namespace_name = args
        assert namespace_name == "hirundo"

    test.run_test(
        lambda: pulumi.Output.all(
            pulumi_program.hirundo_namespace.id,
            pulumi_program.hirundo_namespace.metadata["name"],
        ).apply(check)
    )

# Test if Node Pool uses the correct machine type
def test_node_pool_machine_type(pulumi_program):
    def check(args):
        _, machine_type = args
        assert machine_type == "n1-standard-2"  # Default value from config

    test.run_test(
        lambda: pulumi.Output.all(
            pulumi_program.gke_node_pool.id,
            pulumi_program.gke_node_pool.node_config.machine_type,
        ).apply(check)
    )