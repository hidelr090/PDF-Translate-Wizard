import Database from 'better-sqlite3';
import path from 'node:path';
import { app } from 'electron';

let db: Database.Database | null = null;

export function initStorage(): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      const userDataPath = app.getPath('userData');
      const dbPath = path.join(userDataPath, 'pdf-translate-wizard.db');
      db = new Database(dbPath);

      db.exec(`
        CREATE TABLE IF NOT EXISTS providers (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          type TEXT NOT NULL,
          api_key_encrypted TEXT,
          base_url TEXT,
          is_active INTEGER DEFAULT 1,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS provider_models (
          id TEXT PRIMARY KEY,
          provider_id TEXT NOT NULL,
          model_id TEXT NOT NULL,
          name TEXT,
          is_default INTEGER DEFAULT 0,
          FOREIGN KEY (provider_id) REFERENCES providers(id)
        );

        CREATE TABLE IF NOT EXISTS translation_jobs (
          id TEXT PRIMARY KEY,
          source_path TEXT NOT NULL,
          output_path TEXT,
          source_language TEXT,
          target_language TEXT,
          provider_id TEXT,
          model_id TEXT,
          status TEXT DEFAULT 'pending',
          progress INTEGER DEFAULT 0,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          completed_at TEXT,
          FOREIGN KEY (provider_id) REFERENCES providers(id)
        );

        CREATE TABLE IF NOT EXISTS translation_settings (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS glossaries (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          description TEXT,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS glossary_terms (
          id TEXT PRIMARY KEY,
          glossary_id TEXT NOT NULL,
          term TEXT NOT NULL,
          translation TEXT NOT NULL,
          preserve_mandatory INTEGER DEFAULT 0,
          FOREIGN KEY (glossary_id) REFERENCES glossaries(id)
        );
      `);

      resolve();
    } catch (err) {
      reject(err);
    }
  });
}

export function getDb(): Database.Database {
  if (!db) {
    throw new Error('Database não inicializado. Chame initStorage() primeiro.');
  }
  return db;
}