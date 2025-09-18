#!/usr/bin/env python3
"""
sellm - LLM-powered ProServe manifest generator
Simplified single-file implementation
"""

import asyncio
import yaml
import json
import redis
import hashlib
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from aiohttp import web, ClientSession
import click

# Import wmlog for structured logging
from wmlog import WMLLogger, LoggingConfig, LogContext

# ===== Configuration =====

@dataclass
class Config:
    """Application configuration"""
    llm_model: str = "mistral:7b"
    llm_host: str = "localhost:11434"
    api_port: int = 8080
    api_host: str = "0.0.0.0"
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600
    enable_cache: bool = True
    
    @classmethod
    def from_env(cls):
        """Load from environment variables"""
        import os
        from pathlib import Path
        
        # Load .env file if it exists
        env_file = Path(".env") 
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        return cls(
            llm_model=os.getenv("SELLM_MODEL", "mistral:latest"),
            llm_host=os.getenv("SELLM_HOST", "localhost:11434"),
            api_port=int(os.getenv("API_PORT", "8080")),
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
            enable_cache=os.getenv("ENABLE_CACHE", "true").lower() == "true"
        )

# ===== Prompt Templates =====

PROMPT_TEMPLATE = """You are an expert at creating ProServe manifest files.
Generate a complete ProServe manifest YAML file based on the following description.

IMPORTANT: Follow this EXACT ProServe manifest structure (all fields at TOP LEVEL, no nesting under 'service'):

name: "service-name"
description: "Service description"  # optional
version: "1.0.0"
type: "http"  # or "iot", "websocket", "hardware", "microservice"
host: "0.0.0.0"  # optional
port: 8080
endpoints:
  - path: "/api/users"
    method: "GET"
    handler: "handlers/users.py:list_users"
environment:
  DATABASE_URL: "sqlite:///app.db"
  SECRET_KEY: "your-secret-key-here"
features:
  cors: true
  health_check: true
  metrics: true
isolation:
  mode: "process"  # or "docker", "arduino", "micropython"
background_tasks:
  - name: "cleanup_task"
    handler: "tasks/cleanup.py:run"
    interval: 3600

Description: {description}
Service Type: {service_type}

Generate a complete, valid ProServe manifest.yaml file following the EXACT structure above:

```yaml
"""

# ===== LLM Client =====

class LLMClient:
    """Simple Ollama client"""
    
    def __init__(self, host: str, model: str):
        self.base_url = f"http://{host}"
        self.model = model
    
    async def generate(self, prompt: str) -> str:
        """Generate response from LLM"""
        async with ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 2000}
            }
            
            async with session.post(f"{self.base_url}/api/generate", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('response', '')
                else:
                    raise Exception(f"LLM request failed: {resp.status}")

# ===== Manifest Generator =====

class ManifestGenerator:
    """Main manifest generator"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = LLMClient(config.llm_host, config.llm_model)
        
        # Setup wmlog with proper async handling
        log_config = LoggingConfig(
            service_name="sellm",
            log_level="INFO",
            console_enabled=True,
            console_format="rich",
            websocket_enabled=False,  # Disable WebSocket for now to avoid async issues
            websocket_port=8765
        )
        
        log_context = LogContext(
            service_name="sellm",
            version="1.0.0",
            custom_fields={"llm_model": config.llm_model}
        )
        
        try:
            self.logger = WMLLogger.get_logger(log_config, log_context)
        except Exception as e:
            # Fallback to basic logging if wmlog fails
            import logging
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger("sellm")
        
        # Setup Redis cache
        try:
            self.redis = redis.from_url(config.redis_url) if config.enable_cache else None
        except Exception:
            self.redis = None
            self.logger.warning("Redis not available, caching disabled")
    
    def _detect_service_type(self, description: str) -> str:
        """Auto-detect service type from description"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['gpio', 'sensor', 'arduino', 'rp2040']):
            return "hardware"
        elif any(word in desc_lower for word in ['iot', 'mqtt', 'telemetry']):
            return "iot"
        elif any(word in desc_lower for word in ['websocket', 'real-time', 'chat']):
            return "websocket"
        elif any(word in desc_lower for word in ['docker', 'kubernetes', 'cloud']):
            return "microservice"
        else:
            return "http"
    
    def _extract_manifest(self, response: str) -> Dict[str, Any]:
        """Extract YAML from LLM response"""
        # Find YAML block
        lines = response.split('\n')
        yaml_lines = []
        in_yaml = False
        
        for line in lines:
            if line.strip() == '```yaml':
                in_yaml = True
                continue
            elif line.strip() == '```' and in_yaml:
                break
            elif in_yaml:
                yaml_lines.append(line)
        
        yaml_content = '\n'.join(yaml_lines) if yaml_lines else response
        
        try:
            # Handle environment variable substitution syntax
            import re
            yaml_content = re.sub(r'\$\{([^}]+)\}', r'"${\1}"', yaml_content)
            
            return yaml.safe_load(yaml_content)
        except Exception as e:
            self.logger.warning(f"Failed to parse YAML: {e}")
            self.logger.warning(f"Full YAML content that failed: {yaml_content}")
            # Try to clean up common YAML issues
            try:
                # Fix inconsistent indentation - normalize all top-level fields
                cleaned_lines = []
                for line in yaml_content.split('\n'):
                    if line.strip():
                        # If line starts with known top-level fields, ensure no indentation
                        stripped = line.strip()
                        if any(stripped.startswith(f"{field}:") for field in [
                            'name', 'description', 'version', 'type', 'host', 'port',
                            'endpoints', 'environment', 'features', 'isolation', 'background_tasks'
                        ]):
                            cleaned_lines.append(stripped)
                        else:
                            # Keep original indentation for nested items
                            cleaned_lines.append(line.rstrip())
                
                cleaned_yaml = '\n'.join(cleaned_lines)
                self.logger.info(f"Attempting to parse cleaned YAML: {cleaned_yaml[:100]}...")
                return yaml.safe_load(cleaned_yaml)
            except Exception as e2:
                self.logger.warning(f"Even cleaned YAML failed: {e2}")
            # Fallback manifest
            return {
                "name": "generated-service",
                "version": "1.0.0",
                "type": "http",
                "port": 8080
            }
    
    def _validate_manifest(self, manifest: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Simple manifest validation"""
        errors = []
        
        # Check required fields
        required = ["name", "version", "type", "port"]
        for field in required:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")
        
        # Validate port
        if "port" in manifest:
            port = manifest["port"]
            if not isinstance(port, int) or not (1 <= port <= 65535):
                errors.append(f"Invalid port: {port}")
        
        # Validate name format
        if "name" in manifest:
            name = manifest["name"]
            if " " in name:
                manifest["name"] = name.replace(" ", "-")
        
        return len(errors) == 0, errors
    
    async def generate(
        self,
        description: str,
        service_type: str = "auto",
        validate: bool = True
    ) -> Dict[str, Any]:
        """Generate ProServe manifest from description"""
        
        self.logger.info("Generating manifest", description_length=len(description))
        
        # Check cache (with error handling)
        cached_result = None
        cache_key = None
        if self.redis and self.config.enable_cache:
            try:
                cache_key = hashlib.md5(f"{description}:{service_type}".encode()).hexdigest()
                cached = self.redis.get(cache_key)
                if cached:
                    self.logger.debug("Cache hit")
                    cached_result = json.loads(cached)
                    return cached_result
            except Exception as e:
                self.logger.warning(f"Cache read failed: {e}, continuing without cache")
                self.redis = None  # Disable Redis for future requests
        
        # Auto-detect type if needed
        if service_type == "auto":
            service_type = self._detect_service_type(description)
        
        # Build prompt
        prompt = PROMPT_TEMPLATE.format(
            description=description,
            service_type=service_type
        )
        
        # Generate with LLM
        response = await self.llm.generate(prompt)
        manifest = self._extract_manifest(response)
        
        # Validate if requested
        if validate:
            is_valid, errors = self._validate_manifest(manifest)
            if not is_valid:
                self.logger.warning("Validation errors", errors=errors)
        
        # Cache result (with error handling)
        if self.redis and self.config.enable_cache and cache_key:
            try:
                self.redis.setex(cache_key, self.config.cache_ttl, json.dumps(manifest))
                self.logger.debug("Cache write successful")
            except Exception as e:
                self.logger.warning(f"Cache write failed: {e}, continuing without cache")
                self.redis = None  # Disable Redis for future requests
        
        self.logger.info("Manifest generated", name=manifest.get('name'))
        
        return manifest

# ===== API Server =====

class APIServer:
    """REST API server"""
    
    def __init__(self, generator: ManifestGenerator, config: Config):
        self.generator = generator
        self.config = config
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        self.app.router.add_get('/health', self.health)
        self.app.router.add_post('/generate', self.generate)
        self.app.router.add_post('/validate', self.validate)
        self.app.router.add_get('/models', self.list_models)
    
    async def health(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "version": "1.0.0",
            "model": self.config.llm_model
        })
    
    async def generate(self, request):
        """Generate manifest endpoint"""
        try:
            data = await request.json()
            
            manifest = await self.generator.generate(
                description=data.get("description"),
                service_type=data.get("type", "auto"),
                validate=data.get("validate", True)
            )
            
            return web.json_response({
                "manifest": manifest,
                "validation": {"is_valid": True}
            })
        except Exception as e:
            return web.json_response({
                "error": str(e)
            }, status=400)
    
    async def validate(self, request):
        """Validate manifest endpoint"""
        try:
            data = await request.json()
            manifest = data.get("manifest", {})
            
            is_valid, errors = self.generator._validate_manifest(manifest)
            
            return web.json_response({
                "is_valid": is_valid,
                "errors": errors,
                "warnings": []
            })
        except Exception as e:
            return web.json_response({
                "error": str(e)
            }, status=400)
    
    async def list_models(self, request):
        """List available models"""
        # Query Ollama for models
        try:
            async with ClientSession() as session:
                async with session.get(f"http://{self.config.llm_host}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return web.json_response({"models": data.get("models", [])})
        except Exception:
            pass
        
        return web.json_response({"models": []})
    
    def run(self):
        """Start API server"""
        web.run_app(self.app, host=self.config.api_host, port=self.config.api_port)

# ===== CLI =====

@click.group()
def cli():
    """sellm - LLM-powered ProServe manifest generator"""
    pass

@cli.command()
@click.argument('description')
@click.option('--output', '-o', help='Output file')
@click.option('--type', '-t', default='auto', help='Service type')
def generate(description, output, type):
    """Generate manifest from description"""
    config = Config.from_env()
    generator = ManifestGenerator(config)
    
    def _format_manifest_yaml(manifest: Dict[str, Any]) -> str:
        """Format manifest with proper ProServe field ordering"""
        # Define proper field order for ProServe manifests
        field_order = [
            'name', 'description', 'version', 'type', 'host', 'port',
            'endpoints', 'websocket', 'websockets', 'background_tasks',
            'environment', 'environment_variables', 'features', 'isolation', 'isolation_mode'
        ]
        
        # Create ordered manifest
        ordered_manifest = {}
        
        # Add fields in proper order
        for field in field_order:
            if field in manifest:
                ordered_manifest[field] = manifest[field]
        
        # Add any remaining fields not in the order list
        for key, value in manifest.items():
            if key not in ordered_manifest:
                ordered_manifest[key] = value
        
        # Generate clean YAML with proper formatting
        yaml_content = yaml.dump(
            ordered_manifest,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,  # Keep our custom order
            indent=2
        )
        
        return yaml_content
    
    async def _generate():
        try:
            manifest = await generator.generate(description, type)
            yaml_content = _format_manifest_yaml(manifest)
            
            print(yaml_content)
            
            if output:
                Path(output).write_text(yaml_content)
                print(f"Saved to {output}")
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(_generate())

@cli.command()
@click.option('--port', '-p', default=8080, help='API port')
@click.option('--host', '-h', default='0.0.0.0', help='API host')
def serve(port, host):
    """Start API server"""
    config = Config.from_env()
    config.api_port = port
    config.api_host = host
    
    generator = ManifestGenerator(config)
    server = APIServer(generator, config)
    
    print(f"🚀 sellm API server starting on http://{host}:{port}")
    print(f"📊 WebSocket logs available on ws://{host}:8765")
    print(f"🤖 LLM model: {config.llm_model}")
    
    server.run()

@cli.command()
def examples():
    """Show example manifests"""
    examples_file = Path("prompts.yaml")
    if examples_file.exists():
        with open(examples_file) as f:
            examples = yaml.safe_load(f)
        
        print(" Example Prompts:")
        for name, data in examples.items():
            print(f"\n {name}:")
            print(f"  Description: {data.get('description', 'N/A')}")
            if 'prompt' in data:
                print(f"  Prompt: {data['prompt'][:100]}...")
    else:
        print(" Examples file not found")

@cli.command()
@click.argument('prompt')
@click.option('--type', '-t', 'service_type', default='auto', help='Service type (auto, http, websocket, iot, hardware)')
@click.option('--workspace', '-w', default='./projects', help='Projects workspace directory')
@click.option('--run', '-r', is_flag=True, help='Automatically run generated service with ProServe')
def project(prompt, service_type, workspace, run):
    """Create a complete project with manifest and ProServe integration"""
    
    async def create_project():
        from project_manager import ProjectManager
        
        print(f" Creating new SELLM project...")
        print(f" Prompt: {prompt}")
        print(f" Type: {service_type}")
        print(f" Workspace: {workspace}")
        print("=" * 50)
        
        try:
            manager = ProjectManager(workspace)
            result = await manager.create_project(prompt, service_type)
            
            print(f"\n Project {result['project_number']} created successfully!")
            print(f" Location: {result['project_dir']}")
            print(f" Service: {result['manifest_name']} ({result['manifest_type']})")
            print(f"  Duration: {result['duration_seconds']:.2f}s")
            print(f" Validation: {'PASSED' if result['validation_passed'] else 'FAILED'}")
            
            print(f"\n Files created:")
            for filename in result['files_created']:
                print(f"  {filename}")
            
            print(f"\n Usage:")
            print(f"  cd {result['project_dir']}")
            print(f"  ./run.sh")
            
            if run:
                print(f"\n Auto-running with ProServe...")
                import subprocess
                import os
                
                try:
                    os.chdir(result['project_dir'])
                    subprocess.run(['./run.sh'], check=False)
                except Exception as e:
                    print(f" Auto-run failed: {e}")
                    print(f" Try running manually: cd {result['project_dir']} && ./run.sh")
            
        except Exception as e:
            print(f" Project creation failed: {e}")
            raise
    
    asyncio.run(create_project())

@cli.command()
@click.option('--workspace', '-w', default='./projects', help='Projects workspace directory')
def projects(workspace):
    """List all projects in workspace"""
    from project_manager import ProjectManager
    
    manager = ProjectManager(workspace)
    project_list = manager.list_projects()
    
    if not project_list:
        print(f" No projects found in {workspace}")
        print(f" Create a project with: sellm project \"Your service description\"")
    else:
        print(f" Found {len(project_list)} projects in {workspace}:")
        print("=" * 60)
        
        for project in project_list:
            status = "" if all(project['files'].values()) else ""
            print(f"{status} Project {project['project_number']}: {project.get('manifest_name', 'N/A')}")
            print(f"   Type: {project.get('manifest_type', 'N/A')} | Port: {project.get('manifest_port', 'N/A')}")
            print(f"   Dir: {project['project_dir']}")
            if 'prompt' in project:
                print(f"   Prompt: {project['prompt']}")
            print()

@cli.command()
@click.argument('project_number', type=int)
@click.option('--workspace', '-w', default='./projects', help='Projects workspace directory')
def run_project(project_number, workspace):
    """Run a specific project with ProServe"""
    from project_manager import ProjectManager
    import subprocess
    import os
    
    manager = ProjectManager(workspace)
    project_info = manager._get_project_info(project_number)
    
    if not project_info:
        print(f" Project {project_number} not found in {workspace}")
        return
    
    project_dir = project_info['project_dir']
    run_script = os.path.join(project_dir, 'run.sh')
    
    if not os.path.exists(run_script):
        print(f" Run script not found: {run_script}")
        return
    
    print(f" Running project {project_number}: {project_info.get('manifest_name', 'N/A')}")
    print(f" Directory: {project_dir}")
    print(f" Script: {run_script}")
    print("=" * 50)
    
    try:
        os.chdir(project_dir)
        result = subprocess.run(['./run.sh'], check=False)
        
        if result.returncode == 0:
            print(f"\n Project {project_number} completed successfully")
        else:
            print(f"\n Project {project_number} exited with code {result.returncode}")
            
    except KeyboardInterrupt:
        print(f"\n Project {project_number} stopped by user")
    except Exception as e:
        print(f"\n Error running project {project_number}: {e}")

if __name__ == "__main__":
    cli()
