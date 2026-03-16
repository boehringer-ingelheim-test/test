import pytest
from unittest.mock import patch, MagicMock
from app.services import terraform


def make_run(returncode=0, stdout="", stderr=""):
    return (returncode, stdout, stderr)


@patch("app.services.terraform._run")
def test_provision_success(mock_run):
    mock_run.side_effect = [
        make_run(0),                          # terraform init
        make_run(1),                          # workspace select (fails → triggers new)
        make_run(0),                          # workspace new
        make_run(0),                          # terraform apply
        make_run(0, '{"vpc_id": {"value": "vpc-123"}}'),  # terraform output
    ]

    outputs = terraform.provision("test-workspace", "medium")
    assert outputs == {"vpc_id": "vpc-123"}


@patch("app.services.terraform._run")
def test_provision_init_failure(mock_run):
    mock_run.return_value = make_run(1, stderr="init error")
    with pytest.raises(RuntimeError, match="terraform init failed"):
        terraform.provision("test-workspace", "small")


@patch("app.services.terraform._run")
def test_provision_apply_failure(mock_run):
    mock_run.side_effect = [
        make_run(0),   # init
        make_run(0),   # workspace select (succeeds)
        make_run(1, stderr="apply error"),  # apply fails
    ]
    with pytest.raises(RuntimeError, match="terraform apply failed"):
        terraform.provision("test-workspace", "large")


@patch("app.services.terraform._run")
def test_deprovision_success(mock_run):
    mock_run.side_effect = [
        make_run(0),  # workspace select
        make_run(0),  # terraform destroy
        make_run(0),  # workspace select default
        make_run(0),  # workspace delete
    ]
    terraform.deprovision("test-workspace")  # should not raise


@patch("app.services.terraform._run")
def test_deprovision_workspace_not_found(mock_run):
    mock_run.return_value = make_run(1, stderr="no workspace")
    with pytest.raises(RuntimeError, match="Workspace"):
        terraform.deprovision("nonexistent-workspace")


def test_tshirt_sizes_defined():
    for size in ("small", "medium", "large"):
        assert size in terraform.TSHIRT_SIZES
        cfg = terraform.TSHIRT_SIZES[size]
        assert "instance_type" in cfg
        assert "disk_size_gb" in cfg
