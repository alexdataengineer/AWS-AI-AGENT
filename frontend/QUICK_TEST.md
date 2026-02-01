# Quick Test Prompts

## ✅ Prompts que Funcionam Agora

### 1. Análise de Pipeline
```
analyze pipeline test-pipeline
```

```
check pipeline my-pipeline
```

```
show pipeline status for data-pipeline
```

### 2. Verificar Logs
```
check logs for test-pipeline
```

```
what errors in my-pipeline
```

```
show errors for data-pipeline
```

### 3. Com Tempo Específico
```
analyze pipeline test-pipeline last 48 hours
```

```
check logs for my-pipeline in the last 12 hours
```

## 🎯 Como Testar

1. **Abra o chatbot** (http://localhost:8001)

2. **Digite um dos prompts acima**, por exemplo:
   ```
   analyze pipeline test-pipeline
   ```

3. **Ou configure o pipeline nas settings** (⚙️):
   - Pipeline Name: `test-pipeline`
   - Hours Back: `24`
   - Depois use: `check logs` ou `analyze pipeline`

## 📝 Exemplos de Respostas Esperadas

### Se o pipeline não existe no catálogo:
```
1) Summary
- No errors found in the last 24 hours.

2) Evidence
- No evidence found in the specified time range.

3) Probable cause
- Insufficient evidence to determine cause.

4) Recommended next steps
- Pipeline appears healthy. Monitor for any new issues.
```

### Se o pipeline existe e tem erros:
```
1) Summary
- Found 5 log errors and 2 failed Step Functions executions in the last 24 hours.

2) Evidence
- Log error at 2026-01-31T23:00:00: ERROR: Connection timeout
- Step Function failure: arn:aws:states:... (Status: FAILED)

3) Probable cause
- Application errors detected in logs
- Step Functions executions are failing

4) Recommended next steps
- Review CloudWatch Logs for log group: /aws/lambda/my-function
- Check Step Functions execution history for detailed failure reasons
```

## 🔧 Registrar Pipeline para Teste Real

```python
import boto3

ddb = boto3.resource('dynamodb')
table = ddb.Table('ops-agent-pipelines-catalog-prod')

table.put_item(
    Item={
        'pipeline_name': 'test-pipeline',
        'log_group': '/aws/lambda/your-function-name',
        'state_machine_arn': 'arn:aws:states:us-east-1:336751562831:stateMachine:YourStateMachine',
        'region': 'us-east-1',
        'owner': 'test-user',
        'log_filter_pattern': 'ERROR Exception "error" "failed"'
    }
)
```
