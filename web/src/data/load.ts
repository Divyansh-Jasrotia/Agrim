import Ajv2020 from "ajv/dist/2020";
import projectsSchema from "../contracts/projects.schema.json";
import findingsSchema from "../contracts/findings.schema.json";
import modelsSchema from "../contracts/models.schema.json";
import briefsSchema from "../contracts/briefs.schema.json";
import modelCardSchema from "../contracts/model_card.schema.json";
import type { Project, Projects } from "../types/projects";
import type { Findings } from "../types/findings";
import type { Models } from "../types/models";
import type { Briefs } from "../types/briefs";
import type { ModelCard } from "../types/model_card";

export interface Bundle {
  projects: Projects;
  findings: Findings;
  models: Models | null;
  briefs: Briefs | null;
  modelCard: ModelCard | null;
  byCode: Map<string, Project>;
}

const ajv = new Ajv2020({ allErrors: false, strict: false });

async function fetchJson(path: string): Promise<unknown | null> {
  const r = await fetch(path);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  // An optional file (briefs.json) is absent until its task runs. The static demo
  // server answers that with 404, but the dev server answers any unknown path with
  // the SPA fallback: 200 and index.html. Content-type is the one absence signal
  // both servers agree on, so check it before parsing.
  if (!(r.headers.get("content-type") ?? "").includes("application/json")) return null;
  return r.json();
}

function validate<T>(name: string, schema: object, data: unknown): T {
  const check = ajv.compile(schema);
  if (!check(data)) {
    const e = check.errors?.[0];
    throw new Error(`${name} violates the contract at "${e?.instancePath ?? ""}": ${e?.message ?? "unknown"}`);
  }
  return data as T;
}

export async function loadBundle(): Promise<Bundle> {
  const [p, f, m, b, c] = await Promise.all([
    fetchJson("data/projects.json"), fetchJson("data/findings.json"), fetchJson("data/models.json"),
    fetchJson("data/briefs.json"), fetchJson("data/model_card.json"),
  ]);
  if (p == null || f == null) throw new Error("projects.json and findings.json are required (run findings/run.py)");
  const projects = validate<Projects>("projects.json", projectsSchema, p);
  const findings = validate<Findings>("findings.json", findingsSchema, f);
  const models = m == null ? null : validate<Models>("models.json", modelsSchema, m);
  const briefs = b == null ? null : validate<Briefs>("briefs.json", briefsSchema, b);
  const modelCard = c == null ? null : validate<ModelCard>("model_card.json", modelCardSchema, c);
  return { projects, findings, models, briefs, modelCard, byCode: new Map(projects.map((x) => [x.project_code, x])) };
}
