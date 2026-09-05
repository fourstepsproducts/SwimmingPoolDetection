import React, { createContext, useContext, useState } from 'react';

const AnalysisContext = createContext(null);

export const AnalysisProvider = ({ children }) => {
  const [analysisResult, setAnalysisResult] = useState(null);

  const clearAnalysis = () => {
    setAnalysisResult(null);
  };

  return (
    <AnalysisContext.Provider value={{
      analysisResult,
      setAnalysisResult,
      clearAnalysis
    }}>
      {children}
    </AnalysisContext.Provider>
  );
};

export const useAnalysis = () => useContext(AnalysisContext);
export default AnalysisContext;
