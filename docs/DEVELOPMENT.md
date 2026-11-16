# Guia de Desenvolvimento — PDF Translate Wizard

## Configuração do ambiente

### Pré-requisitos

- Node.js 18 ou superior
- npm 9 ou superior

### Instalação

```bash
git clone https://github.com/hidelr090/PDF-Translate-Wizard.git
cd "PDF Translate Wizard"
npm install
```

### Execução em desenvolvimento

```bash
npm run dev
```

O aplicativo será iniciado com recarregamento automático e DevTools abertos.

### Build para produção

```bash
npm run build
```

Gera o instalador Windows (`.exe`) na pasta `release/`.

### Lint

```bash
npm run lint
```

### Testes

```bash
npm test
```

## Estrutura de diretórios

```
.
├── .cursor/              # Personas, skills e rules do Cursor
├── .github/              # Templates de issue e PR
├── docs/                 # Documentação técnica
├── python-service/       # Serviço Python (PDF, OCR)
├── src/
│   ├── main/             # Processo principal Electron
│   ├── preload/          # Bridge IPC segura
│   ├── renderer/         # React + Vite
│   └── shared/           # Tipos e schemas compartilhados
├── electron-builder.json # Configuração do instalador Windows
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
└── README.md
```

## Adicionando um novo provedor de IA

1. Crie uma pasta em `src/modules/ai/infrastructure/providers/<nome-do-provedor>/`
2. Implemente a interface `AIProvider` (`validateConnection`, `listModels`, `translate`, `getCapabilities`)
3. Registre o provedor no `ProviderManager`
4. Adicione testes unitários para o adapter

## Adicionando um novo idioma

Os idiomas são configurados em um arquivo de constantes. Basta adicionar o novo idioma à lista de idiomas suportados.

## Convenções de código

- TypeScript strict mode
- Nomes de arquivos em kebab-case
- Componentes React em PascalCase
- Commits seguindo Conventional Commits
- Documentar decisões arquiteturais importantes em `docs/`

## Testes

- Testes unitários com Vitest (`tests/unit/`)
- Testes de integração com Vitest (`tests/integration/`)
- Testes de regressão visual com Playwright (`tests/e2e/`)

Documentos de referência para regressão visual devem ser mantidos em `tests/fixtures/pdf/`.