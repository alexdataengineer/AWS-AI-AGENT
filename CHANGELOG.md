# Changelog

## Security Improvements

### ✅ Implemented

1. **Input Validation**
   - Added `validate_request()` function to Lambda handler
   - Validates `pipeline_name` or `message` presence
   - Validates `hours_back` range (1-168 hours)
   - Returns 400 error for invalid requests

2. **Configurable Log Filter Pattern**
   - Changed from hardcoded filter pattern to configurable
   - Filter pattern can be set per pipeline in DynamoDB catalog
   - Falls back to default pattern if not specified
   - Field: `log_filter_pattern` in pipelines catalog

3. **CORS Configuration Warning**
   - Updated `terraform.tfvars.example` with explicit warning
   - Added recommendation to restrict origins in production

4. **Security Documentation**
   - Created comprehensive `SECURITY.md` guide
   - Documents current security posture
   - Provides implementation examples for:
     - API Key authentication
     - IAM authorization
     - AWS WAF rate limiting
     - Secrets Manager integration
   - Includes security checklist for production deployment

5. **Backend Configuration**
   - Created `backend.tf.example` for Terraform remote state
   - Includes instructions for S3 bucket and DynamoDB table setup

6. **API Key Example**
   - Created `infra/modules/api_http/api_key.tf.example`
   - Shows how to add API key authentication

### ⚠️ Recommendations (Not Yet Implemented)

1. **API Authentication** - HIGH PRIORITY
   - Current: API is public and unauthenticated
   - Recommendation: Add API Keys, IAM, or Cognito authentication
   - See `SECURITY.md` for implementation examples

2. **CORS Restriction** - MEDIUM PRIORITY
   - Current: `allowed_origins = ["*"]`
   - Recommendation: Restrict to specific domains in production

3. **Credential Rotation** - MEDIUM PRIORITY
   - Current: Credentials in `.env` file
   - Recommendation: Rotate regularly, use AWS SSO or Secrets Manager

## Code Quality Improvements

### ✅ Fixed

1. **Deprecated datetime.utcnow()**
   - Changed to `datetime.now(timezone.utc)` throughout handler.py
   - More explicit and timezone-aware

2. **Removed Unused Dependencies**
   - Removed `pandas` from `requirements.txt` (not used)

3. **Type Hints**
   - Added `Tuple` import for validation function return type

## Documentation Updates

1. **README.md**
   - Translated to English
   - Removed hardcoded credentials
   - Added links to all documentation
   - Added security section

2. **ARCHITECTURE.md**
   - Added security considerations section
   - Links to SECURITY.md

3. **DEPLOYMENT.md**
   - Added security note at the beginning
   - Links to SECURITY.md

4. **New Files**
   - `SECURITY.md` - Comprehensive security guide
   - `backend.tf.example` - Terraform backend configuration template
   - `api_key.tf.example` - API key authentication example
   - `CHANGELOG.md` - This file

## Pipeline Catalog Schema Update

The pipelines catalog now supports an optional `log_filter_pattern` field:

```python
{
    'pipeline_name': 'my-pipeline',
    'log_group': '/aws/lambda/my-function',
    'state_machine_arn': 'arn:aws:states:...',
    'log_filter_pattern': 'ERROR Exception "error" "failed"',  # Optional
    'region': 'us-east-1',
    'owner': 'team-name',
    'runbook': 'https://...'
}
```

If `log_filter_pattern` is not provided, defaults to: `'ERROR Exception "error" "failed" "failure"'`

## Next Steps

Before production deployment:

1. [ ] Implement API authentication (see `SECURITY.md`)
2. [ ] Restrict CORS origins in `terraform.tfvars`
3. [ ] Rotate AWS credentials
4. [ ] Review and test input validation
5. [ ] Set up Terraform backend (see `backend.tf.example`)
6. [ ] Configure CloudWatch Alarms
7. [ ] Review IAM policies for least privilege
