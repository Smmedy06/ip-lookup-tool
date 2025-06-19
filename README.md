<h1 align="center">🕵️‍♂️ IP-LOOKUP-TOOL</h1>
<p align="center"><strong>A High-Performance, Extensible Python Tool for IP Geolocation and Threat Intelligence</strong></p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/Smmedy06/ip-lookup-tool?style=flat&logo=git" />
  <img src="https://img.shields.io/badge/Python-100%25-blue?logo=python" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
  <img src="https://img.shields.io/github/languages/count/Smmedy06/ip-lookup-tool" />
</p>

## Features

- Geolocation data lookup using multiple providers:
  - ipinfo.io
  - ip-api.com
- Asynchronous API calls for better performance
- Configurable API timeouts
- Extensible provider architecture

## Project Structure

```
ip_lookup_tool/
├── api/                    # API integration modules
│   ├── base_provider.py    # Base provider interface
│   ├── geo_providers.py    # Geolocation providers
│   └── threat_providers.py # Threat intelligence providers
├── core/                   # Core functionality
│   ├── orchestrator.py     # Main orchestration logic
│   └── ip_utils.py         # IP address utilities
├── reporting/              # Data export functionality
│   └── exporter.py         # Export utilities
├── ui/                     # User interface
│   └── app_gui.py         # GUI implementation
├── config.py              # Configuration settings
├── main.py                # Application entry point
└── requirements.txt       # Project dependencies
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `config.py` file with your API keys:
```python
IPINFO_API_KEY = "your_ipinfo_api_key"
API_TIMEOUT = 10  # seconds
```

## Usage

```python
from core.orchestrator import IPLookupOrchestrator

# Initialize the orchestrator
orchestrator = IPLookupOrchestrator()

# Lookup an IP address
results = await orchestrator.lookup_ip("8.8.8.8")
```

## Dependencies

- aiohttp: For asynchronous HTTP requests
- Additional dependencies listed in requirements.txt

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 
