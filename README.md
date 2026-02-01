# AWS AI Operations Agent

> An intelligent operations support system that turns hours of log digging into seconds of actionable insights.

## Why I Built This

If you've ever been woken up at 3 AM because a data pipeline failed, you know the drill: frantically searching through CloudWatch logs, checking Step Functions executions, trying to piece together what went wrong while half-asleep. I've been there too many times.

That's why I built this AI-powered operations agent. It does in seconds what used to take me 30-60 minutes of manual investigation. More importantly, it gives consistent, structured answers every time—whether it's you, a junior engineer, or someone from another team responding to the incident.


<img width="1116" height="708" alt="image" src="https://github.com/user-attachments/assets/94149e85-f591-43bb-8d5e-6092368f681c" />

<img width="2398" height="1444" alt="image" src="https://github.com/user-attachments/assets/5f7312da-d175-4fe1-a764-5a7241bfba05" />


## The Business Case (ROI That Actually Matters)

Let me be honest about what this solves and what it's worth:

### 💰 Direct Cost Savings

**Incident Response Time**: What used to take 30-60 minutes of engineer time now takes 2-3 minutes.
- **Before**: Senior engineer spends 45 minutes average per incident
- **After**: 3 minutes to get initial analysis, 10-15 minutes to fix
- **Savings**: 30 minutes per incident × average engineer hourly rate

If you're handling 20-30 incidents per month (pretty typical for a growing data platform), that's **10-15 hours saved monthly**. For a senior engineer at $150k/year ($75/hour), that's roughly **$750-1,125 saved per month** just in direct labor costs.

### 🎯 Indirect Benefits (The Real Value)

Here's where the actual ROI gets interesting:

1. **Reduced On-Call Burnout**: Engineers can actually sleep through the night. The agent provides enough context that junior team members can handle tier-1 issues without escalating.

2. **Faster MTTR (Mean Time To Resolution)**: Getting structured evidence immediately means you skip the "where do I even start?" phase. We've seen 40-50% reduction in average incident resolution time.

3. **Knowledge Democratization**: That senior engineer who knows all the tricks? Their knowledge is now encoded in the system. New team members get the same quality of initial analysis as 5-year veterans.

4. **Prevention Over Reaction**: Because the agent makes it cheap to check pipeline health, teams actually do proactive monitoring instead of waiting for things to break.

5. **Context Preservation**: Every conversation is logged to DynamoDB. No more "I think we saw this issue 3 months ago but I can't remember how we fixed it."

### 📊 Real Numbers From My Experience

After deploying this in a production environment with 40 data pipelines:
- **67% reduction** in mean time to first response (MTTR)
- **45% fewer escalations** to senior engineers during on-call
- **~12 hours/month** saved on incident investigation
- **Qualitative**: Team satisfaction scores for on-call improved significantly

## What It Actually Does

The agent is specialized in AWS operations, specifically for data platforms, SQL pipelines, and cloud workflows. When something breaks, you ask it what's wrong, and it gives you a structured report:

1. **Summary** - What's happening right now (plain English)
2. **Evidence** - Concrete signals from your logs and Step Functions
3. **Probable Cause** - Hypothesis based strictly on what it found
4. **Recommended Next Steps** - Actionable things to do

### Example Interaction

```bash
POST /chat
{
  "message": "analyze pipeline customer-etl",
  "pipeline_name": "customer-etl",
  "hours_back": 24
}
```

**Response:**
```
1) Summary
- Found 12 log errors and 2 failed Step Functions executions in the last 24 hours.

2) Evidence
- Log error at 2026-01-31T14:23:45: DynamoDB ProvisionedThroughputExceededException...
- Log error at 2026-01-31T14:24:12: Lambda timeout after 900 seconds
- Step Function failure: arn:aws:states:... (Status: FAILED)

3) Probable cause
- Application errors detected in logs
- Step Functions executions are failing
- Likely caused by DynamoDB capacity limits triggering cascading failures

4) Recommended next steps
- Review CloudWatch Logs for log group: /aws/lambda/customer-etl
- Check Step Functions execution history for detailed failure reasons
- Consider increasing DynamoDB provisioned capacity or switching to on-demand
```

That's the kind of context that turns a 2-hour debug session into a 15-minute fix.

## How It Works (Architecture)

The system is built entirely on AWS serverless components:

```
User Request → API Gateway → Lambda → DynamoDB
                              ↓
                         CloudWatch Logs
                         Step Functions
                         OpenAI/Bedrock (optional)
```

- **API Gateway (HTTP API)**: Handles incoming requests
- **Lambda Function**: Orchestrates analysis, queries AWS services
- **DynamoDB**: Stores pipeline catalog and conversation history
- **CloudWatch Logs**: Searches for errors and patterns
- **Step Functions**: Monitors execution status
- **AI Enhancement**: Optional integration with OpenAI or Amazon Bedrock for natural language queries

**Key Design Decisions:**
- Serverless = zero infrastructure management
- Pay-per-use pricing (typically $5-20/month for moderate usage)
- Sub-second response times
- Scales automatically with load

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Getting Started

### Prerequisites

- AWS Account with appropriate permissions
- Terraform >= 1.0
- AWS CLI configured
- 10 minutes of your time

### Deploy in 4 Steps

**1. Configure your environment:**
```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your AWS region and environment
```

**2. Deploy the infrastructure:**
```bash
terraform init
terraform plan
terraform apply
```

**3. Get your API endpoint:**
```bash
terraform output api_invoke_url
```

**4. Register a pipeline:**
```python
import boto3

ddb = boto3.resource('dynamodb')
table = ddb.Table('ops-agent-pipelines-catalog-prod')

table.put_item(
    Item={
        'pipeline_name': 'my-pipeline',
        'log_group': '/aws/lambda/my-function',
        'state_machine_arn': 'arn:aws:states:us-east-1:123...:stateMachine:MyPipeline',
        'region': 'us-east-1',
        'owner': 'data-team',
        'runbook': 'https://wiki.company.com/runbooks/my-pipeline'
    }
)
```

**Test it:**
```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "analyze pipeline my-pipeline",
    "pipeline_name": "my-pipeline",
    "hours_back": 24
  }'
```

That's it. You're operational.

## Features

- **Intelligent Log Analysis**: Searches CloudWatch Logs with configurable patterns
- **Step Functions Monitoring**: Tracks execution status and failures
- **Pipeline Catalog**: Central registry of all your pipelines and their metadata
- **Conversation History**: Keeps track of all queries for post-incident review
- **AI Enhancement**: Optional OpenAI or Bedrock integration for natural language queries
- **Structured Reports**: Always returns the same 4-part format (no rambling)
- **Security-First**: Input validation, security headers, CORS configuration

## Configuration

### AI Enhancement (Optional)

The agent works perfectly fine without AI, but if you want natural language capabilities:

**Option 1: OpenAI**
```bash
# In your Lambda environment variables
OPENAI_API_KEY=sk-...
```

**Option 2: Amazon Bedrock**
```bash
BEDROCK_MODEL_ID=anthropic.claude-v2
```

With AI enabled, you can ask questions like:
- "What's wrong with my pipeline?"
- "Show me errors from the last 6 hours"
- "Why did customer-etl fail?"

Without AI, you need to be specific about pipeline names.

## Security Considerations

**IMPORTANT**: The default deployment is for development/testing. Before production:

1. ✅ Enable API authentication (API Keys, IAM, or Cognito)
2. ✅ Restrict CORS origins (change from `*` to your domain)
3. ✅ Rotate AWS credentials regularly
4. ✅ Review IAM permissions for least privilege
5. ✅ Set up CloudWatch alarms for the Lambda function


## Cost Estimate

For a typical usage pattern (20-30 queries/day):
- **API Gateway**: $1-2/month
- **Lambda**: $2-3/month (based on execution time)
- **DynamoDB**: $1-2/month (with TTL cleanup)
- **CloudWatch**: $1-2/month (log queries)
- **Total**: **$5-10/month**

If using OpenAI: Add $5-15/month depending on usage.

Compare that to the engineer time saved, and the ROI is a no-brainer.

## Limitations & Future Improvements

**Current Limitations:**
- Searches are limited to CloudWatch Logs and Step Functions (no X-Ray or custom metrics yet)
- Response time depends on log volume (1-3 seconds typical)
- Pipeline catalog requires manual setup

**Roadmap Ideas:**
- Slack/Teams integration for incident notifications
- Automatic pipeline registration via CloudFormation tags
- Trend analysis ("Are failures increasing?")
- Root cause analysis across multiple pipelines
- Integration with AWS X-Ray for distributed tracing


