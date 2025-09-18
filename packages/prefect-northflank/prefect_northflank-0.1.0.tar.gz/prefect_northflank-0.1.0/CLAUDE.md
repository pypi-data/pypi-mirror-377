# CLAUDE.md - Prefect Northflank Worker Architecture

## Project Overview
This is a **Prefect 3.x custom PULL worker** that executes flow runs as containerized jobs on the Northflank platform. The worker follows the container/job submission execution strategy rather than subprocess execution.

## Architecture

### Core Components

1. **NorthflankWorker** (`prefect_northflank/worker.py:104`)
   - Extends `BaseWorker[JobConfig, Variables, Result]` with proper generics
   - Type: `"northflank"`
   - Execution strategy: Container job submission via Northflank API

2. **NorthflankJobConfiguration** (`prefect_northflank/worker.py:20`)
   - Runtime configuration for individual job executions
   - Includes Northflank-specific fields: deployment_plan, gpu_enabled, etc.
   - Handles command generation and environment merging

3. **NorthflankVariables** (`prefect_northflank/worker.py:60`)
   - Template variables for work pool configuration
   - Mirrors job configuration for pool-level defaults

4. **NorthflankClient** (`prefect_northflank/client.py`)
   - Async HTTP client for Northflank API interactions
   - Handles: job creation, execution, status polling, cleanup

### Execution Flow

1. **Job Creation**: Worker creates Northflank job with deployment configuration
2. **Job Start**: Initiates job run with merged environment variables
3. **Status Monitoring**: Polls job status until completion (SUCCESS/FAILED)
4. **Cleanup**: Optionally deletes job after completion if `cleanup_job=True`

### Deployment Types

The worker supports three deployment strategies:

1. **External Image**: Deploy from a pre-built container image (default: "prefecthq/prefect:3-python3.12")
2. **Internal Build**: Deploy from Northflank build service output
3. **VCS (Version Control)**: Deploy directly from Git repository source code

Only one deployment type can be specified per job. If none is explicitly configured, external deployment with the default Prefect image is used.

## Key Practices

### Environment Variable Merging
```python
# Correct pattern for env merging
env = {
    **self._get_flow_run_env(flow_run),  # Prefect base environment
    **(configuration.env or {}),        # User-provided overrides
}
```

### Command Generation
```python
# Default to Prefect engine execution if no command specified
command = configuration.command or [
    "python", "-m", "prefect.engine", "execute-flow-run", str(flow_run.id)
]
```

### Error Handling
- Use flow run logger: `self.get_flow_run_logger(flow_run)`
- Validate configuration early with clear error messages
- Always attempt cleanup in `finally` blocks
- Distinguish between transient and permanent failures

### Resource Management
- Use async context managers for HTTP clients
- Implement proper cancellation handling
- Set appropriate timeouts for job operations
- Clean up Northflank resources on failure/cancellation

## Configuration Options

### Job Configuration
- `credentials`: Northflank block or environment variables
- `project_id`: Required Northflank project ID
- `deployment_plan`: Resource allocation (default: "nf-compute-20")
- `image`: Container image (default: "prefecthq/prefect:3-python3.12")
- `command`: Custom command (default: Prefect engine execution)
- `active_deadline_seconds`: Job timeout (default: 3600)
- `backoff_limit`: Retry attempts (default: 3)
- `gpu_enabled`: Enable GPU support (default: False)
- `cleanup_job`: Delete job after completion (default: True)

### VCS Deployment Configuration
- `deployment_vcs_project_url`: URL of the Git repo to build from
- `deployment_vcs_project_type`: VCS provider (github, gitlab, bitbucket, self-hosted, azure)
- `deployment_vcs_project_branch`: Git branch name to deploy
- `deployment_vcs_self_hosted_vcs_id`: ID for self-hosted VCS (when project_type is self-hosted)
- `deployment_vcs_account_login`: Specific VCS account login to use
- `deployment_vcs_vcs_link_id`: ID of linked VCS account to use

## Testing Strategy

### Unit Tests (`tests/`)
- Configuration validation
- Environment merging logic
- Mock Northflank API responses
- Error handling scenarios
- Cancellation behavior

### Integration Tests
- End-to-end flow execution with mock API
- Work pool creation and configuration
- Deployment lifecycle testing

## Development Commands

### Setup
```bash
uv sync
uv run python -m pip install -e .

```
### Linting
```bash
uv run ruff check .
uv run mypy prefect_northflank/
```

## Deployment Patterns

### Work Pool Creation
```bash
prefect work-pool create --type northflank my-northflank-pool
```

### Worker Start
```bash
prefect worker start --pool my-northflank-pool --type northflank
```

### Flow Deployment

#### External Image Deployment
```yaml
# prefect.yaml
work_pool:
  name: my-northflank-pool
  job_variables:
    credentials: "{{ prefect.blocks.northflank-credentials.my-creds }}"
    project_id: "proj-12345"
    deployment_external_image_path: "python:3.12-slim"
    billing_deployment_plan: "nf-compute-20"
```

#### Internal Build Service Deployment
```yaml
# prefect.yaml
work_pool:
  name: my-northflank-pool
  job_variables:
    credentials: "{{ prefect.blocks.northflank-credentials.my-creds }}"
    project_id: "proj-12345"
    deployment_internal_id: "build-service-123"
    deployment_internal_branch: "main"
    billing_deployment_plan: "nf-compute-20"
```

## Implementation Status

✅ **Completed Features:**
- BaseWorker with proper generic type parameters
- Complete job configuration and variables classes
- Environment variable merging with Prefect context
- Command generation (custom or default Prefect engine)
- Proper cancellation handling with job termination
- Comprehensive error handling and cleanup
- Full test coverage (33 tests passing)
- Working entry point registration
