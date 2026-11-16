# Skill: TypeScript Strict

## Descrição
Escrever TypeScript com `strict: true`, tipagem explícita e evitando `any`. Aplica-se a todos os apps do monorepo (API, web, backoffice, mobile).

## O que essa skill envolve
- `tsconfig.json` com `strict: true`, `noImplicitAny`, `strictNullChecks`
- Usar `interface`/`type` para modelos de dados, DTOs e respostas de API
- Evitar `any`; usar `unknown` quando o tipo for realmente desconhecido, seguido de narrow/type guard
- Tipar retorno de funções e parâmetros
- Não usar `// @ts-ignore` nem `as any` para burlar o compilador
- Usar enums ou union types para campos com conjunto fixo de valores (ex: tipo de transação: `receita` | `despesa`)

## Padrão do workspace Homefin
```ts
// Bom
interface Transacao {
  id: string;
  descricao: string;
  valor: number;
  tipo: 'receita' | 'despesa';
  data: Date;
}

// Evitar
const transacao: any = {};
```

## Checklist de validação
- [ ] Nenhum `any` no código novo (exceto justificado e comentado)
- [ ] Tipos de resposta da API definidos
- [ ] `tsc` passa sem erros no build
- [ ] ESLint `@typescript-eslint/no-explicit-any` não dispara como erro

## Quando aplicar
Sempre que criar ou editar arquivos `.ts` / `.tsx` em qualquer app do workspace.