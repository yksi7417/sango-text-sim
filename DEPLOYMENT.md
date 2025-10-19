# Deploying Sango Text Sim to Fly.io

This guide will help you deploy the game to Fly.io.

## Prerequisites

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly.io**
   ```bash
   fly auth login
   ```

3. **Create Fly.io account** if you don't have one (free tier available)

## Quick Deploy

### Option 1: Using Existing Configuration

```bash
# Deploy the app
fly deploy

# Open the deployed app
fly open
```

### Option 2: Fresh Setup

```bash
# Launch a new app (creates fly.toml)
fly launch

# Follow the prompts:
# - Choose app name (or use auto-generated)
# - Choose region (closest to your users)
# - Don't add PostgreSQL database (not needed)
# - Don't add Redis (not needed for basic deployment)
# - Deploy now? Yes

# Your app will be deployed!
```

## Configuration

### fly.toml

The `fly.toml` file contains the deployment configuration:
- **app**: Your app name on Fly.io
- **primary_region**: Server location (lax, ord, fra, etc.)
- **internal_port**: 8080 (Flask app port)
- **vm**: Minimal resources (256MB RAM, 1 shared CPU)

### Environment Variables

Set secrets in Fly.io (not in fly.toml for security):

```bash
# Set Flask secret key
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
```

## Deployment Commands

### Deploy Updates

```bash
# Deploy latest changes
fly deploy

# Deploy with verbose output
fly deploy --verbose

# Deploy specific Dockerfile
fly deploy --dockerfile Dockerfile
```

### Monitor Deployment

```bash
# View logs
fly logs

# Check app status
fly status

# Open app in browser
fly open

# View app dashboard
fly dashboard
```

### Scale Resources

```bash
# Scale VM size
fly scale vm shared-cpu-1x --memory 512

# Scale number of instances
fly scale count 2

# Auto-scale (scale to zero when idle)
fly autoscale balanced min=0 max=3
```

## Troubleshooting

### Python Version Error (mise/asdf)

If you get the error about Python 3.8 installation failing:

**Solution 1: Use Dockerfile (Recommended)**
- The Dockerfile uses Python 3.11 official image
- No `mise` or version managers needed
- More reliable and faster builds

**Solution 2: Update Python Version**
```bash
# Edit .python-version
echo "3.11" > .python-version

# Or in fly.toml, set:
[build.args]
  PYTHON_VERSION = "3.11"
```

### Build Failures

```bash
# View detailed build logs
fly deploy --verbose

# Check Dockerfile syntax
docker build -t sango-test .

# Test locally with Docker
docker run -p 8080:8080 sango-test
```

### App Not Starting

```bash
# Check logs
fly logs

# Check health endpoint
curl https://your-app.fly.dev/health

# SSH into container
fly ssh console
```

### Port Issues

Make sure:
- Dockerfile exposes port 8080
- web_server.py uses PORT environment variable
- fly.toml internal_port matches (8080)

## Local Testing

Test the Docker container locally before deploying:

```bash
# Build image
docker build -t sango-text-sim .

# Run container
docker run -p 8080:8080 sango-text-sim

# Test in browser
# Navigate to http://localhost:8080
```

## Costs

Fly.io free tier includes:
- Up to 3 shared-cpu-1x 256MB VMs
- 160GB outbound data transfer
- Auto-sleep when idle (saves resources)

This app should run entirely on the free tier!

## Advanced Configuration

### Custom Domain

```bash
# Add custom domain
fly certs add yourdomain.com

# Get DNS records to configure
fly certs show yourdomain.com
```

### Persistent Storage (for save files)

```bash
# Create volume
fly volumes create sango_data --size 1

# Update fly.toml
[[mounts]]
  source = "sango_data"
  destination = "/data"
```

### Multiple Regions

```bash
# Add instances in different regions
fly regions add lax ord fra

# Fly will automatically route users to nearest region
```

## CI/CD Integration

See `CICD.md` for GitHub Actions integration.

## Useful Links

- [Fly.io Documentation](https://fly.io/docs/)
- [Python on Fly.io](https://fly.io/docs/languages-and-frameworks/python/)
- [Fly.io Dashboard](https://fly.io/dashboard)
- [Fly.io Community](https://community.fly.io/)

## Support

If you encounter issues:
1. Check `fly logs`
2. Visit Fly.io community forum
3. Check this project's GitHub issues
