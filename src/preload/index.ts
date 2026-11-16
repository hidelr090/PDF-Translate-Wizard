import { contextBridge, ipcRenderer } from 'electron';

// API exposta ao Renderer. Somente canais explicitamente autorizados.
contextBridge.exposeInMainApi('electronAPI', {
  ping: () => ipcRenderer.invoke('app:ping'),
  // Canais adicionais serão expostos conforme as fases forem implementadas
});