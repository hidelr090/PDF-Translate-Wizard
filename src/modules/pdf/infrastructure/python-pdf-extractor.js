import { spawn } from "node:child_process";
import path from "node:path";
export class PythonPDFExtractor {
    pythonProcess = null;
    resolveMap = new Map();
    rejectMap = new Map();
    messageId = 0;
    constructor() {
        this.startPythonService();
    }
    startPythonService() {
        let pythonBin;
        if (import.meta.env.DEV) {
            pythonBin = "python3";
        }
        else {
            const resourcesPath = process.resourcesPath;
            pythonBin = path.join(resourcesPath, "python-service", ".venv", "bin", "python3");
        }
        const scriptPath = path.join(__dirname, "../../../python-service/main.py");
        this.pythonProcess = spawn(pythonBin, [scriptPath], {
            stdio: ["pipe", "pipe", "pipe"],
        });
        this.pythonProcess.stdout?.on("data", (data) => {
            const lines = data.toString().split("\n").filter(Boolean);
            for (const line of lines) {
                try {
                    const message = JSON.parse(line);
                    this.handlePythonMessage(message);
                }
                catch (err) {
                    console.error("[Python] Erro ao parsear mensagem:", err);
                }
            }
        });
        this.pythonProcess.stderr?.on("data", (data) => {
            console.error("[Python stderr]", data.toString().trim());
        });
        this.pythonProcess.on("exit", (code) => {
            console.log(`[Python] processo finalizado com código ${code}`);
            this.pythonProcess = null;
        });
    }
    handlePythonMessage(message) {
        const { type } = message;
        if (type === "extraction_result" || type === "ocr_result" || type === "classification_result") {
            const requestId = message.requestId;
            const resolve = this.resolveMap.get(requestId);
            if (resolve) {
                resolve(message.data);
                this.resolveMap.delete(requestId);
                this.rejectMap.delete(requestId);
            }
        }
        else if (type === "error") {
            const requestId = message.requestId;
            const reject = this.rejectMap.get(requestId);
            if (reject) {
                reject(new Error(message.message));
                this.rejectMap.delete(requestId);
                this.resolveMap.delete(requestId);
            }
        }
        else if (type === "ready") {
            console.log("[Python] serviço pronto");
        }
        else if (type === "pong") {
            console.log("[Python] pong recebido");
        }
    }
    sendRequest(action, payload) {
        return new Promise((resolve, reject) => {
            if (!this.pythonProcess) {
                reject(new Error("Serviço Python não está rodando"));
                return;
            }
            const requestId = `req_${++this.messageId}`;
            this.resolveMap.set(requestId, resolve);
            this.rejectMap.set(requestId, reject);
            const message = {
                requestId,
                type: action,
                ...payload,
            };
            this.pythonProcess.stdin?.write(JSON.stringify(message) + "\n");
        });
    }
    async extract(filePath) {
        return this.sendRequest("extract", { file_path: filePath });
    }
    async classify(filePath) {
        return this.sendRequest("classify", { file_path: filePath });
    }
    async ocr(filePath, pageNumber, language) {
        return this.sendRequest("ocr", {
            file_path: filePath,
            page_number: pageNumber || 0,
            language: language || "por+eng",
        });
    }
}
