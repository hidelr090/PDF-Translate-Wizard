import { BrowserWindow } from 'electron';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
export function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 900,
        minHeight: 600,
        show: false,
        webPreferences: {
            preload: path.join(__dirname, '../preload/index.js'),
            contextIsolation: true,
            nodeIntegration: false,
        },
    });
    win.once('ready-to-show', () => {
        win.show();
    });
    if (import.meta.env.DEV) {
        win.loadURL('http://localhost:5123');
        win.webContents.openDevTools();
    }
    else {
        win.loadFile(path.join(__dirname, '../../dist/renderer/index.html'));
    }
    return win;
}
