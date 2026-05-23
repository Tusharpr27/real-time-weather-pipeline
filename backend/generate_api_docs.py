#!/usr/bin/env python
"""
API Documentation Generator for Real-Time Weather Pipeline
Generates OpenAPI spec, Swagger UI, and ReDoc documentation
Run: python generate_api_docs.py
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def generate_openapi_spec() -> Dict[str, Any]:
    """
    Generate OpenAPI 3.0.0 specification for the API
    This would normally be auto-generated from FastAPI, but we create a comprehensive spec here
    """
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Real-Time Weather Data Pipeline API",
            "description": "Comprehensive API for weather data collection, processing, analysis, and monitoring",
            "version": "1.0.0",
            "contact": {
                "name": "Weather Pipeline Team",
                "url": "https://github.com/example/weather-pipeline"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.example.com",
                "description": "Production server"
            }
        ],
        "tags": [
            {
                "name": "Weather Data",
                "description": "Weather data collection and retrieval endpoints"
            },
            {
                "name": "Alerts",
                "description": "Alert management and configuration"
            },
            {
                "name": "System",
                "description": "System administration and health endpoints"
            },
            {
                "name": "Storage",
                "description": "Data storage and archival management"
            },
            {
                "name": "API Enhancement",
                "description": "Webhooks, exports, and real-time updates"
            },
            {
                "name": "Monitoring",
                "description": "Performance metrics and system monitoring"
            }
        ],
        "paths": {
            "/api/health": {
                "get": {
                    "tags": ["System"],
                    "summary": "Health Check",
                    "description": "Check application health status",
                    "responses": {
                        "200": {
                            "description": "System is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "healthy"},
                                            "app_name": {"type": "string"},
                                            "environment": {"type": "string"},
                                            "version": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/weather/current/{location}": {
                "get": {
                    "tags": ["Weather Data"],
                    "summary": "Get Current Weather",
                    "description": "Retrieve current weather data for a location",
                    "parameters": [
                        {
                            "name": "location",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Location name (e.g., 'Delhi')"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Current weather data",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "location": {"type": "string"},
                                            "temperature": {"type": "number"},
                                            "humidity": {"type": "number"},
                                            "wind_speed": {"type": "number"},
                                            "pressure": {"type": "number"},
                                            "description": {"type": "string"},
                                            "timestamp": {"type": "string", "format": "date-time"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "Location not found"}
                    }
                }
            },
            "/api/weather/alerts": {
                "get": {
                    "tags": ["Alerts"],
                    "summary": "Get All Alerts",
                    "description": "Retrieve all active alerts across all locations",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {"type": "integer", "default": 100},
                            "description": "Maximum number of alerts to return"
                        },
                        {
                            "name": "offset",
                            "in": "query",
                            "schema": {"type": "integer", "default": 0},
                            "description": "Pagination offset"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of alerts",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "location": {"type": "string"},
                                                "rule_id": {"type": "string"},
                                                "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                                                "status": {"type": "string", "enum": ["active", "acknowledged", "resolved"]},
                                                "timestamp": {"type": "string", "format": "date-time"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/export/alerts": {
                "get": {
                    "tags": ["API Enhancement"],
                    "summary": "Export Alerts",
                    "description": "Export alerts in multiple formats",
                    "parameters": [
                        {
                            "name": "format",
                            "in": "query",
                            "schema": {"type": "string", "enum": ["json", "csv", "jsonl"]},
                            "description": "Export format"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {"type": "integer", "default": 1000},
                            "description": "Maximum records to export"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Exported data",
                            "content": {
                                "application/json": {"schema": {"type": "object"}},
                                "text/csv": {"schema": {"type": "string"}},
                                "application/jsonl": {"schema": {"type": "string"}}
                            }
                        }
                    }
                }
            },
            "/api/monitoring/metrics/overview": {
                "get": {
                    "tags": ["Monitoring"],
                    "summary": "Get Metrics Overview",
                    "description": "Get overall system performance metrics",
                    "responses": {
                        "200": {
                            "description": "System metrics overview",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "performance": {"type": "object"},
                                            "system": {"type": "object"},
                                            "timestamp": {"type": "string", "format": "date-time"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/monitoring/health": {
                "get": {
                    "tags": ["Monitoring"],
                    "summary": "Get System Health",
                    "description": "Check health status of all system components",
                    "responses": {
                        "200": {
                            "description": "System health status",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"]},
                                            "checks": {"type": "array"},
                                            "summary": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "WeatherData": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "temperature": {"type": "number"},
                        "humidity": {"type": "number"},
                        "wind_speed": {"type": "number"},
                        "pressure": {"type": "number"},
                        "description": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"}
                    }
                },
                "Alert": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "location": {"type": "string"},
                        "rule_id": {"type": "string"},
                        "severity": {"type": "string"},
                        "status": {"type": "string"},
                        "message": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                        "status_code": {"type": "integer"}
                    }
                }
            },
            "securitySchemes": {
                "api_key": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                },
                "bearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
    return spec


def generate_html_swagger_ui() -> str:
    """Generate standalone Swagger UI HTML"""
    html = """<!DOCTYPE html>
<html>
  <head>
    <title>Real-Time Weather Pipeline - API Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
    <style>
      body { margin: 0; padding: 0; }
      .topbar { background-color: #fafafa; padding: 10px; border-bottom: 1px solid #dedede; }
      .topbar h1 { margin: 0; padding: 10px; font-size: 20px; }
    </style>
  </head>
  <body>
    <div class="topbar">
      <h1>🌤️ Real-Time Weather Pipeline API</h1>
    </div>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-standalone-preset.js"></script>
    <script>
      window.onload = function() {
        SwaggerUIBundle({
          url: "./openapi.json",
          dom_id: '#swagger-ui',
          presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
          ],
          layout: "StandaloneLayout"
        })
      }
    </script>
  </body>
</html>
"""
    return html


def generate_html_redoc() -> str:
    """Generate ReDoc HTML for API documentation"""
    html = """<!DOCTYPE html>
<html>
  <head>
    <title>Real-Time Weather Pipeline - API Reference</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
      body { margin: 0; padding: 0; }
    </style>
  </head>
  <body>
    <redoc spec-url="./openapi.json"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
  </body>
</html>
"""
    return html


def main():
    """Main function to generate documentation"""
    print("Generating API Documentation...")
    
    # Create docs directory
    docs_dir = Path("docs/api")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate OpenAPI spec
    spec = generate_openapi_spec()
    
    # Save as JSON
    json_path = docs_dir / "openapi.json"
    with open(json_path, "w") as f:
        json.dump(spec, f, indent=2)
    print(f"✓ OpenAPI JSON: {json_path}")
    
    # Save as YAML
    yaml_path = docs_dir / "openapi.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(spec, f, default_flow_style=False)
    print(f"✓ OpenAPI YAML: {yaml_path}")
    
    # Generate Swagger UI HTML
    swagger_html = generate_html_swagger_ui()
    swagger_path = docs_dir / "swagger.html"
    with open(swagger_path, "w") as f:
        f.write(swagger_html)
    print(f"✓ Swagger UI: {swagger_path}")
    
    # Generate ReDoc HTML
    redoc_html = generate_html_redoc()
    redoc_path = docs_dir / "redoc.html"
    with open(redoc_path, "w") as f:
        f.write(redoc_html)
    print(f"✓ ReDoc: {redoc_path}")
    
    # Create README
    readme_path = docs_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write("""# API Documentation

This directory contains API documentation for the Real-Time Weather Pipeline.

## Documentation Formats

- **interactive.html** - Interactive API explorer (Swagger UI)
- **reference.html** - API reference (ReDoc)
- **openapi.json** - OpenAPI 3.0.0 specification (JSON)
- **openapi.yaml** - OpenAPI 3.0.0 specification (YAML)

## Viewing Documentation

### Local Development
```bash
# Using Python HTTP server
cd docs/api
python -m http.server 8001
# Open http://localhost:8001/swagger.html
```

### Docker
```bash
# Documentation is served at /docs endpoint
curl http://localhost:8000/docs
```

## API Base URL

- Development: `http://localhost:8000`
- Production: `https://api.example.com`

## Authentication

The API uses API Key authentication (optional). Include the key in the header:
```
X-API-Key: your-api-key
```

## Rate Limiting

- 1000 requests per minute for general endpoints
- 100 requests per minute for export endpoints
- 10 requests per second for WebSocket connections

## Support

For API support, contact: api-support@example.com
""")
    print(f"✓ Documentation index: {readme_path}")
    
    print(f"\n✅ API documentation generated successfully!")
    print(f"📁 Documentation path: {docs_dir}")
    print(f"\nTo view the documentation:")
    print(f"  - Swagger UI: open {swagger_path}")
    print(f"  - ReDoc: open {redoc_path}")


if __name__ == "__main__":
    main()
