# JobPoller

A Python library for polling and processing jobs from API endpoints.

## Installation

```bash
pip install jobpoller
```

## Features

- Configurable API endpoints and authentication
- Flexible job processing with customizable scripts
- Robust logging and error handling
- Simple interface for creating job processing services

## Usage

### Basic Usage

```python
from jobpoller import JobProcessor, JobConfig

# Create configuration
config = JobConfig(
    api_url="https://api.example.com",
    api_key="your-api-key",
    poll_endpoint="/queue/next",
    log_dir="queue_logs"
)

# Create job processor
processor = JobProcessor(
    config=config,
    logger_name="QueueProcessor",
    process_script="process_job.py",
    script_executor="python"
)

# Run the processor
processor.run()
```

### Custom Job Processing

```python
from jobpoller import JobProcessor, JobConfig

# Create configuration
config = JobConfig(
    api_url="https://api.example.com",
    api_key="your-api-key",
    poll_endpoint="/renders/next",
    log_dir="render_logs"
)

# Custom job parser function
def parse_render_job(job_data):
    job_id = job_data.get("msgId")
    message = json.loads(job_data.get("message"))
    return {
        "job_id": job_id,
        "floorPlanId": message.get("floorPlanId"),
        "styleId": message.get("styleId")
    }

# Create job processor
processor = JobProcessor(
    config=config,
    logger_name="RenderProcessor",
    process_script="process_blend_automated.sh",
    script_executor="bash",
    job_parser=parse_render_job
)

# Run the processor
processor.run()
```

## License

MIT
