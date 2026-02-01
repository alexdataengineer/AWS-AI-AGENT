#!/bin/bash

# Script interativo para configurar AWS CLI

echo "🔧 Configuração do AWS CLI"
echo "==========================\n"

echo "Para obter as credenciais:"
echo "1. Acesse: https://console.aws.amazon.com/iam/home#/security_credentials"
echo "2. Vá em 'Access keys' → 'Create access key'"
echo "3. Copie o Access Key ID e Secret Access Key\n"

read -p "Pressione Enter quando tiver as credenciais prontas..."

echo "\n📝 Configure as credenciais:\n"

# Executa aws configure
aws configure

echo "\n✅ Configuração concluída!"
echo "\n🔍 Testando conexão...\n"

# Testa a conexão
IDENTITY=$(aws sts get-caller-identity 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ Conexão estabelecida com sucesso!\n"
    echo "$IDENTITY" | python3 -m json.tool
    
    ACCOUNT_ID=$(echo "$IDENTITY" | grep -o '"Account": "[^"]*"' | cut -d'"' -f4)
    echo "\n✅ Connected to AWS Account: $ACCOUNT_ID"
else
    echo "❌ Erro na conexão:"
    echo "$IDENTITY"
    echo "\nVerifique se as credenciais estão corretas."
fi
