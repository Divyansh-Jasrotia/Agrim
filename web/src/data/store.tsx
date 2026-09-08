import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { loadBundle, type Bundle } from "./load";

interface Store { bundle: Bundle | null; error: string | null; sector: string | null; setSector: (s: string | null) => void }
const Ctx = createContext<Store>({ bundle: null, error: null, sector: null, setSector: () => {} });

export function StoreProvider({ children }: { children: ReactNode }) {
  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sector, setSector] = useState<string | null>(null);
  useEffect(() => { loadBundle().then(setBundle).catch((e: Error) => setError(e.message)); }, []);
  return <Ctx.Provider value={{ bundle, error, sector, setSector }}>{children}</Ctx.Provider>;
}

export const useBundle = () => useContext(Ctx);
