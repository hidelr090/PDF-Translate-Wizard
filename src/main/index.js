import { app, BrowserWindow } from 'electron';
import { createWindow } from './window';
import { setupIpcHandlers } from './ipc';
import { initStorage } from './storage';
import { spawnPythonService } from './python-service';
// Garante instância única
if (!app.requestSingleInstanceLock()) {
    app.quit();
    process.exit(0);
}
let mainWindow = null;
app.whenReady().then(async () => {
    // Inicializa persistência local (SQLite)
    await initStorage();
    // Inicializa serviço Python (extração PDF, OCR)
    await spawnPythonService();
    // Cria janela principal
    mainWindow = createWindow();
    // Registra handlers de IPC
    setupIpcHandlers();
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            mainWindow = createWindow();
        }
    });
});
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
app.on('second-instance', () => {
    if (mainWindow) {
        if (mainWindow.isMinimized())
            mainWindow.restore();
        mainWindow.focus();
    }
});
