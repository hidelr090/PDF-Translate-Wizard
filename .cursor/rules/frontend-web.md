# Rule: Regras do Frontend Web (homefinapp-web / backoffice)

Aplica-se a `homefinapp-web` e `homefinapp-backoffice` (React + Vite + TypeScript).

## Componentes
- Todo componente com `interface Props` tipada; proibido `any`.
- Um componente faz uma coisa só; lógica de negócio em hooks customizados.

## Estilo
- Usar **styled-components** com o tema central em `src/styles/themes.ts`.
- Não usar valores de cor/espaçamento hard-coded; usar variáveis do tema.

## Estado
- Estado de servidor com **React Query** (`useQuery` / `useMutation`).
- Tratar sempre: loading, error, empty state e success.
- Estado local de UI com `useState`/`useReducer`; evitar contexto para estado de servidor.

## Acessibilidade básica
- Labels associados a inputs (`htmlFor`), `alt` em imagens, navegação por teclado.

## Quando aplicar
Criação ou edição de páginas/componentes no frontend web.