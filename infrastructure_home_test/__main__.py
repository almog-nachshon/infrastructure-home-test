import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s

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
    addons_config=gcp.container.ClusterAddonsConfigArgs(
        gcp_filestore_csi_driver_config=gcp.container.ClusterAddonsConfigGcpFilestoreCsiDriverConfigArgs(
            enabled=True,
        ),
    ),
)

# Create a GKE Node Pool
gke_node_pool = gcp.container.NodePool(
    "gke-node-pool",
    project=project,
    cluster=gke_cluster.id,
    location=region,
    node_config=gcp.container.NodePoolNodeConfigArgs(
        machine_type=node_machine_type,
    ),
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
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-f1-micro",
        backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
            enabled=True,
            start_time="05:00",
            backup_retention_settings=gcp.sql.DatabaseInstanceSettingsBackupConfigurationBackupRetentionSettingsArgs(
                retained_backups=7,
            ),
        ),
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            private_network=network.id,
            require_ssl=True,
        ),
    ),
)

###############################
# Bonus: Kubernetes Resources
# Create a Kubernetes Provider
###############################

k8s_provider = k8s.Provider(
    "k8s-provider",
    kubeconfig=gke_cluster.kube_config_raw,
)

# Create a Kubernetes Namespace
hirundo_namespace = k8s.core.v1.Namespace(
    "hirundo-namespace",
    metadata={"name": "hirundo"},
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# Create a Kubernetes Secret
k8s_secret = k8s.core.v1.Secret(
    "k8s-secret",
    metadata={"name": "hirundo-secret", "namespace": hirundo_namespace.metadata["name"]},
    string_data={"example-key": "example-value"},
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# Create a Kubernetes ServiceAccount
k8s_service_account = k8s.core.v1.ServiceAccount(
    "k8s-service-account",
    metadata={"name": "hirundo-sa", "namespace": hirundo_namespace.metadata["name"]},
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# Deploy a Helm Chart (e.g., NGINX)
helm_chart = k8s.helm.v3.Release(
    "nginx-helm-chart",
    chart="nginx",
    namespace=hirundo_namespace.metadata["name"],
    repository_opts=k8s.helm.v3.RepositoryOptsArgs(
        repo="https://charts.bitnami.com/bitnami",
    ),
    values={
        "service": {"type": "ClusterIP"},
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# Export outputs
pulumi.export("network_id", network.id)
pulumi.export("subnetwork_id", subnetwork.id)
pulumi.export("gke_cluster_id", gke_cluster.id)
pulumi.export("cloud_sql_instance_id", cloud_sql_instance.id)
pulumi.export("k8s_namespace", hirundo_namespace.metadata["name"])
pulumi.export("helm_chart_status", helm_chart.status)