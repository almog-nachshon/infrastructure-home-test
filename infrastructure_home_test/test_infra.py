import pulumi
import pytest
from pulumi.runtime import set_mocks
from pulumi_gcp import compute, container, sql
from mocks import HirundoMocks

# Register the Pulumi Mocks
set_mocks(HirundoMocks())

@pytest.fixture(scope="module")
def pulumi_program():
    from infrastructure_home_test import __main__  # Import the Pulumi program
    return __main__

# Test if the network is created
def test_network_created(pulumi_program):
    def check_network(args):
        assert args["auto_create_subnetworks"] is False
    
    pulumi.Output.all(pulumi_program.network.id, pulumi_program.network.auto_create_subnetworks).apply(check_network)

# Test if the subnetwork is created
def test_subnetwork_created(pulumi_program):
    def check_subnetwork(args):
        assert args["ip_cidr_range"] == "10.0.0.0/24"
        assert args["private_ip_google_access"] is True
    
    pulumi.Output.all(pulumi_program.subnetwork.id, pulumi_program.subnetwork.ip_cidr_range, pulumi_program.subnetwork.private_ip_google_access).apply(check_subnetwork)

# Test if GKE cluster is created
def test_gke_cluster_created(pulumi_program):
    def check_gke_cluster(args):
        assert args["enable_autopilot"] is False
        assert args["remove_default_node_pool"] is True
    
    pulumi.Output.all(pulumi_program.gke_cluster.id, pulumi_program.gke_cluster.enable_autopilot, pulumi_program.gke_cluster.remove_default_node_pool).apply(check_gke_cluster)

# Test if Cloud SQL instance is created
def test_cloud_sql_instance_created(pulumi_program):
    def check_cloud_sql(args):
        assert args["database_version"] == "POSTGRES_15"
        assert args["settings"]["backup_configuration"]["enabled"] is True
        assert args["settings"]["backup_configuration"]["start_time"] == "05:00"
        assert args["settings"]["backup_configuration"]["retained_backups"] == 7
        assert args["settings"]["ip_configuration"]["require_ssl"] is True
    
    pulumi.Output.all(pulumi_program.cloud_sql_instance.id, pulumi_program.cloud_sql_instance.settings).apply(check_cloud_sql)
