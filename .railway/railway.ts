import { defineRailway, github, project, service, volume } from "railway/iac";
// This repository manages only its own resources in the environment. Other
// repositories export their own partial name.
// See https://docs.railway.com/infrastructure-as-code#multi-repo-projects
export const partial = "jenbina";
export default defineRailway(() => {
  // Jenbina's memory (ChromaDB + SQLite); JENBINA_DATA_DIR points at its mount path.
  // Keep the volume and its mount declared: an apply without them detaches it.
  const memory = volume("jenbina-volume", { region: "europe-west4-drams3a", sizeMB: 5000 });

  const jenbina = service("jenbina", {
    source: github("motya770/jenbina", { branch: "main", checkSuites: false }),
    build: { buildEnvironment: "V3", builder: "RAILPACK" },
    start: "streamlit run core/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true",
    healthcheck: "/_stcore/health",
    healthcheckTimeout: 300,
    replicas: { "europe-west4-drams3a": 1 },
    deploy: { restartPolicyType: "ON_FAILURE", restartPolicyMaxRetries: 3 },
    volumeMounts: { "/jenbina": memory },
  });

  return project("selfless-education", {
    variables: { managed: false },
    resources: [jenbina, memory],
  });
});
