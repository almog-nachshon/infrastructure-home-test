import pulumi
import pulumi_gcp as gcp

# Configuration
config = pulumi.Config()
project = "hirundo-infrastructure-test"
region = "us-central1"
node_machine_type = config.get("node_machine_type") or "n1-standard-2"

# Enable GCP Services
compute_service = gcp.projects.Service("compute", project=project, service="compute.googleapis.com")
crm_service = gcp.projects.Service("crm", project=project, service="cloudresourcemanager.googleapis.com")
container_service = gcp.projects.Service("container", project=project, service="container.googleapis.com")
service_networking_service = gcp.projects.Service("service-networking", project=project, service="servicenetworking.googleapis.com")
sql_admin_service = gcp.projects.Service("sqladmin", project=project, service="sqladmin.googleapis.com")

# Create a VPC Network
network = gcp.compute.Network("network", project=project, auto_create_subnetworks=False)

# Create a Subnetwork for GKE
subnetwork = gcp.compute.Subnetwork(
    "subnetwork",
    project=project,
    region=region,
    network=network.id,
    ip_cidr_range="10.0.0.0/24",
    private_ip_google_access=True,
)

# Create a GKE Cluster with GCFS enabled
gke_cluster = gcp.container.Cluster(
    "gke-cluster",
    project=project,
    location=region,
    enable_autopilot=False,
    remove_default_node_pool=True,
    initial_node_count=1,
    networking_mode="VPC_NATIVE",
    ip_allocation_policy={},
    resource_labels={"env": "test"},
)

# Create a GKE Node Pool
gke_node_pool = gcp.container.NodePool(
    "gke-node-pool",
    project=project,
    cluster=gke_cluster.id,
    location=region,
    node_config={"machine_type": node_machine_type},
    initial_node_count=1,
)

# Reserve a private IP for Cloud SQL
private_ip = gcp.compute.GlobalAddress(
    "private-ip",
    project=project,
    address_type="INTERNAL",
    purpose="VPC_PEERING",
    network=network.id,
)

# Establish VPC peering
gcp.servicenetworking.Connection(
    "vpc-peering",
    project=project,
    network=network.id,
    service="servicenetworking.googleapis.com",
    reserved_peering_ranges=[private_ip.name],
)

# Create Cloud SQL Instance
cloud_sql_instance = gcp.sql.DatabaseInstance(
    "cloud-sql-instance",
    project=project,
    region=region,
    database_version="POSTGRES_15",
    settings={
        "tier": "db-f1-micro",
        "backup_configuration": {
            "enabled": True,
            "start_time": "05:00",
            "point_in_time_recovery_enabled": True,
            "retained_backups": 7,
        },
        "ip_configuration": {
            "private_network": network.id,
            "require_ssl": True,
        },
    },
)

# Export outputs
pulumi.export("network_id", network.id)
pulumi.export("subnetwork_id", subnetwork.id)
pulumi.export("gke_cluster_id", gke_cluster.id)
pulumi.export("cloud_sql_instance_id", cloud_sql_instance.id)
