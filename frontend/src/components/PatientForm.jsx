import React, { useRef } from "react";
import { useLanguage } from "../context/LanguageContext.jsx";

const RISK_COLORS = {
  Low: "bg-green-100 text-green-700 border-green-300",
  Medium: "bg-amber-100 text-amber-700 border-amber-300",
  High: "bg-orange-100 text-orange-700 border-orange-300",
  Critical: "bg-red-100 text-red-700 border-red-300",
};

export default function PatientForm({
  patient,
  setPatient,
  imageFile,
  setImageFile,
  imagePreview,
  setImagePreview,
  onAnalyze,
  loading,
  error,
}) {
  const fileInputRef = useRef(null);
  const { t } = useLanguage();

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleChange = (field) => (e) => {
    setPatient((prev) => ({ ...prev, [field]: e.target.value }));
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-card p-6 flex flex-col gap-6 h-full transition-colors">
      <div>
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-medical-500"></span>
          {t("patientInfo")}
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {t("patientInfoDesc")}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">
            {t("age")}
          </label>
          <input
            type="number"
            min="0"
            max="120"
            value={patient.age}
            onChange={handleChange("age")}
            placeholder={t("agePlaceholder")}
            className="w-full rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent placeholder:text-slate-400 dark:placeholder:text-slate-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">
            {t("gender")}
          </label>
          <select
            value={patient.gender}
            onChange={handleChange("gender")}
            className="w-full rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent"
          >
            <option value="">{t("select")}</option>
            <option value="male">{t("male")}</option>
            <option value="female">{t("female")}</option>
            <option value="other">{t("other")}</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">
          {t("diabeticHistory")}
        </label>
        <input
          type="text"
          value={patient.diabetic_history}
          onChange={handleChange("diabetic_history")}
          placeholder={t("diabeticHistoryPlaceholder")}
          className="w-full rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent placeholder:text-slate-400 dark:placeholder:text-slate-500"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">
          {t("symptoms")}
        </label>
        <textarea
          value={patient.symptoms}
          onChange={handleChange("symptoms")}
          placeholder={t("symptomsPlaceholder")}
          rows={2}
          className="w-full rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent resize-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-2">
          {t("retinalImage")}
        </label>
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileInputRef.current?.click()}
          className="cursor-pointer border-2 border-dashed border-medical-200 dark:border-medical-700 rounded-xl bg-medical-50/50 dark:bg-medical-900/20 hover:bg-medical-50 dark:hover:bg-medical-900/30 transition-colors flex flex-col items-center justify-center text-center p-4 min-h-[180px]"
        >
          {imagePreview ? (
            <img
              src={imagePreview}
              alt="Retinal preview"
              className="max-h-40 rounded-lg object-contain"
            />
          ) : (
            <>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-10 h-10 text-medical-400 mb-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 7.5L12 3m0 0L7.5 7.5M12 3v13.5"
                />
              </svg>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t("dragDrop")}</p>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{t("fileTypes")}</p>
            </>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm rounded-lg p-3">
          {error}
        </div>
      )}

      <button
        onClick={onAnalyze}
        disabled={loading || !imageFile}
        className="mt-auto w-full bg-gradient-to-r from-medical-600 to-medical-500 hover:from-medical-700 hover:to-medical-600 disabled:from-slate-300 disabled:to-slate-300 dark:disabled:from-slate-600 dark:disabled:to-slate-600 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl shadow-md transition-all flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <span className="spinner inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
            {t("analyzing")}
          </>
        ) : (
          t("analyzeButton")
        )}
      </button>
    </div>
  );
}

export { RISK_COLORS };
