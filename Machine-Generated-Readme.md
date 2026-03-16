# Cloud Provisioner

A backend API for automated enterprise cloud resource provisioning, running on **minikube** with **LocalStack** simulating AWS, exposed publicly via **ngrok**.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Your Machine                     │
│                                                     │
│  ┌──────────────────────┐   ┌────────────────────┐  │
│  │      minikube        │   │    LocalStack      │  │
│  │                      │   │  (Docker Compose)  │  │
│  │  ┌────────────────┐  │   │                    │  │
│  │  │ cloud-provisioner│◄──►│  S3  EC2  IAM  VPC │  │
│  │  │  (FastAPI Pod)  │  │   │  DynamoDB         │  │
│  │  └───────┬────────┘  │   └────────────────────┘  │
│  │          │ NodePort  │                           │
│  │          │ :30080    │                           │
│  └──────────┼───────────┘                           │
│             │                                       │
│         ┌───▼────┐                                  │
│         │  ngrok │◄── Public HTTPS URL              │
│         └────────┘                                  │
└─────────────────────────────────────────────────────┘
```

**Stack:**
- **FastAPI** — REST API (Python 3.11)
- **SQLite** — persisted via k8s PersistentVolumeClaim
- **Terraform** — IaC for VPC, EC2, S3, IAM (run inside the pod)
- **LocalStack** — local AWS simulation
- **Helm** — k8s packaging and deployment
- **minikube** — local Kubernetes cluster
- **ngrok** — public HTTPS tunnel
- **GitHub Actions** — CI (lint, test, validate) + CD (build, push, deploy)

---

## Prerequisites

Install the following on your Ubuntu machine:

```bash
# Docker
sudo apt-get install docker.io

# minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl
sudo snap install kubectl --classic

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# ngrok
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Configure ngrok with your auth token
ngrok config add-authtoken <YOUR_NGROK_AUTHTOKEN>
```

---

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/your-org/cloud-provisioner.git
cd cloud-provisioner
cp .env.example .env
# Edit .env and set your LOCALSTACK_AUTH_TOKEN
```

### 2. Start LocalStack and bootstrap Terraform state

```bash
./scripts/setup-localstack.sh
```

This starts LocalStack via Docker Compose and creates:
- S3 bucket `tf-state-provisioner` for Terraform remote state
- DynamoDB table `terraform-lock` for state locking

### 3. Deploy to minikube and expose via ngrok

```bash
./scripts/deploy-minikube.sh
```

This will:
1. Start minikube (if not running)
2. Build the Docker image inside minikube's daemon
3. Deploy the Helm chart
4. Start an ngrok tunnel and print your public URL

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/provisions` | Create a new provision |
| `GET` | `/provisions` | List all provisions |
| `GET` | `/provisions/{id}` | Get provision status |
| `DELETE` | `/provisions/{id}` | Deprovision (destroy resources) |

Interactive docs available at: `http://<ngrok-url>/docs`

### Create a provision

```bash
curl -X POST https://<ngrok-url>/provisions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "team-alpha",
    "owner": "alice",
    "tshirt_size": "medium"
  }'
```

**T-shirt sizes:**

| Size | EC2 Instance | Disk |
|------|-------------|------|
| `small` | t3.small | 20 GB |
| `medium` | t3.medium | 50 GB |
| `large` | t3.xlarge | 100 GB |

**Provision lifecycle:**
```
pending → provisioning → active
                       ↘ failed
active → (DELETE) → destroyed
```

### Check status

```bash
curl https://<ngrok-url>/provisions/<id>
```

### Deprovision

```bash
curl -X DELETE https://<ngrok-url>/provisions/<id>
```

---

## Development

### Run tests locally

```bash
pip install -r requirements.txt
pytest tests/ -v
```

### Run the API locally (without minikube)

```bash
cp .env.example .env          # ensure LocalStack is running first
uvicorn app.main:app --reload
```

---

## CI/CD (GitHub Actions)

### CI — runs on every Pull Request
- **Ruff** linting
- **pytest** unit tests
- **helm lint** chart validation
- **terraform validate** config validation

### CD — runs on merge to `main`
- Builds and pushes Docker image to **Docker Hub**
- Deploys to k8s via **Helm**

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `KUBECONFIG_B64` | Base64-encoded kubeconfig for your cluster |

To encode your kubeconfig:
```bash
base64 -w 0 ~/.kube/config
```

---

## Project Structure

```
cloud-provisioner/
├── app/                        # FastAPI application
│   ├── api/provisions.py       # REST endpoints
│   ├── core/config.py          # Settings
│   ├── core/database.py        # SQLite setup
│   ├── models/provision.py     # ORM model
│   ├── schemas/provision.py    # Pydantic schemas
│   └── services/terraform.py  # Terraform runner
├── terraform/
│   ├── modules/                # vpc / ec2 / s3 / iam
│   └── environments/dev/       # Root config pointing at LocalStack
├── helm/cloud-provisioner/     # Helm chart
├── scripts/
│   ├── setup-localstack.sh     # Bootstrap LocalStack
│   └── deploy-minikube.sh      # Full local deploy
├── tests/                      # pytest test suite
├── .github/workflows/          # CI + CD pipelines
├── docker-compose.yml          # LocalStack only
├── Dockerfile
└── .env.example
```
