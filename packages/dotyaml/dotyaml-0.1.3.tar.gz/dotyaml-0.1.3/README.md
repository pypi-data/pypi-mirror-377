# dotyaml

A Python library that bridges YAML configuration files and environment variables, providing the flexibility to configure applications using either approach.

## The Problem dotyaml Solves

When building applications, you often face a configuration dilemma:

**Environment variables** are great for deployment flexibility and security (keeping secrets out of code), but they can become disorganized and hard to manage. You end up with a flat list of variables like `DB_HOST`, `API_TIMEOUT`, `STRIPE_KEY`, `JWT_SECRET` with no clear structure or organization.

**YAML configuration files** provide excellent organization with nested sections, clear structure, and are easy for humans and AI coding agents to understand. However, they're not ideal for secrets management and deployment flexibility.

**dotyaml bridges this gap** by letting you have the best of both worlds:

### Structured Configuration with Automatic Environment Variable Generation

Define your configuration in organized YAML sections:

```yaml
database:
  host: localhost
  port: 5432
  name: myapp
api:
  timeout: 30
  retries: 3
stripe:
  publishable_key: pk_test_123
```

dotyaml automatically generates properly namespaced environment variables following a consistent pattern:
- `APP_DATABASE_HOST=localhost`
- `APP_DATABASE_PORT=5432`
- `APP_API_TIMEOUT=30`
- `APP_STRIPE_PUBLISHABLE_KEY=pk_test_123`

### Flexible Override System with Clear Precedence

The power comes from the precedence system - you can override any configuration value at multiple levels:

1. **Manual environment variables** (highest precedence) - Always win
2. **YAML configuration with environment variable interpolation** 
3. **Automatic .env file loading** (lowest precedence)

This means:
- **Development**: Use `.env` files for secrets and local overrides
- **Staging/Production**: Set environment variables directly to override anything
- **Team sharing**: Commit the YAML structure to git, keep secrets in `.env` (gitignored)
- **AI/tooling friendly**: The YAML structure clearly expresses your application's configuration needs

### Example: Secrets Management Made Simple

**.env file** (gitignored, contains secrets):
```bash
DB_PASSWORD=super_secret_123
STRIPE_SECRET_KEY=sk_live_real_key
```

**config.yaml** (committed to git, safe to share):
```yaml
database:
  host: "{{ DB_HOST|localhost }}"
  username: admin
  password: "{{ DB_PASSWORD }}"  # Comes from .env
stripe:
  secret_key: "{{ STRIPE_SECRET_KEY }}"  # Comes from .env
  webhook_endpoint: /webhooks/stripe
```

**Result**: Clean, organized configuration with secure secrets management and full deployment flexibility.

## Installation

```bash
pip install dotyaml
```

dotyaml automatically includes `python-dotenv` for `.env` file support and environment variable interpolation.

## Quick Start

Just like python-dotenv, dotyaml is designed to be simple to use. It automatically loads `.env` files and supports environment variable interpolation:

```python
from dotyaml import load_config

# Automatically loads .env file first, then processes YAML with variable interpolation
load_config('config.yaml')

# Now your app can access configuration via environment variables
import os
db_host = os.getenv('APP_DATABASE_HOST')
```

**Example with secrets management:**

**.env file** (keep secret):
```bash
DB_USERNAME=admin
DB_PASSWORD=secret123
```

**config.yaml file** (safe to commit):
```yaml
database:
  host: localhost
  username: "{{ DB_USERNAME }}"
  password: "{{ DB_PASSWORD }}"
```

## Basic Usage

### 1. Create a YAML configuration file

**config.yaml:**
```yaml
database:
  host: localhost
  port: 5432
  name: myapp
api:
  timeout: 30
  retries: 3
```

### 2. Load configuration in your Python application

```python
from dotyaml import load_config

# This will set environment variables based on your YAML structure
load_config('config.yaml', prefix='APP')

# Environment variables are now available:
# APP_DATABASE_HOST=localhost
# APP_DATABASE_PORT=5432
# APP_DATABASE_NAME=myapp
# APP_API_TIMEOUT=30
# APP_API_RETRIES=3
```

### 3. Use environment variables in your application

```python
import os

# Your application code remains simple and flexible
database_config = {
    'host': os.getenv('APP_DATABASE_HOST'),
    'port': int(os.getenv('APP_DATABASE_PORT')),
    'name': os.getenv('APP_DATABASE_NAME')
}
```

## Alternative: Environment Variables Only

Your application works the same way even without a YAML file:

```bash
# Set environment variables directly
export APP_DATABASE_HOST=prod-db.example.com
export APP_DATABASE_PORT=5432
export APP_DATABASE_NAME=production
export APP_API_TIMEOUT=60
export APP_API_RETRIES=5
```

```python
# Your application code doesn't change
import os
database_config = {
    'host': os.getenv('APP_DATABASE_HOST'),
    'port': int(os.getenv('APP_DATABASE_PORT')),
    'name': os.getenv('APP_DATABASE_NAME')
}
```

## Advanced Usage

### Environment Variable Precedence

Environment variables always take precedence over YAML values:

```python
# YAML file has database.host: localhost
# But environment variable is set:
os.environ['APP_DATABASE_HOST'] = 'prod-db.example.com'

load_config('config.yaml', prefix='APP')
# Result: APP_DATABASE_HOST=prod-db.example.com (env var wins)
```

### Force Override

Override existing environment variables with YAML values:

```python
load_config('config.yaml', prefix='APP', override=True)
```

### ConfigLoader for Advanced Use Cases

```python
from dotyaml import ConfigLoader

# Load configuration without setting environment variables
loader = ConfigLoader(prefix='APP')
config = loader.load_from_yaml('config.yaml')  # Returns dict

# Load configuration from environment variables only
env_config = loader.load_from_env()

# Set environment variables from configuration dict
loader.set_env_vars(config)
```

### Automatic .env File Loading and Environment Variable Interpolation

dotyaml automatically loads `.env` files and supports environment variable interpolation in YAML files using Jinja-like syntax. This is perfect for managing secrets securely:

#### Basic Environment Variable Interpolation

Use `{{ VARIABLE_NAME }}` syntax in your YAML files to interpolate environment variables:

```yaml
# config.yaml
database:
  host: localhost
  username: "{{ DB_USERNAME }}"
  password: "{{ DB_PASSWORD }}"
  name: myapp
api:
  key: "{{ API_SECRET_KEY }}"
  timeout: 30
```

```python
from dotyaml import load_config

# Automatically loads .env file first, then processes YAML with interpolation
config = load_config('config.yaml', prefix='APP')
```

#### Using Default Values

Provide default values using the pipe syntax `{{ VARIABLE_NAME|default_value }}`:

```yaml
# config.yaml
database:
  host: "{{ DB_HOST|localhost }}"
  username: "{{ DB_USERNAME|dev_user }}"
  password: "{{ DB_PASSWORD|dev_password }}"
  port: "{{ DB_PORT|5432 }}"
```

#### Recommended Pattern: Secrets in .env, Config in YAML

**Create `.env` file for secrets** (add to `.gitignore`):
```bash
# .env - Keep this file secret and out of version control!
DB_USERNAME=production_admin
DB_PASSWORD=super_secret_password_123!
API_SECRET_KEY=sk_live_abc123def456ghi789
JWT_SECRET=jwt_signing_secret_xyz789
```

**Create YAML config file** (safe to commit to git):
```yaml
# config.yaml - Safe to commit to version control
app:
  name: MyApp
  debug: false

database:
  host: "{{ DB_HOST|localhost }}"
  port: 5432
  username: "{{ DB_USERNAME }}"           # Required from .env
  password: "{{ DB_PASSWORD }}"           # Required from .env
  name: "{{ DB_NAME|myapp_production }}"
  ssl: true

api:
  secret_key: "{{ API_SECRET_KEY }}"      # Required from .env
  jwt_secret: "{{ JWT_SECRET }}"          # Required from .env
  timeout: 30
```

**Load in your application**:
```python
from dotyaml import load_config

# Automatically loads .env first, then interpolates variables in YAML
config = load_config('config.yaml', prefix='MYAPP')

# Your secrets are now available as environment variables:
# MYAPP_DATABASE_USERNAME=production_admin
# MYAPP_DATABASE_PASSWORD=super_secret_password_123!
# MYAPP_API_SECRET_KEY=sk_live_abc123def456ghi789
```

#### Advanced .env Integration

You can also customize .env file loading:

```python
from dotyaml import load_config

# Custom .env path
config = load_config('config.yaml', prefix='APP', dotenv_path='.env.production')

# Disable automatic .env loading
config = load_config('config.yaml', prefix='APP', load_dotenv_first=False)

# Custom .env path with ConfigLoader
from dotyaml import ConfigLoader
loader = ConfigLoader(prefix='APP', dotenv_path='.env.staging')
yaml_config = loader.load_from_yaml('config.yaml')
```

**Precedence order** (highest to lowest):
1. **Manually set environment variables** (highest precedence) - Never overridden
2. **Variables from `.env` file** (loaded automatically) - Only set if not already defined
3. **Interpolated values with defaults in YAML** - Uses existing env vars or defaults
4. **Regular YAML configuration values** (lowest precedence)

**Critical guarantee**: If you manually set any environment variable (either the final prefixed name like `APP_DATABASE_HOST` or an interpolation source like `DB_PASSWORD`), dotyaml will **never override it**. This ensures that manual configuration always takes precedence, whether set via command line, deployment scripts, or any other method.

This pattern gives you maximum flexibility and security:
- **Development**: Use `.env` for secrets and local overrides
- **Staging**: Use different `.env` files per environment
- **Production**: Use environment variables only (no `.env` file)
- **Security**: Keep secrets out of your git repository

### Data Type Handling

dotyaml automatically handles various YAML data types:

- **Strings**: Passed through as-is
- **Numbers**: Converted to string representations
- **Booleans**: Converted to `"true"`/`"false"`
- **Lists**: Converted to comma-separated strings
- **Null values**: Converted to empty strings

## License

MIT License - see [LICENSE](LICENSE) file for details.