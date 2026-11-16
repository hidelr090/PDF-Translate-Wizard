import { ipcMain, IpcMainEvent } from 'electron';

export function setupIpcHandlers(mainWindow: Electron.BrowserWindow): void {
  // Ping de saúde
  ipcMain.handle('app:ping', () => 'pong');

  // Placeholder: handlers de PDF, IA, tradução, configurações serão implementados nas próximas fases
  console.log('[IPC] Handlers registrados');
}