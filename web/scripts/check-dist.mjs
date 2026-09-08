import { existsSync, readFileSync } from "node:fs";
const html = "dist/index.html";
if (!existsSync(html)) { console.error("dist/index.html missing"); process.exit(1); }
const t = readFileSync(html, "utf8");
if (!t.includes("/assets/")) { console.error("dist/index.html does not reference /assets/"); process.exit(1); }
console.log("dist ok");
