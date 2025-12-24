# Cribl Architecture Overview Tool

A Python script that interacts with the Cribl Cloud API to provide a comprehensive overview of your system's architecture. Designed to help engineers quickly understand the environment by summarizing key components.

## Features

- Lists worker groups (fleets) with their IDs, names, and product types
- Shows all workers with hostname, status, and group associations
- For each worker group, displays:
  - Sources (inputs) - e.g., Splunk HEC, Syslog
  - Destinations (outputs) - e.g., Splunk, S3
  - Pipelines with processing logic
  - Routes showing data flow configuration
- ASCII diagram visualization of data flows
- Structured, hierarchical output for easy reading

## Requirements

- Python 3.x
- `requests` library

```bash
pip install requests
```

## Usage

1. Obtain your Cribl Cloud API Bearer token from **Settings > Global > API Reference** in your Cribl instance
2. Run the script:

```bash
python cribl_overview.py
```

3. Enter your Cribl Cloud instance base URL when prompted (e.g., `https://main-instance.cribl.cloud`)
4. Enter your Bearer token when prompted

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/master/groups` | List worker groups/fleets |
| `GET /api/v1/master/workers` | List all workers |
| `GET /api/v1/m/{group_id}/system/inputs` | List sources per group |
| `GET /api/v1/m/{group_id}/system/outputs` | List destinations per group |
| `GET /api/v1/m/{group_id}/system/pipelines` | List pipelines per group |
| `GET /api/v1/m/{group_id}/routes` | List routes per group |

## License

MIT
