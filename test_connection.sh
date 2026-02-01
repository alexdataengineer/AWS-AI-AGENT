#!/bin/bash

# Script para testar a conexão com AWS CLI

echo "🔌 Testando conexão com AWS CLI...\n"

# Verifica se AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não está instalado!"
    echo "Instale com: brew install awscli"
    exit 1
fi

echo "✅ AWS CLI instalado: $(aws --version)\n"

# Testa a conexão
echo "📋 Obtendo informações da conta...\n"
IDENTITY=$(aws sts get-caller-identity 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ Conexão estabelecida com sucesso!\n"
    echo "$IDENTITY" | python3 -m json.tool
    
    # Extrai Account ID
    ACCOUNT_ID=$(echo "$IDENTITY" | grep -o '"Account": "[^"]*"' | cut -d'"' -f4)
    
    echo "\n🔍 Verificando Account ID..."
    if [ "$ACCOUNT_ID" == "336751562831" ]; then
        echo "✅ Account ID confere: $ACCOUNT_ID"
    else
        echo "⚠️  Account ID diferente do esperado. Esperado: 336751562831, Obtido: $ACCOUNT_ID"
    fi
    
    echo "\n🔍 Testando acesso a serviços...\n"
    
    # Testa S3
    echo "📦 Testando S3..."
    if aws s3 ls &> /dev/null; then
        BUCKET_COUNT=$(aws s3 ls 2>/dev/null | wc -l | tr -d ' ')
        echo "   ✅ S3: Acesso permitido ($BUCKET_COUNT buckets)"
    else
        echo "   ⚠️  S3: Sem permissão ou sem buckets"
    fi
    
    # Testa EC2
    echo "🖥️  Testando EC2..."
    if aws ec2 describe-regions &> /dev/null; then
        echo "   ✅ EC2: Acesso permitido"
    else
        echo "   ⚠️  EC2: Sem permissão"
    fi
    
else
    echo "❌ Erro ao conectar na AWS!"
    echo "\nPossíveis causas:"
    echo "   - Credenciais não configuradas (execute: aws configure)"
    echo "   - Credenciais inválidas ou expiradas"
    echo "   - Região incorreta"
    echo "\nDetalhes do erro:"
    echo "$IDENTITY"
    exit 1
fi

echo "\n✅ Teste concluído!"
