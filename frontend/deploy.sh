#!/bin/bash

# Deploy frontend to S3
# Usage: ./deploy.sh [bucket-name] [region]

BUCKET_NAME=${1:-"ops-agent-frontend-prod"}
REGION=${2:-"us-east-1"}

echo "Deploying frontend to S3..."
echo "Bucket: $BUCKET_NAME"
echo "Region: $REGION"
echo ""

# Check if bucket exists
if ! aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Bucket exists, syncing files..."
else
    echo "Creating bucket..."
    aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"
    
    # Enable static website hosting
    aws s3 website "s3://$BUCKET_NAME" \
        --index-document index.html \
        --error-document index.html
fi

# Upload files
echo "Uploading files..."
aws s3 sync . "s3://$BUCKET_NAME" \
    --exclude "*.sh" \
    --exclude "README.md" \
    --exclude ".git/*" \
    --delete \
    --region "$REGION"

# Set public read permissions
echo "Setting permissions..."
aws s3 cp "s3://$BUCKET_NAME/index.html" "s3://$BUCKET_NAME/index.html" \
    --acl public-read \
    --region "$REGION"

echo ""
echo "Deployment complete!"
echo "Website URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo ""
echo "To use CloudFront for HTTPS:"
echo "1. Create CloudFront distribution"
echo "2. Set origin to: $BUCKET_NAME.s3.amazonaws.com"
echo "3. Set default root object to: index.html"
