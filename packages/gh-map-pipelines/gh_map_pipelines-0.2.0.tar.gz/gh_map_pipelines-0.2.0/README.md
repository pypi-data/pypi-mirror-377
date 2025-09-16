# gh_map_pipelines v2 - Improved Version

## 📋 Principais Melhorias

### 1. **Gravação Incremental**
- Dados são salvos em lotes (batch) durante o processamento
- Não há perda de dados em caso de interrupção
- Arquivos Parquet são atualizados incrementalmente
- Batch size configurável (padrão: 10 itens)

### 2. **Tratamento Inteligente de Rate Limit**
- Detecta erro 429 automaticamente
- Aguarda tempo configurável (padrão: 60 segundos)
- Registra ocorrências em tabela `rate_limit_log`
- Verifica histórico antes de fazer novas requisições
- Retry automático com backoff

### 3. **Sistema de Retomada (Resume)**
- Rastreia progresso em tabelas de controle
- Permite retomar de onde parou com `--resume`
- Não reprocessa workflows já analisados
- Mantém contador de tentativas para cada item

### 4. **Novos Comandos CLI**

## 🚀 Uso

### Instalação
```bash
# Se estiver usando poetry
poetry install

# Ou instale diretamente
pip install -e .
```

### Comandos Disponíveis

#### 1. Processamento Completo
```bash
# Processar organização do zero
gh_map process --org <nome-da-org>

# Com configurações customizadas
gh_map process --org <nome-da-org> --batch-size 20 --wait 120
```

#### 2. Retomar Processamento
```bash
# Retomar de onde parou (após interrupção ou rate limit)
gh_map process --org <nome-da-org> --mode resume

# Ou use o atalho
gh_map resume --org <nome-da-org>
```

#### 3. Processar Apenas Uses (após coletar repos e workflows)
```bash
# Útil quando repos e workflows já foram coletados
gh_map process --org <nome-da-org> --mode uses-only
```

#### 4. Verificar Status
```bash
# Ver estatísticas do processamento
gh_map status --org <nome-da-org>

# Ou através do modo
gh_map process --org <nome-da-org> --mode status
```

#### 5. Reset de Status (mantém dados)
```bash
# Reseta status de processamento mas mantém dados coletados
gh_map reset --org <nome-da-org> --confirm
```

#### 6. Limpar Dados
```bash
# Limpar todos os dados
gh_map clean --org <nome-da-org> --confirm

# Limpar mas manter repositórios
gh_map clean --org <nome-da-org> --confirm --keep-repos
```

#### 7. Exportar Dados
```bash
# Exportar para JSON
gh_map export --org <nome-da-org> --format json --output data.json

# Exportar para CSV (gera 3 arquivos)
gh_map export --org <nome-da-org> --format csv --output export
```

## 📊 Estrutura de Dados

### Tabelas SQLite

#### 1. `repositorios`
- Informações dos repositórios da organização

#### 2. `workflow_runs`
- Workflows do GitHub Actions de cada repositório

#### 3. `uses_workflows`
- Actions utilizadas em cada workflow

#### 4. `workflow_status` (Nova)
- Controle de processamento de cada workflow
- Status: `completed`, `error`, `rate_limited`, `not_found`, `yaml_error`, `skipped`
- Contador de tentativas

#### 5. `processing_status` (Nova)
- Estado geral do processamento
- Checkpoints para retomada

#### 6. `rate_limit_log` (Nova)
- Histórico de rate limits encontrados
- Usado para evitar requisições durante período de espera

### Arquivos Parquet
- `repos.parquet` - Repositórios
- `workflow_runs.parquet` - Workflows
- `uses_workflows.parquet` - Uses encontrados

## 🔄 Fluxo de Processamento

1. **Coleta de Repositórios**
   - Lista páginas da API incrementalmente
   - Salva em lotes no banco e parquet
   - Checkpoint a cada página processada

2. **Coleta de Workflows**
   - Processa repositório por repositório
   - Pula repositórios já processados
   - Salva incrementalmente

3. **Extração de Uses**
   - Baixa YAMLs dos workflows
   - Extrai actions recursivamente
   - Marca status de cada workflow
   - Retry automático em caso de falha

## 🛡️ Resiliência

### Cenários Tratados:
- **Rate Limit (429)**: Aguarda e tenta novamente
- **Timeout**: Retry automático
- **Erro 404**: Marca como `not_found` e continua
- **YAML inválido**: Marca como `yaml_error` e continua
- **Interrupção**: Use `--resume` para continuar

### Limites de Retry:
- Máximo de 3 tentativas por workflow
- Workflows com muitos erros são pulados
- Rate limit reseta contador após sucesso

## 📈 Monitoramento

### Status Report mostra:
- Total de repositórios coletados
- Total de workflows encontrados
- Total de uses extraídos
- Workflows processados com sucesso
- Workflows com erro
- Workflows aguardando retry (rate limited)

## 💡 Dicas de Uso

1. **Para grandes organizações**: Use batch size maior (ex: `--batch-size 50`)

2. **Se encontrar muitos rate limits**: Aumente tempo de espera (ex: `--wait 300`)

3. **Para debug**: Acompanhe os logs coloridos no console

4. **Consulta durante processamento**: Os dados são salvos incrementalmente, permitindo consultas SQL/Parquet mesmo durante a coleta

5. **Processamento em etapas**:
   ```bash
   # Primeiro, colete apenas repositórios
   gh_map process --org myorg
   # (interrompa com Ctrl+C após coletar repos)
   
   # Depois, continue com workflows e uses
   gh_map resume --org myorg
   ```

## 🔍 Consultas SQL Úteis

```sql
-- Workflows pendentes de processamento
SELECT COUNT(*) FROM workflow_runs wr
LEFT JOIN workflow_status ws ON wr.node_id = ws.node_id
WHERE ws.status IS NULL OR ws.status != 'completed';

-- Top 10 actions mais usadas
SELECT use, COUNT(*) as count 
FROM uses_workflows 
GROUP BY use 
ORDER BY count DESC 
LIMIT 10;

-- Repositórios com mais workflows
SELECT r.name, COUNT(w.id) as workflow_count
FROM repositorios r
JOIN workflow_runs w ON r.id = w.id_repo
GROUP BY r.name
ORDER BY workflow_count DESC;
```

## 🐛 Troubleshooting

### Problema: Rate limit constante
**Solução**: Aumente o tempo de espera ou execute em horários com menos tráfego

### Problema: Memória insuficiente para grandes orgs
**Solução**: Reduza o batch size para processar menos itens por vez

### Problema: Processo travado
**Solução**: Use `Ctrl+C` para interromper e depois `gh_map resume` para continuar

## 📝 Notas de Implementação

### Diferenças da v1:
1. Não carrega tudo em memória antes de salvar
2. Salva incrementalmente em lotes configuráveis
3. Rate limit com retry inteligente e backoff
4. Sistema de checkpoint para retomada
5. Múltiplos modos de operação
6. Comandos auxiliares (status, reset, clean, export)
7. Melhor tratamento de erros e edge cases
