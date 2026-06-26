import React, { createContext, useContext, useEffect, useState } from "react";
import translations from "../i18n/translations.js";

export const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी (Hindi)" },
  { code: "te", label: "తెలుగు (Telugu)" },
];

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem("dr-app-language");
    if (saved && translations[saved]) return saved;
    return "en";
  });

  useEffect(() => {
    localStorage.setItem("dr-app-language", language);
    document.documentElement.lang = language;
  }, [language]);

  // t() looks up a key in the current language, falling back to English,
  // then finally to the raw key itself so the UI never shows "undefined".
  const t = (key) => {
    return translations[language]?.[key] ?? translations.en[key] ?? key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within a LanguageProvider");
  return ctx;
}
