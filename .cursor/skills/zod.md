# Skill: Validação com Zod

## Descrição
Validar dados de entrada (API) e, quando aplicável, formulários frontend, usando schemas Zod com mensagens claras em português.

## Regras da skill
1. **Um schema por entidade/formulário**: ex. `CriarTransacaoSchema`, `AtualizarPerfilSchema`.
2. **Tipos inferidos**: usar `z.infer<typeof Schema>` para gerar tipos TypeScript automaticamente.
3. **Validações obrigatórias**: campos obrigatórios com `.min()`, `.email()`, `.positive()`, `.date()`, etc., conforme o caso.
4. **Mensagens em português**: personalizar mensagens de erro (`{ message: 'Campo obrigatório' }`).
5. **Aplicar antes do caso de uso**: no backend, validar no controller/middleware; no frontend, validar antes de enviar à API.
6. **Não confiar no frontend**: validar sempre no backend, mesmo que o frontend já valide.

## Exemplo
```ts
import { z } from 'zod';

export const CriarTransacaoSchema = z.object({
  descricao: z.string().min(3, 'Descrição deve ter pelo menos 3 caracteres'),
  valor: z.number().positive('Valor deve ser positivo'),
  tipo: z.enum(['receita', 'despesa']),
  data: z.date(),
});

export type CriarTransacaoDTO = z.infer<typeof CriarTransacaoSchema>;
```

## Quando aplicar
Todos os endpoints que recebem entrada do cliente e formulários críticos no frontend/mobile.