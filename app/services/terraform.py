import json
import os
import subprocess
import logging
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

# T-shirt size → EC2 instance type mapping
TSHIRT_SIZES = {
    "small":  {"instance_type": "t3.small",  "disk_size_gb": 20},
    "medium": {"instance_type": "t3.medium", "disk_size_gb": 50},
    "large":  {"instance_type": "t3.xlarge", "disk_size_gb": 100},
}


def _run(cmd: list[str], cwd: str, env: dict) -> tuple[int, str, str]:
    """Run a subprocess command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    logger.debug("CMD: %s\nSTDOUT: %s\nSTDERR: %s", cmd, result.stdout, result.stderr)
    return result.returncode, result.stdout, result.stderr


def _build_env(workspace: str) -> dict:
    """Build environment variables for Terraform, pointing at LocalStack."""
    env = os.environ.copy()
    env.update({
        "AWS_ACCESS_KEY_ID":     settings.aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": settings.aws_secret_access_key,
        "AWS_DEFAULT_REGION":    settings.aws_region,
        # Override every AWS provider endpoint to LocalStack
        "AWS_ENDPOINT_URL":      settings.localstack_endpoint,
        # tflocal / Terraform vars
        "TF_VAR_localstack_endpoint": settings.localstack_endpoint,
        "TF_VAR_workspace":           workspace,
        "TF_VAR_aws_region":          settings.aws_region,
    })
    return env


def provision(workspace: str, tshirt_size: str) -> dict:
    """
    Run terraform init + workspace select/new + apply for the given workspace.
    Returns the parsed terraform outputs dict.
    Raises RuntimeError on failure.
    """
    size_cfg = TSHIRT_SIZES[tshirt_size]
    cwd = settings.terraform_working_dir
    env = _build_env(workspace)

    # Inject t-shirt size vars
    env["TF_VAR_instance_type"]  = size_cfg["instance_type"]
    env["TF_VAR_disk_size_gb"]   = str(size_cfg["disk_size_gb"])

    # 1. Init
    rc, out, err = _run(["terraform", "init", "-input=false", "-reconfigure"], cwd, env)
    if rc != 0:
        raise RuntimeError(f"terraform init failed:\n{err}")

    # 2. Workspace
    rc, _, _ = _run(["terraform", "workspace", "select", workspace], cwd, env)
    if rc != 0:
        rc, _, err = _run(["terraform", "workspace", "new", workspace], cwd, env)
        if rc != 0:
            raise RuntimeError(f"terraform workspace new failed:\n{err}")

    # 3. Apply
    rc, out, err = _run(
        ["terraform", "apply", "-input=false", "-auto-approve"],
        cwd, env,
    )
    if rc != 0:
        raise RuntimeError(f"terraform apply failed:\n{err}\n{out}")

    # 4. Capture outputs
    rc, out, err = _run(["terraform", "output", "-json"], cwd, env)
    if rc != 0:
        raise RuntimeError(f"terraform output failed:\n{err}")

    raw = json.loads(out)
    return {k: v["value"] for k, v in raw.items()}


def deprovision(workspace: str) -> None:
    """
    Run terraform destroy for the given workspace.
    Raises RuntimeError on failure.
    """
    cwd = settings.terraform_working_dir
    env = _build_env(workspace)

    rc, _, err = _run(["terraform", "workspace", "select", workspace], cwd, env)
    if rc != 0:
        raise RuntimeError(f"Workspace '{workspace}' not found:\n{err}")

    rc, out, err = _run(
        ["terraform", "destroy", "-input=false", "-auto-approve"],
        cwd, env,
    )
    if rc != 0:
        raise RuntimeError(f"terraform destroy failed:\n{err}\n{out}")

    # Clean up the workspace
    _run(["terraform", "workspace", "select", "default"], cwd, env)
    _run(["terraform", "workspace", "delete", workspace], cwd, env)
