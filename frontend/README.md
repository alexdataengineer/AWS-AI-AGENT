# Operations Agent Frontend

Modern web interface for the AWS Operations Agent chatbot.

## Features

- Real-time chat interface
- Pipeline analysis queries
- Log error checking
- Responsive design
- Configuration panel
- Quick action buttons

## Usage

### Local Development

1. Open `index.html` in a web browser
2. Configure API endpoint in settings (gear icon)
3. Set pipeline name and time range
4. Start chatting!

### Production Deployment

#### Option 1: Static Hosting (S3 + CloudFront)

```bash
# Build and upload to S3
aws s3 sync frontend/ s3://your-bucket-name/ops-agent/ --delete

# Enable static website hosting
aws s3 website s3://your-bucket-name/ --index-document ops-agent/index.html

# Or use CloudFront for HTTPS
```

#### Option 2: Simple HTTP Server

```bash
cd frontend
python3 -m http.server 8000
# Open http://localhost:8000
```

#### Option 3: Deploy to AWS Amplify

1. Connect your repository to AWS Amplify
2. Set build settings:
   - Build command: (none needed for static site)
   - Output directory: `frontend`
3. Deploy

## Configuration

The frontend stores configuration in browser localStorage:
- `apiUrl`: API Gateway endpoint
- `pipelineName`: Default pipeline name
- `hoursBack`: Default time range in hours

## API Integration

The frontend calls the Operations Agent API:

```javascript
POST /chat
{
  "message": "analyze pipeline my-pipeline",
  "pipeline_name": "my-pipeline",
  "hours_back": 24
}
```

## Customization

### Change API Endpoint

Edit `app.js`:
```javascript
const CONFIG = {
    apiUrl: 'https://your-api-id.execute-api.us-east-1.amazonaws.com',
    // ...
};
```

### Styling

Edit `styles.css` to customize colors, fonts, and layout.

### Features

Add new quick actions in `app.js`:
```javascript
case 'new-action':
    message = 'Your custom message';
    break;
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Security Notes

- API endpoint is configurable (no hardcoded URLs)
- CORS must be configured on API Gateway
- Consider adding API key authentication for production
