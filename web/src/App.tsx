import { HashRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { StoreProvider } from "./data/store";
import { Assistant } from "./screens/Assistant";
import { Drivers } from "./screens/Drivers";
import { Exits } from "./screens/Exits";
import { Fields } from "./screens/Fields";
import { Ledger } from "./screens/Ledger";
import { ModelCard } from "./screens/ModelCard";
import { Overview } from "./screens/Overview";
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
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/model-card" element={<ModelCard />} />
          </Route>
        </Routes>
      </HashRouter>
    </StoreProvider>
  );
}
