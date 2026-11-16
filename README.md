# PDF Translate Wizard

Aplicativo desktop (Windows) para tradução inteligente de PDFs, preservando
layout, diagramação e identidade visual do documento original.

## Stack

- **Electron** — Desktop (Windows 10/11)
- **TypeScript** — Linguagem principal
- **React + Vite** — Frontend
- **Tailwind CSS + shadcn/ui** — Estilização e componentes
- **Zustand** — Gerenciamento de estado
- **SQLite (better-sqlite3)** — Persistência local
- **Zod** — Validação
- **pdf-plumber** — Extração de texto/estrutura (serviço Python)
- **pdf-lib** — Reconstrução de PDF
- **Tesseract / PaddleOCR** — OCR
- **Ollama** — Modelos locais de IA
- **electron-builder** — Empacotamento `.exe`

## Estrutura

```
src/
  main/          # Processo principal Electron
  preload/       # Bridge IPC segura (contextBridge)
  renderer/      # React + Vite
  shared/        # Tipos e schemas compartilhados
python-service/  # Serviço Python (PDF, OCR)
```

## Scripts

| Script | Descrição |
|--------|-----------|
| `npm run dev` | Inicia em modo desenvolvimento |
| `npm run build` | Build do renderer + empacotamento Windows |
| `npm run lint` | Executa ESLint |
| `npm test` | Executa Vitest |

## Licença

MIT