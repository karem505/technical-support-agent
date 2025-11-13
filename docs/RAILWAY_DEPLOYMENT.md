# Railway Deployment Guide

This guide will help you deploy the Odoo Technical Support Agent on Railway.

## Prerequisites

- Railway account (sign up at https://railway.app)
- LiveKit Cloud account or self-hosted LiveKit server
- OpenAI API key
- Accessible Odoo instance

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure all changes are committed:

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Create a New Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your repository
5. Select your `technical-support-agent` repository

### 3. Configure Backend Service

Railway will automatically detect your project. You need to configure three services:

#### Backend API Service

1. Click "Add Service" → "New Service"
2. Name it "backend-api"
3. Set the root directory: `/backend`
4. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

5. Add environment variables:
```
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
OPENAI_API_KEY=your-openai-key
ODOO_HOST=your-odoo-host.com
ODOO_PORT=8069
ODOO_DB=your-database
ODOO_USERNAME=admin
ODOO_PASSWORD=your-password
```

6. Generate a domain for the service

#### Agent Service

1. Click "Add Service" → "New Service"
2. Name it "voice-agent"
3. Set the root directory: `/backend`
4. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m agent.agent`

5. Add the same environment variables as the backend API

#### Frontend Service

1. Click "Add Service" → "New Service"
2. Name it "frontend"
3. Set the root directory: `/frontend`
4. Configure build settings:
   - Build Command: `pnpm install && pnpm build`
   - Start Command: `pnpm start`

5. Add environment variables:
```
NEXT_PUBLIC_API_URL=https://your-backend-api.railway.app
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
```

6. Generate a domain for the service

### 4. Deploy

Railway will automatically deploy your services. Monitor the deployment logs to ensure everything starts correctly.

### 5. Verify Deployment

1. Open your frontend URL in a browser
2. Click "Start Voice Session"
3. Allow microphone access
4. Test the voice interaction

## Using Railway CLI

Alternatively, you can deploy using the Railway CLI:

### Install Railway CLI

```bash
npm i -g @railway/cli
```

### Login

```bash
railway login
```

### Initialize Project

```bash
railway init
```

### Link to Project

```bash
railway link
```

### Deploy Backend

```bash
cd backend
railway up
```

### Deploy Frontend

```bash
cd ../frontend
railway up
```

### Set Environment Variables

```bash
railway variables set LIVEKIT_URL=wss://your-server.livekit.cloud
railway variables set LIVEKIT_API_KEY=your-key
# ... set all other variables
```

## Setting Up LiveKit Cloud

If you don't have a LiveKit server:

1. Go to https://cloud.livekit.io
2. Sign up for an account
3. Create a new project
4. Copy your credentials:
   - LiveKit URL
   - API Key
   - API Secret

## Monitoring

### Viewing Logs

In Railway dashboard:
1. Select your service
2. Click on "Deployments"
3. Click on the latest deployment
4. View real-time logs

### Metrics

Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network traffic

## Scaling

Railway automatically scales based on demand. For production:

1. Go to service settings
2. Adjust replica count if needed
3. Configure autoscaling rules

## Custom Domain

To use a custom domain:

1. Go to service settings
2. Click "Generate Domain"
3. Add your custom domain
4. Configure DNS settings as shown

## Troubleshooting

### Build Failures

**Python dependencies fail:**
```bash
# Check requirements.txt for incompatible versions
# Railway uses Python 3.11 by default
```

**Node build fails:**
```bash
# Ensure package.json has correct scripts
# Check that all dependencies are listed
```

### Runtime Issues

**Service crashes immediately:**
- Check environment variables are set correctly
- View logs for error messages
- Verify external service connectivity (LiveKit, Odoo)

**Cannot connect to Odoo:**
- Ensure Odoo instance is publicly accessible
- Check firewall rules
- Verify credentials

**Voice not working:**
- Check OpenAI API key is valid
- Verify LiveKit credentials
- Ensure WSS connection is not blocked

### Environment Variables Not Loading

```bash
# Use Railway CLI to verify
railway variables

# Set missing variables
railway variables set KEY=value
```

## Cost Optimization

1. **Use appropriate instance sizes:**
   - Start with smallest instance
   - Scale up based on usage

2. **Monitor usage:**
   - Check Railway dashboard regularly
   - Set up billing alerts

3. **Optimize builds:**
   - Use build cache
   - Minimize dependencies

## Security Best Practices

1. **Never commit secrets:**
   - Use Railway environment variables
   - Keep `.env` in `.gitignore`

2. **Restrict CORS:**
   - Update `backend/api/main.py` with specific origins
   - Remove `allow_origins=["*"]` in production

3. **Use HTTPS:**
   - Railway provides HTTPS by default
   - Ensure all external connections use secure protocols

4. **Rotate credentials:**
   - Change API keys periodically
   - Update Railway variables after rotation

## Rollback

If deployment fails:

1. Go to service deployments
2. Find the last working deployment
3. Click "Redeploy"

## Database Backups

Important: The agent connects to your Odoo instance but doesn't store data. Ensure your Odoo instance has proper backups configured.

## Support

- Railway documentation: https://docs.railway.app
- Railway community: https://discord.gg/railway
- Project issues: Create an issue in your GitHub repository

## Next Steps

After successful deployment:

1. Test all features thoroughly
2. Set up monitoring and alerts
3. Configure custom domain
4. Implement usage analytics
5. Set up CI/CD pipeline
