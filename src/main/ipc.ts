import { ipcMain } from "electron";

export function setupIpcHandlers(): void {
  // Ping de saúde
  ipcMain.handle("app:ping", () => "pong");

  console.log("[IPC] Handlers registrados (PDF desativado temporariamente)");
}