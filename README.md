# Infrastructure Home Test -  By Almog Nachshon

This project defines and provisions Google Cloud infrastructure using Pulumi with Python. It includes a VPC, a subnetwork, a GKE cluster with GCFS enabled, and a Cloud SQL instance with a private IP and backups.

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Infrastructure Components](#infrastructure-components)
- [Running the Pulumi Program](#running-the-pulumi-program)
- [Testing](#testing)
- [Code](#code)
- [Topic](#topic)
- [Assumptions](#assumptions)
- [Questions & Considerations](#questions--considerations)

## Requirements

- Pulumi 3.149.0
- Python 3.13
- `pip` or `pixi` for dependency management
- `pytest` for testing
- `pyright` and `ruff` for static analysis and linting

## Setup

1. **Clone the Repository:**

   ```sh
   git clone https://github.com/Hirundo-io/infrastructure-home-test.git
   cd infrastructure_home_test
   ```

2. **Install Dependencies:** Using `pip`:

   ```sh
   pip install -r requirements.txt
   ```

   Using `pixi`:

   ```sh
   pixi install
   ```

3. **Configure Pulumi:**

   ```sh
   pulumi login --local
   pulumi stack init dev
   pulumi config set gcp:project hirundo-infrastructure-test
   pulumi config set gcp:region us-central1
   ```

4. **Verify Static Analysis & Linting:**

   ```sh
   ruff check .
   pyright
   ```

## Project Structure

```
infrastructure_home_test/
│── Pulumi.yaml            # Pulumi project configuration
│── __init__.py            # Empty init file
│── __main__.py            # Main Pulumi infrastructure definition
│── mocks.py               # Mocks for testing
│── test_infra.py          # Unit tests for infrastructure
│── requirements.txt       # Python dependencies
│── README.md              # Project documentation
```

## Infrastructure Components

The project provisions the following resources:

- **GCP Services:** Enables necessary GCP services:
  - Compute Engine API
  - Cloud Resource Manager API
  - Kubernetes Engine API
  - Service Networking API
  - Cloud SQL Admin API
- **VPC Network & Subnetwork:**
  - Creates a private VPC network
  - Subnet with CIDR `10.0.0.0/24`
- **GKE Cluster & Node Pool:**
  - Enables GCFS for image streaming
  - Default node pool with `n1-standard-2` instance
- **Cloud SQL Instance:**
  - PostgreSQL 15 with private IP & VPC peering
  - Backups enabled (5 AM daily, retention: 7 days)
  - Enforces SSL connections

## Running the Pulumi Program

To preview the changes:

```sh
pulumi preview
```

To deploy the infrastructure:

```sh
pulumi up
```

To destroy the infrastructure:

```sh
pulumi destroy
```

## Testing

To run unit tests using Pulumi Mocks:

```sh
pytest test_infra.py
```

## Code

Here is an example of defining a GCP Compute Network in Pulumi:

```python
import pulumi
import pulumi_gcp as gcp

network = gcp.compute.Network(
    "network",
    auto_create_subnetworks=False
)
```

## Topic

This project focuses on **Infrastructure as Code (IaC)** using Pulumi with GCP. It ensures infrastructure is defined, tested, and provisioned in a repeatable manner.

## Assumptions

- The `hirundo-infrastructure-test` GCP project exists (though it is mocked for testing).
- All resources are deployed in `us-central1`.
- The default machine type for GKE nodes is `n1-standard-2`, configurable via Pulumi config.

## Questions & Considerations

- Should we enable more advanced security policies for Cloud SQL?
- Should we configure autoscaling for the GKE node pool?
- Is additional logging/monitoring required for production readiness?

