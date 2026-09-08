import { HashRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { StoreProvider } from "./data/store";
import { Ledger } from "./screens/Ledger";
import { Overview } from "./screens/Overview";
import { Placeholder } from "./screens/Placeholder";
import { Project } from "./screens/Project";

export default function App() {
  return (
    <StoreProvider>
      <HashRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Overview />} />
            <Route path="/ledger" element={<Ledger />} />
            <Route path="/project/:code" element={<Project />} />
            <Route path="/exits" element={<Placeholder name="Exit Ledger" />} />
            <Route path="/warning" element={<Placeholder name="Early Warning" />} />
            <Route path="/predict" element={<Placeholder name="Predictions" />} />
            <Route path="/drivers" element={<Placeholder name="Drivers & Benchmark" />} />
            <Route path="/fields" element={<Placeholder name="Field Audit" />} />
            <Route path="/assistant" element={<Placeholder name="Assistant" />} />
            <Route path="/model-card" element={<Placeholder name="Model Card" />} />
          </Route>
        </Routes>
      </HashRouter>
    </StoreProvider>
  );
}
