import { createContext, useContext, useState } from "react";

const DetailContext = createContext(null);

export function DetailProvider({ children }) {
  const [symbol, setSymbol] = useState(null);
  const value = { symbol, open: setSymbol, close: () => setSymbol(null) };
  return <DetailContext.Provider value={value}>{children}</DetailContext.Provider>;
}

export const useDetail = () => useContext(DetailContext);
