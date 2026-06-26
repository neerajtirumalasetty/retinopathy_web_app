import React, { useState } from "react";
import PatientForm from "./components/PatientForm.jsx";
import ResultPanel from "./components/ResultPanel.jsx";
import Toolbar from "./components/Toolbar.jsx";
import { useLanguage } from "./context/LanguageContext.jsx";
import { predictRetinopathy } from "./api.js";

export default function App() {
  const { t, language } = useLanguage();

  const [patient, setPatient] = useState({
    age: "",
    gender: "",
    diabetic_history: "",
    symptoms: "",
  });

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!imageFile) {
      setError(t("uploadFirst"));
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);

    try {
      const data = await predictRetinopathy(imageFile, patient, language);
      setResult(data);
    } catch (err) {
      console.error(err);
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        t("genericError");
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-8">
      <header className="max-w-6xl mx-auto mb-8 flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-medical-600 to-medical-500 flex items-center justify-center shadow-md">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="w-6 h-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.8}
                d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.8}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-slate-800 dark:text-slate-100">
              {t("appTitle")}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">{t("appSubtitle")}</p>
          </div>
        </div>

        <Toolbar />
      </header>

      <main className="max-w-6xl mx-auto grid md:grid-cols-2 gap-6">
        <PatientForm
          patient={patient}
          setPatient={setPatient}
          imageFile={imageFile}
          setImageFile={setImageFile}
          imagePreview={imagePreview}
          setImagePreview={setImagePreview}
          onAnalyze={handleAnalyze}
          loading={loading}
          error={error}
        />
        <ResultPanel result={result} loading={loading} />
      </main>

      <footer className="max-w-6xl mx-auto mt-8 text-center text-xs text-slate-400 dark:text-slate-500">
        {t("footer")}
      </footer>
    </div>
  );
}
