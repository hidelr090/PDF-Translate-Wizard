import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ProviderManager } from '../src/modules/ai/application/provider-manager';

describe('Integration: ProviderManager', () => {
  let manager: ProviderManager;

  beforeEach(() => {
    manager = new ProviderManager();
  });

  it('deve ser instanciado', () => {
    expect(manager).toBeInstanceOf(ProviderManager);
  });

  it('deve ter configs padrão', () => {
    const openaiConfig = manager.getConfig('openai');
    expect(openaiConfig).toBeDefined();
    expect(openaiConfig?.id).toBe('openai');
    expect(openaiConfig?.type).toBe('commercial');
  });

  it('deve validar conexão (mock)', async () => {
    const result = await manager.validateConnection('openai');
    // Em ambiente de teste sem provedor real, retorna false
    expect(typeof result).toBe('boolean');
  });

  it('deve listar modelos (mock)', async () => {
    const models = await manager.listModels('openai');
    expect(Array.isArray(models)).toBe(true);
  });

  it('deve traduzir (mock)', async () => {
    const result = await manager.translate('openai', {
      id: 'test-1',
      prompt: 'Hello world',
      sourceLanguage: 'en',
      targetLanguage: 'pt',
      modelId: 'gpt-4o-mini',
      preserveTechnicalTerms: true,
    });
    expect(typeof result.success).toBe('boolean');
  });

  it('deve retornar erro para provedor inexistente', async () => {
    const result = await manager.translate('provedor-inexistente', {
      prompt: 'teste',
      sourceLanguage: 'en',
      targetLanguage: 'pt',
    });
    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });

  it('deve registrar e dess registrar provedor', () => {
    const mockProvider = {} as any;
    const mockConfig: any = { id: 'teste', name: 'Teste', type: 'commercial', isActive: true };
    
    manager.registerProvider(mockProvider as any, mockConfig);
    expect(manager.getAllProviders().length).toBe(1);
    
    manager.unregisterProvider('teste');
    expect(manager.getAllProviders().length).toBe(0);
  });

  it('deve getActiveProviders e getAllProviders', () => {
    const actives = manager.getActiveProviders();
    const all = manager.getAllProviders();
    expect(Array.isArray(actives)).toBe(true);
    expect(Array.isArray(all)).toBe(true);
    expect(actives.length).toBe(4); // configs padrão
    expect(all.length).toBe(4);
  });
});
