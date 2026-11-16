# Arquitetura — PDF Translate Wizard

## Visão geral

O aplicativo segue **Clean Architecture** com separação entre processos do Electron e camadas de domínio, aplicação e infraestrutura.

## Processos do Electron

### Main Process (`src/main/`)

Responsável por:
- Inicialização do Electron e gerenciamento da janela principal
- Comunicação entre Main e Renderer via IPC
- Gerenciamento de arquivos e pastas
- Persistência local (SQLite via `better-sqlite3`)
- Gerenciamento do serviço Python (child_process)
- Credenciais via `electron safeStorage`
- Agendamento e controle de tarefas de tradução
- Notificações de progresso

### Preload (`src/preload/`)

Bridge segura que expõe apenas APIs autorizadas ao Renderer via `contextBridge`. Configurado com:
- `contextIsolation: true`
- `nodeIntegration: false`

### Renderer Process (`src/renderer/`)

Interface construída com React, Vite, Tailwind CSS e shadcn/ui. Gerenciamento de estado com Zustand.

## Módulos de negócio

### PDF Processing Engine (`src/modules/pdf/`)

Extração de texto com coordenadas, identificação de blocos, ordem de leitura, fontes, tamanhos, tabelas, cabeçalhos, rodapés e OCR condicional.

### AI Provider Engine (`src/modules/ai/`)

Interface comum (`AIProvider`) implementada por adapters específicos:
- OpenAI, Anthropic, Gemini, Azure OpenAI, Mistral, DeepSeek, xAI Grok, OpenRouter
- Ollama (modelos locais)
- LM Studio (via API compatível OpenAI)

Credenciais armazenadas em `safeStorage`, nunca em texto puro.

### Translation Engine (`src/modules/translation/`)

Segmentação inteligente, preservação de contexto, glossários, preservação de expressões técnicas, controle de concorrência, retry, timeout e validação de respostas.

### Document Reconstruction Engine (`src/modules/reconstruction/`)

Três estratégias de reconstrução (A: substituição no original, B: reconstrução de blocos, C: reconstrução de página), ajuste tipográfico, gerenciamento de fontes, expansão de páginas e exportação.

### Persistence (`src/modules/persistence/`)

SQLite com tabelas para provedores, modelos, jobs de tradução, páginas, blocos, configurações, glossários e termos de glossário.

## Estratégia de preservação de layout

Adotada por página ou região:
1. **Estratégia A** — Substituição de texto no documento original
2. **Estratégia B** — Reconstrução de blocos com coordenadas e estilos
3. **Estratégia C** — Reconstrução de página para layouts complexos

Controle de expansão de texto: espaçamento → quebra de linha → tamanho da fonte → altura do bloco → expansão da área → nova página.

## Segurança

- `contextIsolation: true`, `nodeIntegration: false`
- Preload com APIs explicitamente autorizadas
- IPC com validação de entradas
- Content Security Policy
- Credenciais via `safeStorage`
- Nenhum conteúdo sensível em logs

## Empacotamento

`electron-builder` gera instalador `.exe` para Windows com:
- Ícone próprio
- Nome e versão do aplicativo
- Diretório de instalação configurável
- Atalho no menu Iniciar
- Opção de desinstalação

O serviço Python é empacotado via `extraResources`, sem exigir instalação manual do Python pelo usuário.