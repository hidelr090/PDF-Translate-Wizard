import { spawn } from 'node:child_process';
import path from 'node:path';
let pythonProcess = null;
export async function spawnPythonService() {
    // Em desenvolvimento, tentamos usar python3 do sistema se disponível.
    // Em produção, o Python é empacotado via electron-builder (extraResources).
    let pythonBin;
    if (import.meta.env.DEV) {
        pythonBin = 'python3';
    }
    else {
        const resourcesPath = process.resourcesPath;
        pythonBin = path.join(resourcesPath, 'python-service-updated', '.venv', 'bin', 'python3');
    }
    const scriptPath = path.join(__dirname, '../../python-service-updated/main.py');
    pythonProcess = spawn(pythonBin, [scriptPath], {
        stdio: ['pipe', 'pipe', 'pipe'],
    });
    pythonProcess.stdout?.on('data', (data) => {
        console.log('[Python]', data.toString().trim());
    });
    pythonProcess.stderr?.on('data', (data) => {
        console.error('[Python stderr]', data.toString().trim());
    });
    pythonProcess.on('exit', (code) => {
        console.log(`[Python] processo finalizado com código ${code}`);
        pythonProcess = null;
    });
    // Aguarda inicialização básica (não bloqueante)
    setTimeout(() => {
        if (pythonProcess) {
            console.log('[Python] serviço iniciado');
        }
    }, 1000);
}
export function getPythonProcess() {
    return pythonProcess;
}
