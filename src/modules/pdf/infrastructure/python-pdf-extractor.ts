import { ChildProcess, spawn } from "node:child_process";
import path from "node:path";
import {
  PDFExtractor,
  PDFDocumentInfo,
  DocumentClassification,
} from "../domain/interfaces/pdf-extractor";

interface PythonMessage {
  type: string;
  [key: string]: any;
}

export class PythonPDFExtractor implements PDFExtractor {
  private pythonProcess: ChildProcess | null = null;
  private resolveMap: Map<string, (value: any) => void> = new Map();
  private rejectMap: Map<string, (error: Error) => void> = new Map();
  private messageId = 0;

  constructor() {
    this.startPythonService();
  }

  private startPythonService(): void {
    let pythonBin: string;

    if (import.meta.env.DEV) {
      pythonBin = "python3";
    } else {
      const resourcesPath = process.resourcesPath;
      pythonBin = path.join(
        resourcesPath,
        "python-service",
        ".venv",
        "bin",
        "python3"
      );
    }

    const scriptPath = path.join(__dirname, "../../../python-service/main.py");

    this.pythonProcess = spawn(pythonBin, [scriptPath], {
      stdio: ["pipe", "pipe", "pipe"],
    });

    this.pythonProcess.stdout?.on("data", (data: Buffer) => {
      const lines = data.toString().split("\n").filter(Boolean);
      for (const line of lines) {
        try {
          const message = JSON.parse(line) as PythonMessage;
          this.handlePythonMessage(message);
        } catch (err) {
          console.error("[Python] Erro ao parsear mensagem:", err);
        }
      }
    });

    this.pythonProcess.stderr?.on("data", (data: Buffer) => {
      console.error("[Python stderr]", data.toString().trim());
    });

    this.pythonProcess.on("exit", (code) => {
      console.log(`[Python] processo finalizado com código ${code}`);
      this.pythonProcess = null;
    });
  }

  private handlePythonMessage(message: PythonMessage): void {
    const { type } = message;

    if (type === "extraction_result" || type === "ocr_result" || type === "classification_result") {
      const requestId = message.requestId;
      const resolve = this.resolveMap.get(requestId);
      if (resolve) {
        resolve(message.data);
        this.resolveMap.delete(requestId);
        this.rejectMap.delete(requestId);
      }
    } else if (type === "error") {
      const requestId = message.requestId;
      const reject = this.rejectMap.get(requestId);
      if (reject) {
        reject(new Error(message.message));
        this.rejectMap.delete(requestId);
        this.resolveMap.delete(requestId);
      }
    } else if (type === "ready") {
      console.log("[Python] serviço pronto");
    } else if (type === "pong") {
      console.log("[Python] pong recebido");
    }
  }

  private sendRequest(
    action: string,
    payload: Record<string, any>
  ): Promise<any> {
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

  async extract(filePath: string): Promise<PDFDocumentInfo> {
    return this.sendRequest("extract", { file_path: filePath });
  }

  async classify(filePath: string): Promise<DocumentClassification> {
    return this.sendRequest("classify", { file_path: filePath });
  }

  async ocr(
    filePath: string,
    pageNumber?: number,
    language?: string
  ): Promise<any> {
    return this.sendRequest("ocr", {
      file_path: filePath,
      page_number: pageNumber || 0,
      language: language || "por+eng",
    });
  }
}