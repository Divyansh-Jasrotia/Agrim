import { HashRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { StoreProvider } from "./data/store";
import { Drivers } from "./screens/Drivers";
import { Exits } from "./screens/Exits";
import { Fields } from "./screens/Fields";
import { Ledger } from "./screens/Ledger";
import { Overview } from "./screens/Overview";
import { Placeholder } from "./screens/Placeholder";
import { Predict } from "./screens/Predict";
import { Project } from "./screens/Project";
import { Warning } from "./screens/Warning";

export default function App() {
  return (
    <StoreProvider>
      <HashRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Overview />} />
            <Route path="/ledger" element={<Ledger />} />
            <Route path="/project/:code" element={<Project />} />
            <Route path="/exits" element={<Exits />} />
            <Route path="/warning" element={<Warning />} />
            <Route path="/predict" element={<Predict />} />
            <Route path="/drivers" element={<Drivers />} />
            <Route path="/fields" element={<Fields />} />
            <Route path="/assistant" element={<Placeholder name="Assistant" />} />
            <Route path="/model-card" element={<Placeholder name="Model Card" />} />
          </Route>
        </Routes>
      </HashRouter>
    </StoreProvider>
  );
}
