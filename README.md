# PDF Translate Wizard

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Electron](https://img.shields.io/badge/Electron-31+-47848F?logo=electron&logoColor=white)](https://www.electronjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5+-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Windows](https://img.shields.io/badge/Windows-10/11-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)

**Aplicativo desktop para tradução inteligente de PDFs, preservando layout, diagramação e identidade visual do documento original.**

</div>

---

## 📖 Sobre o projeto

O **PDF Translate Wizard** é um aplicativo desktop para Windows (10/11) desenvolvido com **Electron**, **React**, **TypeScript** e **Vite**, cujo objetivo é realizar traduções de documentos PDF por meio de modelos de Inteligência Artificial, preservando com a maior fidelidade possível a estrutura, a diagramação e a identidade visual do documento original.

Não é apenas um tradutor de texto que extrai o conteúdo de um PDF. É um **mecanismo de tradução documental** que compreende a estrutura do PDF, identifica elementos visuais, traduz o conteúdo preservando o contexto e reconstrói o documento mantendo suas características visuais.

---

## ✅ Principais características

- Suporte a provedores comerciais (OpenAI, Anthropic, Gemini, Azure, Mistral, DeepSeek, xAI, OpenRouter)
- Modelos locais via **Ollama** (funcionalidade de primeira classe)
- Preservação de layout original (dimensões, margens, colunas, imagens, tabelas)
- Glossários personalizados para preservação de termos técnicos
- OCR para documentos digitalizados
- Processamento de documentos extensos com retomada de interrupções
- Interface intuitiva para usuários não técnicos
- Credenciais armazenadas com segurança (Electron `safeStorage`)
- Instalador Windows independente (`.exe`)

---

## 🚀 Começando

### Pré-requisitos

- **Windows 10 ou 11** (para execução do instalador)
- Para desenvolvimento: **Node.js 18+** e **npm**

### Instalação (usuário final)

1. Baixe o instalador `.exe` mais recente na seção [Releases](https://github.com/hidelr090/PDF-Translate-Wizard/releases)
2. Execute o instalador e siga as instruções na tela
3. O aplicativo estará disponível no menu Iniciar

> O Ollama é uma dependência **opcional**. Você pode usar provedores comerciais (OpenAI, Anthropic, etc.) sem instalar nada além do aplicativo.

### Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/hidelr090/PDF-Translate-Wizard.git
cd "PDF Translate Wizard"

# Instale as dependências
npm install

# Inicie em modo desenvolvimento
npm run dev

# Build para produção (gera instalador Windows)
npm run build
```

### Scripts disponíveis


---

## 🏗️ Arquitetura

O projeto segue **Clean Architecture** com separação clara entre processos do Electron e camadas de domínio, aplicação e infraestrutura.

### Processos do Electron

| Processo | Responsabilidades |
|----------|-------------------|
| **Main** | Ciclo de vida, janela, IPC, arquivos, serviço Python, SQLite, tarefas de tradução |
| **Preload** | Bridge segura (`contextBridge`) expondo apenas APIs autorizadas ao Renderer |
| **Renderer** | Interface React + Zustand, consumo de IPC, visualização de PDF |

### Serviço Python interno

Processamento pesado de PDF e OCR roda em um serviço Python separado, empacotado com o Electron via `electron-builder` (`extraResources`). O usuário **não precisa instalar Python**.

### Persistência

Utiliza **SQLite** local para armazenar configurações de provedores, modelos, preferências de tradução, histórico de documentos e glossários. **Credenciais (API Keys)** são armazenadas exclusivamente no **Electron `safeStorage`**, nunca em texto puro no banco de dados.
| Script | Descrição |
|--------|-----------|
| `npm run dev` | Inicia o aplicativo em modo desenvolvimento com recarregamento automático |
| `npm run build` | Gera o build do renderer e empacota o instalador Windows (`.exe`) |
| `npm run lint` | Executa o ESLint para verificar qualidade do código |

---

## 🗺️ Roadmap

O desenvolvimento está organizado em 7 fases:

| Fase | Objetivo | Status |
|------|----------|--------|
| 1 | Fundação do aplicativo (Electron, React, Vite, SQLite, importação de PDF) | ✅ Concluída |
| 2 | Motor de processamento de PDFs (extração, coordenadas, OCR, classificação) | 🔲 Pendente |
| 3 | Sistema de provedores de IA (OpenAI, Anthropic, Gemini, Ollama, credenciais) | 🔲 Pendente |
| 4 | Motor de tradução (segmentação, glossários, prompts, retomada) | 🔲 Pendente |
| 5 | Reconstrução de PDFs (estratégias A/B/C, ajuste tipográfico, exportação) | 🔲 Pendente |
| 6 | Interface completa (configuração, progresso, comparação, histórico) | 🔲 Pendente |
| 7 | Qualidade e distribuição (testes, regressão visual, instalador Windows) | 🔲 Pendente |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Leia o [Guia de Contribuição](CONTRIBUTING.md) para detalhes sobre como enviar pull requests, relatar bugs e sugerir novas funcionalidades.

### Convenções de commit

Seguimos **Conventional Commits**: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`.

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📞 Suporte

Se você encontrar um problema ou tiver uma sugestão, abra uma [issue](https://github.com/hidelr090/PDF-Translate-Wizard/issues) no GitHub.

---

<div align="center">
  <p>Desenvolvido com ❤️ para traduzir PDFs com inteligência e preservação de layout.</p>
</div>
| `npm test` | Executa a suíte de testes com Vitest |