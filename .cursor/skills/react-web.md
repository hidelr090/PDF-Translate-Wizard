# Skill: Frontend Web (React + TypeScript + styled-components)

## Descrição
Desenvolver interfaces no `homefinapp-web` e `homefinapp-backoffice` com componentes tipados, estado bem gerenciado e estilo consistente.

## Stack
- React 18 + Vite + TypeScript
- styled-components (tema central em `src/styles/themes.ts`)
- React Query v3 (estado de servidor)
- React Router DOM v6 (rotas)
- ESLint + @typescript-eslint + react-hooks

## Regras da skill
1. **Componentes tipados**: `interface Props { ... }` para todos os componentes; evitar `any`.
2. **Estilo via tema**: usar cores e espaçamentos de `src/styles/themes.ts` via styled-components; evitar valores hard-coded.
3. **Estado de servidor com React Query**: chamadas de API via `useQuery`/`useMutation`, com tratamento de loading, error e success.
4. **Estado local apenas quando necessário**: `useState`/`useReducer` para UI; não usar contexto para estado de servidor.
5. **Hooks customizados**: extrair lógica de negócio do componente para hooks (`src/hooks` quando existir).
6. **Acessibilidade básica**: `htmlFor` em labels, `alt` em imagens, navegação por teclado.
7. **Tratamento de erros**: todo consumo de API deve tratar estados de erro e exibir mensagem ao usuário.

## Exemplo de padrão
```tsx
interface TransacaoCardProps { transacao: Transacao; }
const TransacaoCard = ({ transacao }: TransacaoCardProps) => { ... }
```

## Quando aplicar
Criação ou edição de páginas/componentes em `homefinapp-web` e `homefinapp-backoffice`.