# Rule: Regras de TypeScript

Aplica-se a todos os arquivos `.ts` / `.tsx` do workspace.

1. **Strict mode obrigatório**: `strict: true` no `tsconfig.json`; não desabilitar checks por arquivo.
2. **Proibido `any`**: usar `unknown` + type guard, ou definir o tipo correto. `any` apenas com justificativa de código comentada.
3. **Tipagem explícita**: funções com parâmetros e retorno tipados; interfaces para modelos, DTOs e props de componentes.
4. **Não usar `// @ts-ignore`** para esconder erros de tipo.
5. **Aliases de importação**: usar `@app/*`, `@domain/*`, `@application/*`, `@infra/*`, `@controllers/*`, `@routes/*`, `@shared/*` conforme `tsconfig.json` de cada app.
6. **Nenhum erro de build**: `npm run build` / `tsc` deve passar sem erros antes de commitar.

## Exemplo correto (Homefin API)
```ts
interface TransacaoDTO {
  id: string;
  valor: number;
  tipo: 'receita' | 'despesa';
}

async function listarTransacoes(): Promise<TransacaoDTO[]> { ... }
```

## Quando aplicar
Edição ou criação de qualquer arquivo TypeScript no workspace.