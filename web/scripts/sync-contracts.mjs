import { copyFileSync, mkdirSync, readdirSync } from "node:fs";
import { join } from "node:path";
const src = join(process.cwd(), "..", "contracts");
const dst = join(process.cwd(), "src", "contracts");
mkdirSync(dst, { recursive: true });
for (const f of readdirSync(src).filter((f) => f.endsWith(".schema.json"))) copyFileSync(join(src, f), join(dst, f));
console.log("contracts synced");
