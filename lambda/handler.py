"""
Operations Agent Lambda Handler
Handles chat requests and orchestrates pipeline analysis.
"""
import json
import os
import boto3
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Tuple

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ddb = boto3.resource('dynamodb')
logs_client = boto3.client('logs')
sfn_client = boto3.client('stepfunctions')
bedrock_client = boto3.client('bedrock-runtime', region_name=os.getenv('DEFAULT_REGION', 'us-east-1'))

# Environment variables
CONVERSATIONS_TABLE = os.getenv('DDB_CONVERSATIONS_TABLE')
PIPELINES_TABLE = os.getenv('DDB_PIPELINES_TABLE')
DEFAULT_REGION = os.getenv('DEFAULT_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', '')
# Support both OPENAI_API_KEY and OPEN_AI_AGENT for compatibility
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or os.getenv('OPEN_AI_AGENT', '')

# DynamoDB tables
conversations_table = ddb.Table(CONVERSATIONS_TABLE) if CONVERSATIONS_TABLE else None
pipelines_table = ddb.Table(PIPELINES_TABLE) if PIPELINES_TABLE else None


def get_pipeline_info(pipeline_name: str) -> Optional[Dict[str, Any]]:
    """Get pipeline information from catalog."""
    if not pipelines_table:
        return None
    
    try:
        response = pipelines_table.get_item(
            Key={'pipeline_name': pipeline_name}
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting pipeline info: {str(e)}", exc_info=True)
        return None


def save_conversation(conversation_id: str, user_message: str, agent_response: str):
    """Save conversation to DynamoDB."""
    if not conversations_table:
        return
    
    try:
        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        ttl = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())
        
        conversations_table.put_item(
            Item={
                'conversation_id': conversation_id,
                'timestamp': timestamp,
                'user_message': user_message,
                'agent_response': agent_response,
                'ttl': ttl
            }
        )
    except Exception as e:
        logger.error(f"Error saving conversation: {str(e)}", exc_info=True)


def search_cloudwatch_logs(
    log_group: str,
    hours_back: int = 24,
    filter_pattern: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search CloudWatch Logs for errors."""
    try:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        kwargs = {
            'logGroupName': log_group,
            'startTime': int(start_time.timestamp() * 1000),
            'endTime': int(end_time.timestamp() * 1000),
            'limit': 50
        }
        
        if filter_pattern:
            kwargs['filterPattern'] = filter_pattern
        
        response = logs_client.filter_log_events(**kwargs)
        return response.get('events', [])
    except Exception as e:
        logger.error(f"Error searching logs: {str(e)}", exc_info=True)
        return []


def get_step_function_execution(execution_arn: str) -> Optional[Dict[str, Any]]:
    """Get Step Functions execution details."""
    try:
        response = sfn_client.describe_execution(executionArn=execution_arn)
        return response
    except Exception as e:
        logger.error(f"Error getting execution: {str(e)}", exc_info=True)
        return None


def list_step_function_executions(
    state_machine_arn: Optional[str] = None,
    status_filter: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """List Step Functions executions."""
    try:
        kwargs = {'maxResults': max_results}
        
        if state_machine_arn:
            kwargs['stateMachineArn'] = state_machine_arn
        if status_filter:
            kwargs['statusFilter'] = status_filter
        
        response = sfn_client.list_executions(**kwargs)
        return response.get('executions', [])
    except Exception as e:
        logger.error(f"Error listing executions: {str(e)}", exc_info=True)
        return []


def analyze_pipeline(pipeline_name: str, hours_back: int = 24) -> Dict[str, Any]:
    """Analyze pipeline and return structured report."""
    pipeline_info = get_pipeline_info(pipeline_name)
    
    report = {
        'pipeline_name': pipeline_name,
        'time_range_hours': hours_back,
        'summary': '',
        'evidence': [],
        'probable_cause': [],
        'recommendations': []
    }
    
    # Search logs if log group is available
    if pipeline_info and pipeline_info.get('log_group'):
        log_group = pipeline_info['log_group']
        # Use custom filter pattern from catalog, or default
        filter_pattern = pipeline_info.get('log_filter_pattern', 'ERROR Exception "error" "failed" "failure"')
        errors = search_cloudwatch_logs(
            log_group,
            hours_back,
            filter_pattern=filter_pattern
        )
        
        for event in errors[:10]:
            report['evidence'].append({
                'type': 'log_error',
                'timestamp': datetime.fromtimestamp(event['timestamp']/1000).isoformat(),
                'message': event.get('message', '')[:500]
            })
    
    # Check Step Functions if state machine ARN is available
    if pipeline_info and pipeline_info.get('state_machine_arn'):
        state_machine_arn = pipeline_info['state_machine_arn']
        failed_executions = list_step_function_executions(
            state_machine_arn=state_machine_arn,
            status_filter='FAILED',
            max_results=5
        )
        
        for execution in failed_executions:
            report['evidence'].append({
                'type': 'step_function_failure',
                'execution_arn': execution['executionArn'],
                'status': execution['status'],
                'start_date': execution['startDate'].isoformat() if 'startDate' in execution else None
            })
    
    # Generate summary
    if report['evidence']:
        error_count = len([e for e in report['evidence'] if e['type'] == 'log_error'])
        sfn_failures = len([e for e in report['evidence'] if e['type'] == 'step_function_failure'])
        
        report['summary'] = f"Found {error_count} log errors and {sfn_failures} failed Step Functions executions in the last {hours_back} hours."
        
        if error_count > 0:
            report['probable_cause'].append("Application errors detected in logs")
        if sfn_failures > 0:
            report['probable_cause'].append("Step Functions executions are failing")
        
        report['recommendations'].append(f"Review CloudWatch Logs for log group: {pipeline_info.get('log_group', 'N/A')}")
        report['recommendations'].append("Check Step Functions execution history for detailed failure reasons")
    else:
        report['summary'] = f"No errors found in the last {hours_back} hours."
        report['recommendations'].append("Pipeline appears healthy. Monitor for any new issues.")
    
    return report


def format_response(report: Dict[str, Any]) -> str:
    """Format analysis report according to agent guidelines."""
    lines = []
    
    # Summary
    lines.append("1) Summary")
    lines.append(f"- {report['summary']}")
    lines.append("")
    
    # Evidence
    lines.append("2) Evidence")
    if report.get('evidence'):
        for item in report['evidence']:
            if item['type'] == 'log_error':
                lines.append(f"- Log error at {item['timestamp']}: {item['message'][:200]}")
            elif item['type'] == 'step_function_failure':
                lines.append(f"- Step Function failure: {item['execution_arn']} (Status: {item['status']})")
    else:
        lines.append("- No evidence found in the specified time range.")
    
    # Probable cause
    lines.append("")
    lines.append("3) Probable cause")
    if report.get('probable_cause'):
        for cause in report['probable_cause']:
            lines.append(f"- {cause}")
    else:
        lines.append("- Insufficient evidence to determine cause.")
    
    # Recommendations
    lines.append("")
    lines.append("4) Recommended next steps")
    if report.get('recommendations'):
        for rec in report['recommendations']:
            lines.append(f"- {rec}")
    else:
        lines.append("- Gather more information: specify pipeline name, time range, and environment.")
    
    return "\n".join(lines)


def invoke_openai(prompt: str, context: str = "") -> Optional[str]:
    """Invoke OpenAI API if configured."""
    if not OPENAI_API_KEY:
        return None
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        system_prompt = """You are an AWS Operations Support Agent specialized in data platforms, SQL pipelines, and cloud workflows.

Your role is to help engineers understand operational state and troubleshoot issues.

Be concise, technical, and objective. Base conclusions only on provided evidence.
If information is missing, ask for minimum required detail (pipeline name, time range, environment).

Always structure your response as:
1) Summary - One or two sentences describing the current situation
2) Evidence - Bullet points with concrete signals (errors, timestamps, execution status)
3) Probable cause - Hypothesis based strictly on the evidence
4) Recommended next steps - Clear, actionable steps

Write in the same language as the user."""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if context:
            messages.append({"role": "user", "content": f"Context: {context}\n\nUser question: {prompt}"})
        else:
            messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error invoking OpenAI: {str(e)}", exc_info=True)
        return None


def invoke_bedrock(prompt: str) -> Optional[str]:
    """Invoke Bedrock model if configured."""
    if not BEDROCK_MODEL_ID:
        return None
    
    try:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body.get('content', [{}])[0].get('text', '')
    except Exception as e:
        logger.error(f"Error invoking Bedrock: {str(e)}", exc_info=True)
        return None


def validate_request_body(body: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate request body parameters."""
    # Validate hours_back if present
    if 'hours_back' in body:
        hours_back = body['hours_back']
        if not isinstance(hours_back, (int, float)) or hours_back < 1 or hours_back > 168:
            return False, "hours_back must be between 1 and 168 (7 days)"

    # Validate message length if present
    if 'message' in body:
        message = body['message']
        if not isinstance(message, str):
            return False, "message must be a string"
        if len(message) > 5000:
            return False, "message exceeds maximum length of 5000 characters"

    # Validate pipeline_name if present and not empty
    if 'pipeline_name' in body and body['pipeline_name']:
        pipeline_name = body['pipeline_name']
        if not isinstance(pipeline_name, str):
            return False, "pipeline_name must be a string"

        # Remove leading/trailing whitespace
        pipeline_name = pipeline_name.strip()

        # Skip validation if empty after stripping
        if not pipeline_name:
            body['pipeline_name'] = ''
            return True, None

        if len(pipeline_name) > 100:
            return False, "pipeline_name exceeds maximum length of 100 characters"

        # Validate - allow alphanumeric, hyphens, underscores, dots, slashes, and colons (common in AWS resource names)
        import re
        if not re.match(r'^[a-zA-Z0-9_\-./:]+$', pipeline_name):
            # Find invalid characters for better error message
            invalid_chars = [c for c in pipeline_name if not re.match(r'[a-zA-Z0-9_\-./:]', c)]
            invalid_str = ', '.join(set(invalid_chars)) if invalid_chars else 'unknown'
            return False, f"pipeline_name contains invalid characters: '{invalid_str}'. Only alphanumeric, hyphens (-), underscores (_), dots (.), slashes (/), and colons (:) are allowed. Received: '{pipeline_name}'"

        # Update the cleaned name back to body
        body['pipeline_name'] = pipeline_name

    return True, None


def sanitize_pipeline_name(name: str) -> Optional[str]:
    """Sanitize and validate extracted pipeline name."""
    if not name:
        return None

    # Remove leading/trailing whitespace
    name = name.strip()

    # Check length
    if len(name) > 100:
        logger.warning(f"Pipeline name too long: {len(name)} chars")
        return None

    # Validate characters - allow alphanumeric, hyphens, underscores, dots, slashes, colons
    import re
    if not re.match(r'^[a-zA-Z0-9_\-./:]+$', name):
        logger.warning(f"Invalid characters in extracted pipeline name: {name}")
        return None

    return name


def get_security_headers() -> Dict[str, str]:
    """Get security headers for responses."""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Cache-Control': 'no-store, no-cache, must-revalidate, private'
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler."""
    # Log request info
    logger.info(f"Received request: {event.get('requestContext', {}).get('http', {}).get('method', 'UNKNOWN')}")

    # Handle OPTIONS preflight request
    # Check multiple possible event formats for HTTP method
    http_method = None
    if 'requestContext' in event:
        if 'http' in event['requestContext']:
            http_method = event['requestContext']['http'].get('method')
        elif 'httpMethod' in event['requestContext']:
            http_method = event['requestContext']['httpMethod']

    if http_method == 'OPTIONS' or event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key',
                'Access-Control-Max-Age': '300'
            },
            'body': ''
        }
    
    try:
        # Parse request - handle empty body for OPTIONS
        body_str = event.get('body') or '{}'
        if isinstance(body_str, str):
            try:
                body = json.loads(body_str)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in request body: {str(e)}")
                return {
                    'statusCode': 400,
                    'headers': get_security_headers(),
                    'body': json.dumps({
                        'error': 'Invalid JSON format in request body'
                    })
                }
        else:
            body = body_str if isinstance(body_str, dict) else {}

        # Validate request body
        is_valid, error_message = validate_request_body(body)
        if not is_valid:
            logger.warning(f"Invalid request: {error_message}")
            return {
                'statusCode': 400,
                'headers': get_security_headers(),
                'body': json.dumps({
                    'error': error_message
                })
            }

        message = body.get('message', '')
        conversation_id = body.get('conversation_id', str(uuid.uuid4()))
        pipeline_name = body.get('pipeline_name', '')
        hours_back = int(body.get('hours_back', 24))
        
        # Extract pipeline name from message if not provided
        if not pipeline_name and message:
            logger.info(f"Attempting to extract pipeline name from message: {message}")
            message_lower = message.lower()
            # Try different patterns
            import re

            extracted_name = None

            # Pattern 1: "analyze pipeline <name>" or "check pipeline <name>" - capture everything after "pipeline"
            match = re.search(r'(?:analyze|check|show|get|find|what|how).*?pipeline\s+([^\s]+(?:\s+[^\s]+)*)', message_lower)
            if match:
                extracted_name = match.group(1).strip()
            else:
                # Pattern 2: "pipeline <name>" - capture everything after "pipeline"
                match = re.search(r'pipeline\s+([^\s]+(?:\s+[^\s]+)*)', message_lower)
                if match:
                    extracted_name = match.group(1).strip()
                else:
                    # Pattern 3: "logs for <name>" or "errors in <name>"
                    match = re.search(r'(?:logs|errors|status).*?(?:for|in|of)\s+([^\s]+(?:\s+[^\s]+)*)', message_lower)
                    if match:
                        extracted_name = match.group(1).strip()
                    else:
                        # Pattern 4: Just look for any word that might be a pipeline name after common verbs
                        match = re.search(r'(?:analyze|check|show|get|find|what|how|explain)\s+([a-zA-Z0-9_\-./:]+)', message_lower)
                        if match:
                            extracted_name = match.group(1).strip()

            # Clean and sanitize extracted name
            if extracted_name:
                # Remove trailing punctuation
                extracted_name = extracted_name.strip('.,!?;:')
                # Take only the first word if multiple words (or allow hyphenated names)
                words = extracted_name.split()
                if len(words) > 1:
                    # If it's a hyphenated name, keep it together
                    if '-' in extracted_name:
                        extracted_name = extracted_name.split()[0]
                    else:
                        extracted_name = words[0]
                
                pipeline_name = sanitize_pipeline_name(extracted_name)
                if pipeline_name:
                    logger.info(f"Extracted pipeline name: {pipeline_name}")
                else:
                    logger.warning(f"Failed to sanitize extracted pipeline name: {extracted_name}")
            else:
                logger.warning(f"Could not extract pipeline name from message: {message}")
        
        response_text = ""
        
        # If pipeline name is provided, analyze it
        if pipeline_name:
            report = analyze_pipeline(pipeline_name, hours_back)
            response_text = format_response(report)
            
            # Enhance with AI if available (OpenAI first, then Bedrock)
            if OPENAI_API_KEY:
                enhanced = invoke_openai(
                    prompt=message if message else f"Analyze this pipeline report: {response_text}",
                    context=response_text
                )
                if enhanced:
                    response_text = enhanced
            elif BEDROCK_MODEL_ID:
                enhanced = invoke_bedrock(f"Enhance this technical analysis: {response_text}")
                if enhanced:
                    response_text = enhanced
        else:
            # If no pipeline specified, try to answer with AI if available
            if OPENAI_API_KEY and message:
                ai_response = invoke_openai(
                    prompt=message,
                    context="You are an AWS Operations Agent. Help the user analyze pipelines, check logs, and troubleshoot issues."
                )
                if ai_response:
                    response_text = ai_response
                else:
                    response_text = "Please provide a pipeline name to analyze. Usage: {\"message\": \"analyze pipeline <name>\", \"pipeline_name\": \"<name>\"}"
            else:
                response_text = "Please provide a pipeline name to analyze. Usage: {\"message\": \"analyze pipeline <name>\", \"pipeline_name\": \"<name>\"}"
        
        # Save conversation
        save_conversation(conversation_id, message, response_text)

        # Log successful response
        logger.info(f"Successfully processed request for conversation_id: {conversation_id}")

        # Return response
        return {
            'statusCode': 200,
            'headers': get_security_headers(),
            'body': json.dumps({
                'conversation_id': conversation_id,
                'response': response_text,
                'pipeline_name': pipeline_name
            })
        }

    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': get_security_headers(),
            'body': json.dumps({
                'error': 'Internal server error. Please try again later.'
            })
        }
