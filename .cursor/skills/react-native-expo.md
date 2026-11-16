# Skill: Mobile (React Native / Expo)

## Descrição
Desenvolver o `homefinapp-mobile` com foco em desempenho, usabilidade móvel e integração com a API do Homefin.

## Stack
- React Native / Expo
- TypeScript
- Navegação por stack/tabs
- Integração com `homefinapp-api` (mesmos contratos Swagger)

## Regras da skill
1. **Componentes leves**: evitar bibliotecas pesadas; priorizar componentes nativos do React Native/Expo.
2. **Tratamento de rede**: detectar falta de conexão, exibir mensagem amigável e permitir retry.
3. **Estados de API**: loading, error e empty state em toda tela que consome dados.
4. **Contratos da API**: usar os mesmos schemas/Zod e endpoints documentados no Swagger do backend.
5. **Variáveis de ambiente**: URL da API por ambiente (dev/staging/prod) via `.env`/Expo config; nunca commitar valores reais.
6. **Build**: manter `app.json` atualizado; configurar EAS/Expo quando for gerar builds.
7. **Responsividade**: layouts que funcionem em diferentes tamanhos de tela.

## Quando aplicar
Criação ou edição de telas, navegação e integração com API no `homefinapp-mobile`.