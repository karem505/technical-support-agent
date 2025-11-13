# LiveKit Setup Guide

This guide covers setting up LiveKit for the Odoo Technical Support Agent.

## What is LiveKit?

LiveKit is an open-source WebRTC infrastructure for building real-time audio, video, and data applications. For this project, we use it for voice communication between users and the AI agent.

## Option 1: LiveKit Cloud (Recommended)

### Benefits
- No infrastructure management
- Global edge network
- Automatic scaling
- Built-in monitoring

### Setup Steps

1. **Create an Account**
   - Go to https://cloud.livekit.io
   - Sign up with your email or GitHub

2. **Create a Project**
   - Click "New Project"
   - Enter project name (e.g., "odoo-support-agent")
   - Select a region closest to your users

3. **Get Credentials**
   - Go to project settings
   - Copy the following:
     - **LiveKit URL**: `wss://your-project.livekit.cloud`
     - **API Key**: `APIxxxxxxxxxxxxxx`
     - **API Secret**: `secretxxxxxxxxxxxxxxxxx`

4. **Configure Your Application**

   Add to `.env`:
   ```env
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=APIxxxxxxxxxxxxxx
   LIVEKIT_API_SECRET=secretxxxxxxxxxxxxxxxxx
   ```

5. **Set Up Billing** (if needed)
   - Free tier includes 500 minutes/month
   - Upgrade for production use

## Option 2: Self-Hosted LiveKit

### Benefits
- Full control over infrastructure
- No usage limits
- Data stays on your servers

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

### Installation

#### Using Docker

1. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

2. **Create Configuration File**

   Create `livekit.yaml`:
   ```yaml
   port: 7880
   rtc:
     port_range_start: 50000
     port_range_end: 60000
     use_external_ip: true

   redis:
     address: localhost:6379

   room:
     auto_create: true
     empty_timeout: 300
     max_participants: 100

   keys:
     APIxxxxxx: secretxxxxxxxxxx  # Generate your own

   logging:
     level: info
     sample: false
   ```

3. **Generate API Key and Secret**
   ```bash
   # Use any secure method to generate
   API_KEY="API$(openssl rand -hex 8)"
   API_SECRET="$(openssl rand -hex 32)"
   echo "API Key: $API_KEY"
   echo "API Secret: $API_SECRET"
   ```

4. **Run LiveKit Server**
   ```bash
   docker run -d \
     --name livekit \
     -p 7880:7880 \
     -p 7881:7881 \
     -p 50000-60000:50000-60000/udp \
     -v $(pwd)/livekit.yaml:/livekit.yaml \
     livekit/livekit-server \
     --config /livekit.yaml
   ```

5. **Set Up Reverse Proxy (Nginx)**

   Create `/etc/nginx/sites-available/livekit`:
   ```nginx
   server {
       listen 443 ssl http2;
       server_name livekit.yourdomain.com;

       ssl_certificate /etc/letsencrypt/live/livekit.yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/livekit.yourdomain.com/privkey.pem;

       location / {
           proxy_pass http://localhost:7880;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

6. **Enable and Restart Nginx**
   ```bash
   sudo ln -s /etc/nginx/sites-available/livekit /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Configure Firewall**
   ```bash
   sudo ufw allow 443/tcp
   sudo ufw allow 7880/tcp
   sudo ufw allow 50000:60000/udp
   ```

#### Using Kubernetes

1. **Add Helm Repository**
   ```bash
   helm repo add livekit https://helm.livekit.io
   helm repo update
   ```

2. **Create Values File**

   Create `values.yaml`:
   ```yaml
   livekit:
     image:
       tag: latest

     config:
       port: 7880
       rtc:
         port_range_start: 50000
         port_range_end: 60000
       keys:
         APIxxxxxx: secretxxxxxxxxxx

   service:
     type: LoadBalancer

   ingress:
     enabled: true
     hosts:
       - host: livekit.yourdomain.com
         paths:
           - /
   ```

3. **Install**
   ```bash
   helm install livekit livekit/livekit-server -f values.yaml
   ```

## Testing Your LiveKit Setup

### Using LiveKit CLI

1. **Install CLI**
   ```bash
   brew install livekit  # macOS
   # or
   curl -sSL https://get.livekit.io/cli | bash  # Linux
   ```

2. **Create Room**
   ```bash
   livekit-cli create-room \
     --url $LIVEKIT_URL \
     --api-key $LIVEKIT_API_KEY \
     --api-secret $LIVEKIT_API_SECRET \
     --room test-room
   ```

3. **Generate Token**
   ```bash
   livekit-cli create-token \
     --url $LIVEKIT_URL \
     --api-key $LIVEKIT_API_KEY \
     --api-secret $LIVEKIT_API_SECRET \
     --room test-room \
     --identity test-user \
     --grant roomJoin
   ```

### Using the Backend API

```bash
curl -X POST http://localhost:8000/create-room \
  -H "Content-Type: application/json" \
  -d '{
    "room_name": "test-support-session",
    "participant_name": "test-user"
  }'
```

## Security Considerations

1. **API Credentials**
   - Never expose API key/secret in client-side code
   - Use environment variables
   - Rotate credentials periodically

2. **Token Generation**
   - Generate tokens server-side only
   - Set appropriate expiration times
   - Validate room permissions

3. **Network Security**
   - Use WSS (WebSocket Secure) in production
   - Configure proper CORS policies
   - Enable firewall rules

## Monitoring

### LiveKit Cloud

- Built-in dashboard shows:
  - Active rooms
  - Participant count
  - Usage statistics
  - Error rates

### Self-Hosted

1. **Enable Prometheus Metrics**

   Add to `livekit.yaml`:
   ```yaml
   prometheus:
     port: 6789
   ```

2. **Set Up Grafana**
   - Import LiveKit dashboard
   - Configure alerting

3. **Check Logs**
   ```bash
   docker logs livekit -f
   ```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to LiveKit server

**Solutions:**
- Verify URL format: `wss://` (not `ws://`) for production
- Check firewall allows WebSocket connections
- Verify SSL certificate is valid

### Audio Not Working

**Problem:** No audio in voice session

**Solutions:**
- Check browser microphone permissions
- Verify TURN server is configured (for NAT traversal)
- Test with different network (sometimes corporate firewalls block WebRTC)

### Token Errors

**Problem:** "Invalid token" error

**Solutions:**
- Verify API key and secret match
- Check token hasn't expired
- Ensure room name matches exactly

### High Latency

**Solutions:**
- Use edge servers closer to users (LiveKit Cloud)
- Enable TURN server for better connectivity
- Check server resources (CPU, bandwidth)

## Advanced Configuration

### TURN Server

For users behind strict firewalls:

1. **Add TURN Configuration**

   In `livekit.yaml`:
   ```yaml
   rtc:
     turn_servers:
       - urls:
           - turn:turn.yourdomain.com:3478
         username: turnuser
         credential: turnpassword
   ```

### Recording

To record sessions:

1. **Enable Recording**
   ```yaml
   room:
     recording:
       enabled: true
       output_dir: /recordings
   ```

2. **Access Recordings**
   - Configure storage (S3, local)
   - Set retention policies

## Cost Estimation

### LiveKit Cloud Pricing (approximate)

- Free tier: 500 minutes/month
- Pay-as-you-go: ~$0.015/minute
- Enterprise: Custom pricing

### Self-Hosted Costs

- Server: $20-100/month (depending on size)
- Bandwidth: Variable based on usage
- Maintenance: Time investment

## Resources

- LiveKit Documentation: https://docs.livekit.io
- LiveKit Examples: https://github.com/livekit/livekit-examples
- LiveKit Discord: https://livekit.io/discord
- LiveKit Cloud Status: https://status.livekit.io

## Next Steps

After setting up LiveKit:

1. Configure your application with LiveKit credentials
2. Test voice connectivity
3. Deploy your agent
4. Monitor usage and performance
5. Scale as needed
