# Example Prompts for Testing

## Working Prompts

### Basic Pipeline Analysis
```
analyze pipeline my-pipeline
```

```
check pipeline data-pipeline
```

```
show pipeline status for etl-pipeline
```

### Log Queries
```
check logs for my-pipeline
```

```
what errors occurred in data-pipeline
```

```
show recent errors for etl-pipeline
```

### With Time Range
```
analyze pipeline my-pipeline last 48 hours
```

```
check logs for data-pipeline in the last 12 hours
```

## Prompts That Need Pipeline Name in Settings

If you don't specify the pipeline name in the message, you need to set it in settings (⚙️):

1. Set "Pipeline Name" to your pipeline (e.g., `my-pipeline`)
2. Then you can use:
   - "Check logs"
   - "Analyze pipeline"
   - "Show errors"
   - "What happened?"

## Testing Without Real Pipeline

To test the chatbot without a real pipeline registered:

1. Use any pipeline name (it will show "no errors found")
2. Example: `analyze pipeline test-pipeline`
3. The agent will respond that no errors were found (expected behavior)

## Register a Real Pipeline

To test with real data, register a pipeline first:

```python
import boto3

ddb = boto3.resource('dynamodb')
table = ddb.Table('ops-agent-pipelines-catalog-prod')

table.put_item(
    Item={
        'pipeline_name': 'my-pipeline',
        'log_group': '/aws/lambda/my-function',
        'state_machine_arn': 'arn:aws:states:us-east-1:336751562831:stateMachine:MyStateMachine',
        'region': 'us-east-1',
        'owner': 'data-engineering-team',
        'runbook': 'https://wiki.company.com/runbooks/my-pipeline',
        'log_filter_pattern': 'ERROR Exception "error" "failed"'
    }
)
```

## Quick Test Prompts

Try these in order:

1. `analyze pipeline test-pipeline`
2. `check logs for test-pipeline`
3. `what errors in test-pipeline last 24 hours`
