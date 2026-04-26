import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const frontendRoot = path.join(repoRoot, "app", "frontend");
const outputRoot = path.join(repoRoot, "dist", "frontend");
const staticOutputRoot = path.join(outputRoot, "static");
const apiBaseUrl = (process.env.API_BASE_URL || "").replace(/\/$/, "");

if (existsSync(outputRoot)) {
  rmSync(outputRoot, { recursive: true, force: true });
}

mkdirSync(staticOutputRoot, { recursive: true });

cpSync(path.join(frontendRoot, "index.html"), path.join(outputRoot, "index.html"));
cpSync(path.join(frontendRoot, "app.js"), path.join(staticOutputRoot, "app.js"));
cpSync(path.join(frontendRoot, "styles.css"), path.join(staticOutputRoot, "styles.css"));

const configTemplate = readFileSync(path.join(frontendRoot, "config.js"), "utf8");
const configContents = configTemplate.replace('API_BASE_URL: ""', `API_BASE_URL: "${apiBaseUrl}"`);
writeFileSync(path.join(staticOutputRoot, "config.js"), configContents);
