import { spawn, ChildProcess } from 'node:child_process';
import path from 'node:path';

let pythonProcess: ChildProcess | null = null;

export async function spawnPythonService(): Promise<void> {
  // Em desenvolvimento, tentamos usar python3 do sistema se disponível.
  // Em produção, o Python é empacotado via electron-builder (extraResources).
  let pythonBin: string;

  if (import.meta.env.DEV) {
    pythonBin = 'python3';
  } else {
    const resourcesPath = process.resourcesPath;
    pythonBin = path.join(resourcesPath, 'python-service', '.venv', 'bin', 'python3');
  }

  const scriptPath = path.join(__dirname, '../../python-service/main.py');

  pythonProcess = spawn(pythonBin, [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  pythonProcess.stdout?.on('data', (data: Buffer) => {
    console.log('[Python]', data.toString().trim());
  });

  pythonProcess.stderr?.on('data', (data: Buffer) => {
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

export function getPythonProcess(): ChildProcess | null {
  return pythonProcess;
}