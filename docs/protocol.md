# Protocolo JSON-RPC Simplificado

## Visão geral

Este documento descreve o protocolo de comunicação simplificado entre o aplicativo Flutter e o serviço Python.
O protocolo utiliza stdin/stdout para transmissão de mensagens, permitindo execução de tarefas longas
sem bloquear a interface do usuário.

## Formato da mensagem

### Características gerais

- **Uma mensagem JSON por linha**: Cada mensagem é um objeto JSON seguido de caractere de nova linha `\n`.
- **requestId único por solicitação**: Cada mensagem de requisição deve ter um `id` único para correlacionar respostas.
- **Versão do protocolo**: Todas as mensagens devem incluir o campo `jsonrpc` indicando a versão do protocolo.
- **Respostas padronizadas**: As respostas seguem um formato consistente com `result` ou `error`.
- **Eventos assíncronos de progresso**: Suporte a eventos de progresso durante operações longas.
- **Identificação de jobs**: Cada trabalho/tradução tem um identificador único.
- **Cancelamento de operações**: Suporte para cancelamento de operações em andamento.
- **Tratamento de timeout**: Mecanismo para detectar e lidar com timeouts.
- **Tratamento de falhas do processo**: Tratamento adequado quando o processo Python falha ou termina.
- **Reinicialização controlada**: Quando aplicável, reinicialização controlada do serviço.
- **Logs exclusivamente em stderr**: Todos os logs e mensagens de diagnóstico devem ir para stderr.
- **Nenhum log ou texto de diagnóstico em stdout**: O stdout deve conter apenas mensagens JSON-RPC puras.

## Esquema da mensagem

```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "nome-do-método",
  "params": {
    // parâmetros da requisição
  }
}
```

Ou para respostas:

```json
// Sucesso
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "result": {
    "type": "tipo-da-resposta",
    "dados": "dados-da-resposta"
  }
}

// Erro
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "error": {
    "code": -32602,
    "message": "Descrição do erro"
  }
}
```

## Tipos de mensagens

### 1. Mensagens de requisição (do Flutter para o Python)

#### `ping`
- Descrição: Verifica se o serviço está rodando.
- Parâmetros: Nenhum
- Resposta esperada:
  ```json
  {
    "jsonrpc": "2.0",
    "id": "pong-id",
    "result": {
      "type": "pong",
      "service": "python-pdf-service",
      "version": "1.0.0"
    }
  }
  ```

#### `extract`
- Descrição: Extrai texto e estrutura de um PDF.
- Parâmetros:
  - `file_path` (string): Caminho para o arquivo PDF
- Resposta esperada:
  ```json
  {
    "jsonrpc": "2.0",
    "id": "extract-id",
    "result": {
      "type": "extraction_result",
      "data": { ... estrutura do PDF ... }
    }
  }
  ```

#### `ocr`
- Descrição: Realiza OCR em uma página do PDF.
- Parâmetros:
  - `file_path` (string): Caminho para o arquivo PDF
  - `page_number` (number, opcional): Número da página (0 para todas)
  - `language` (string, opcional): Código de idioma (padrão: "por+eng")
- Resposta esperada:
  ```json
  {
    "jsonrpc": "2.0",
    "id": "ocr-id",
    "result": {
      "type": "ocr_result",
      "data": { ... resultados do OCR ... }
    }
  }
  ```

#### `classify`
- Descrição: Classifica a estrutura do documento.
- Parâmetros:
  - `file_path` (string): Caminho para o arquivo PDF
- Resposta esperada:
  ```json
  {
    "jsonrpc": "2.0",
    "id": "classify-id",
    "result": {
      "type": "classification_result",
      "data": { ... classificação do documento ... }
    }
  }
  ```

#### `translate`
- Descrição: Solicita tradução de um documento.
- Parâmetros:
  - `job_id` (string): Identificador único do job
  - `file_path` (string): Caminho para o arquivo PDF
  - `target_language` (string): Idioma alvo
  - `source_language` (string): Idioma de origem
  - `model_name` (string): Nome do modelo de IA
  - `fidelity_visual` (boolean, opcional): Preservação de layout (padrão: true)
- Resposta esperada (inicial):
  ```json
  {
    "jsonrpc": "2.0",
    "id": "translate-id",
    "result": {
      "type": "translation_status",
      "job_id": "job-123",
      "status": "initiated",
      "progress": 0.0
    }
  }
  ```
- Eventos de progresso subsequentes são enviados como mensagens separadas via stdout.

#### `status`
- Descrição: Retorna status de um job.
- Parâmetros:
  - `job_id` (string): Identificador do job
- Resposta esperada:
  ```json
  {
    "jsonrpc": "2.0",
    "id": "status-id",
    "result": {
      "type": "job_status",
      "job_id": "job-123",
      "status": "in_progress",
      "progress": 45.5
    }
  }
  ```

#### `cancel`
- Descrição: Cancela um job em andamento.
- Parâmetros:
  - `job_id` (string): Identificador do job a ser cancelado
- Resposta esperada:
  ```json
  {
    "jsonrpc": "2.0",
    "id": "cancel-id",
    "result": {
      "type": "cancel_ack",
      "job_id": "job-123"
    }
  }
  ```

#### `shutdown`
- Descrição: Solicita desligamento controlado do serviço Python.
- Parâmetros: Nenhum
- Resposta esperada:
  ```json
  {
    "jsonrpc": "2.0",
    "id": "shutdown-id",
    "result": {
      "type": "shutdown_ack"
    }
  }
  ```

### 2. Mensagens de notificação (do Python para o Flutter, sem requestId)

#### Progresso de tradução
- Enviado durante operações longas para atualizar a interface.
- Parâmetros:
  - `job_id` (string): Identificador do job
  - `progress` (number): Progresso de 0.0 a 1.0
  - `status` (string): Status atual (e.g., "in_progress", "paused", "completed", "failed")
  - `message` (string, opcional): Mensagem descritiva
- Formato:
  ```json
  {
    "jsonrpc": "2.0",
    "method": "progress",
    "params": {
      "job_id": "job-123",
      "progress": 0.75,
      "status": "in_progress",
      "message": "Traduzindo página 5 de 10"
    }
  }
  ```

#### Eventos de erro
- Enviado quando ocorre um erro durante o processamento.
- Parâmetros:
  - `job_id` (string): Identificador do job (se aplicável)
  - `error_code` (string): Código do erro
  - `error_message` (string): Descrição do erro
- Formato:
  ```json
  {
    "jsonrpc": "2.0",
    "method": "error",
    "params": {
      "job_id": "job-123",
      "error_code": "extraction_error",
      "error_message": "Erro ao extrair PDF: arquivo corrompido"
    }
  }
  ```

## Protocol specifications

### requestId

- Cada mensagem de requisição deve ter um `id` único.
- O `id` pode ser um string ou número.
- A mesma `id` deve ser usada na resposta correspondente para correlacionar requisição e resposta.
- IDs recomendados: UUIDs ou números inteiros sequenciais.

### Versão do protocolo

- O campo `jsonrpc` deve sempre ser definido como `"2.0"`.
- Isso permite evolução futura do protocolo mantendo compatibilidade backwards.

### Respostas padronizadas

- **Sucesso**: Mensagem com campo `result` contém os dados da resposta.
- **Erro**: Mensagem com campo `error` contém:
  - `code`: Código numérico do erro (convenção: -32700 = parse error, -32602 = inválidos params, -32603 = erro interno)
  - `message`: Descrição legível do erro
  - `data` (opcional): Dados adicionais sobre o erro

### Eventos assíncronos de progresso

- Operações longas (tradução, extração de PDF grande) podem enviar eventos de progresso.
- Estes são enviados como mensagens JSON normais em stdout, sem `id` (ou com `id` null).
- A frequência de eventos de progresso deve ser razoável (ex: a cada 5-10% de progresso ou a cada 5 segundos).

### Identificação de jobs

- Cada trabalho de tradução deve ter um `job_id` único.
- O `job_id` é passado em quase todas as mensagens relacionadas a um trabalho específico.
- O mesmo `job_id` deve ser usado em todas as mensagens relacionadas a um mesmo trabalho.
- Jobs permitem:
  - Monitoramento de progresso
  - Cancelamento
  - Retomada após interrupção

### Cancelamento de operações

- O método `cancel` pode ser usado para solicitar cancelamento de um job em andamento.
- O serviço deve responder com `cancel_ack` confirmando o cancelamento.
- O cancelamento deve ser tratado de forma oportuna, não bloqueando o loop principal.

### Timeout

- O Flutter deve definir timeouts para leitura de mensagens do Python.
- Se nenhuma mensagem for recebida dentro do timeout especificado, o Flutter deve:
  - Considerar o job como falhado
  - Tentar reinicializar o processo Python se necessário
  - Mostrar mensagem de erro ao usuário

### Tratamento de falhas do processo

- Se o processo Python terminar inesperadamente:
  - O Flutter deve detectar o fechamento de stdin/stdout
  - Mostrar mensagem de erro ao usuário
  - Opcional: tentar reinicializar o serviço Python
- Mensagens recebidas após o término do processo devem ser ignoradas.

### Logs

- **Somente stderr**: Todas as mensagens de log, debug e diagnóstico do serviço Python devem ser enviadas para stderr.
- **stdout limpo**: O stdout do serviço Python deve conter apenas mensagens JSON-RPC no formato especificado.
- O Flutter deve redirecionar stderr do processo Python para seus próprios logs ou descartear, dependendo das configurações.

## Exemplo de fluxo completo

### 1. Inicialização

```bash
# Serviço Python inicia e envia:
{"jsonrpc":"2.0","result":{"type":"ready","service":"python-pdf-service","version":"1.0.0"},"id":null}

# Flutter recebe "ready" e considera o serviço disponível
```

### 2. Extrair PDF

```bash
# Flutter envia:
{"jsonrpc":"2.0","id":"extract-1","method":"extract","params":{"file_path":"/caminho/para/documento.pdf"}}

# Python responde:
{"jsonrpc":"2.0","id":"extract-1","result":{"type":"extraction_result","data":{...}}}

# Flutter recebe resposta e processa os dados
```

### 3. Traduzir documento (com progresso)

```bash
# Flutter envia:
{"jsonrpc":"2.0","id":"translate-1","method":"translate","params":{"job_id":"job-abc","file_path":"/caminho/para/documento.pdf","target_language":"en","source_language":"pt","model_name":"openai:gpt-4o-mini"}}

# Python responde (inicial):
{"jsonrpc":"2.0","id":"translate-1","result":{"type":"translation_status","job_id":"job-abc","status":"initiated","progress":0.0}}

# Python envia eventos de progresso (periodicamente):
{"jsonrpc":"2.0","method":"progress","params":{"job_id":"job-abc","progress":0.3,"status":"in_progress","message":"Traduzindo página 3 de 10"}}

# Python envia evento de conclusão (opcional como método ou resposta):
{"jsonrpc":"2.0","id":"translate-1","result":{"type":"translation_status","job_id":"job-abc","status":"completed","progress":1.0}}

# Ou evento de erro:
{"jsonrpc":"2.0","method":"error","params":{"job_id":"job-abc","error_code":"translation_error","error_message":"Timeout do modelo de IA"}}
```

### 4. Cancelar tradução

```bash
# Flutter envia:
{"jsonrpc":"2.0","id":"cancel-1","method":"cancel","params":{"job_id":"job-abc"}}

# Python responde:
{"jsonrpc":"2.0","id":"cancel-1","result":{"type":"cancel_ack","job_id":"job-abc"}}
```

### 5. Desligamento

```bash
# Flutter envia:
{"jsonrpc":"2.0","id":"shutdown-1","method":"shutdown","params":{}}

# Python responde:
{"jsonrpc":"2.0","id":"shutdown-1","result":{"type":"shutdown_ack"}}

# Python encerra o processo
```

## Implementação Flutter

O cliente Flutter deve:

1. Iniciar o processo Python como subprocesso com stdin/stdout conectados
2. Ler mensagens JSON de uma linha por vez de stdout
3. Enviar mensagens JSON codificadas em utf-8 para stdin, terminando com newline
4. Tratar o `id` para correlacionar requisições e respostas
5. Tratar mensagens de `method` (notificações) separadamente de mensagens com `result`
6. Manter stderr separado e não misturar com stdout
7. Implementar timeouts para leitura de mensagens
8. Implementar lógica de reconexão/reinicialização quando o processo termina

## Implementação Python

O serviço Python deve:

1. Ler linhas de stdin até EOF
2. Parsear cada linha como JSON no formato especificado
3. Executar o handler correspondente ao `method` ou tipo da mensagem
4. Enviar resposta em stdout no formato JSON + newline
5. Enviar notificações (progresso, erros) usando o formato de mensagem sem `id` ou com `method`
6. Escrever todos os logs em stderr, nunca em stdout
7. Tratar timeouts e falhas de forma graciosa
8. Gerenciar jobs e seus IDs de forma consistente

## Segurança

- Validar todos os parâmetros recebidos antes do processamento
- Não executar código arbitrário baseado em entrada do usuário
- Sanitizar caminhos de arquivo para evitar ataques de path traversal
- Validar tipos de dados esperados antes do processamento
- Limitar tamanho de mensagens para evitar ataques de memória
