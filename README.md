# Cribl Cloud Explorer Overview Tool

A Python script that interacts with the Cribl Cloud API to provide a comprehensive overview of your system's architecture. Designed to help engineers quickly understand the environment by summarizing key components.

<details>
  <summary><b>📸 Click to view Screenshots</b></summary>
  <br>
  <div style="display: flex; gap: 10px; justify-content: center;">
      <img src="https://github.com/user-attachments/assets/ce7e3c01-ebaa-48b9-a2b5-bf8298732a12" style="width: 30%; height: 500px; object-fit: cover;" alt="screenshot 1" />
      <img src="https://github.com/user-attachments/assets/3dc9594e-5061-4ab8-9fa7-1d942f97fb55" style="width: 30%; height: 500px; object-fit: cover;" alt="screenshot 2" />
      <img src="https://github.com/user-attachments/assets/cdad2856-9b6d-4eca-9554-01e4030ef1c4" style="width: 30%; height: 500px; object-fit: cover;" alt="screenshot 3" />
  </div>
</details>

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

## Setup

1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Obtaining API Credentials

### Step 1: Create API Client Credentials

1. Log in to your Cribl Cloud instance
2. Navigate to **Settings > Organization > Access Management > API Credentials**
3. Click **Add API Credential**
4. Provide a name for your credential and select appropriate permissions
5. Save and copy your **Client ID** and **Client Secret** (the secret is only shown once)

### Step 2: Generate Bearer Token

Use your client credentials to obtain a Bearer token via the OAuth endpoint:

```bash
curl -X POST "https://login.cribl.cloud/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "<YOUR_CLIENT_ID>",
    "client_secret": "<YOUR_CLIENT_SECRET>",
    "audience": "https://api.cribl.cloud"
  }'
```

The response will contain your Bearer token:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

Copy the `access_token` value — this is your Bearer token.

> **Note:** Tokens expire after 24 hours (86400 seconds). You'll need to generate a new token when it expires.

## Usage

1. Ensure your virtual environment is activated (you should see `(venv)` in your prompt)
2. Run the script:

```bash
python cribl_overview.py
```

3. Enter your Cribl Cloud instance base URL when prompted (e.g., `https://main-instance.cribl.cloud`)
4. Enter your Bearer token when prompted (the `access_token` from the previous section)

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/master/groups` | List worker groups/fleets |
| `GET /api/v1/master/workers` | List all workers |
| `GET /api/v1/m/{group_id}/system/inputs` | List sources per group |
| `GET /api/v1/m/{group_id}/system/outputs` | List destinations per group |
| `GET /api/v1/m/{group_id}/system/pipelines` | List pipelines per group |
| `GET /api/v1/m/{group_id}/routes` | List routes per group |

## Security

### Credential Handling

This script does **not** store credentials on disk. All sensitive information is held in memory only:

- **Base URL**: Collected via standard input (visible in terminal)
- **Bearer Token**: Collected via `getpass` (hidden from terminal, not stored in shell history)

### In-Memory Storage

While the script runs, credentials are stored in the `CriblAPIClient` instance:
- `base_url` - The Cribl Cloud instance URL
- `token` - The raw Bearer token
- `headers` - HTTP headers containing `Authorization: Bearer <token>`

### Lifecycle

- Credentials exist **only** while the script is running
- When you quit (option Q) or press Ctrl+C, the Python process ends and all memory is released
- Changing credentials (option 7) creates a new client instance
- No credentials are written to files, logs, or configuration
- No credentials are printed to stdout

### Note

You will need to re-enter credentials each time you run the script. For automation use cases, consider using environment variables, but be aware of the security tradeoffs.

## License

MIT
