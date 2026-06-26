import React from "react";
import { RISK_COLORS } from "./PatientForm.jsx";
import { useLanguage } from "../context/LanguageContext.jsx";

const CLASS_LABEL_KEYS = {
  No_DR: "classNoDR",
  Mild: "classMild",
  Moderate: "classModerate",
  Severe: "classSevere",
  Proliferative_DR: "classProliferative",
};

const RISK_LABEL_KEYS = {
  Low: "riskLow",
  Medium: "riskMedium",
  High: "riskHigh",
  Critical: "riskCritical",
};

function EmptyState({ t }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center py-16">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-16 h-16 text-slate-300 dark:text-slate-600 mb-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.2}
          d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
        />
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.2}
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
        />
      </svg>
      <p className="text-slate-400 dark:text-slate-500 font-medium">{t("noResultYet")}</p>
      <p className="text-slate-400 dark:text-slate-500 text-sm mt-1">{t("noResultDesc")}</p>
    </div>
  );
}

function LoadingState({ t }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center py-16">
      <span className="spinner inline-block w-10 h-10 border-4 border-medical-500 border-t-transparent rounded-full mb-4"></span>
      <p className="text-slate-500 dark:text-slate-400 font-medium">{t("runningInference")}</p>
      <p className="text-slate-400 dark:text-slate-500 text-sm mt-1">{t("inferenceWait")}</p>
    </div>
  );
}

function ProbabilityBars({ probabilities, t }) {
  if (!probabilities) return null;
  const entries = Object.entries(probabilities);
  return (
    <div className="space-y-2">
      {entries.map(([label, value]) => (
        <div key={label}>
          <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
            <span>{t(CLASS_LABEL_KEYS[label]) || label}</span>
            <span>{value}%</span>
          </div>
          <div className="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-medical-500 to-medical-600 h-2 rounded-full transition-all"
              style={{ width: `${Math.min(value, 100)}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function ResultPanel({ result, loading }) {
  const { t } = useLanguage();

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-card p-6 h-full flex flex-col transition-colors">
      <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2 mb-4">
        <span className="w-2 h-2 rounded-full bg-medical-500"></span>
        {t("predictionResult")}
      </h2>

      {loading ? (
        <LoadingState t={t} />
      ) : !result ? (
        <EmptyState t={t} />
      ) : (
        <div className="flex flex-col gap-5 flex-1">
          {/* Top summary cards */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gradient-to-br from-medical-50 to-medical-100 dark:from-medical-900/40 dark:to-medical-900/20 rounded-xl p-4 border border-medical-100 dark:border-medical-800">
              <p className="text-xs text-medical-700 dark:text-medical-300 font-medium uppercase tracking-wide">
                {t("diseaseClass")}
              </p>
              <p className="text-2xl font-bold text-medical-900 dark:text-medical-100 mt-1">
                {t(CLASS_LABEL_KEYS[result.prediction]) || result.prediction}
              </p>
            </div>
            <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700 dark:to-slate-700/60 rounded-xl p-4 border border-slate-200 dark:border-slate-600">
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium uppercase tracking-wide">
                {t("confidence")}
              </p>
              <p className="text-2xl font-bold text-slate-800 dark:text-slate-100 mt-1">
                {result.confidence}%
              </p>
            </div>
          </div>

          {/* Risk badge */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-500 dark:text-slate-400 font-medium">
              {t("riskLevel")}
            </span>
            <span
              className={`px-3 py-1 rounded-full text-sm font-semibold border ${
                RISK_COLORS[result.risk] || "bg-slate-100 text-slate-700 border-slate-300"
              }`}
            >
              {t(RISK_LABEL_KEYS[result.risk]) || result.risk}
            </span>
          </div>

          {/* Class probability breakdown */}
          <div>
            <p className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-2 uppercase tracking-wide">
              {t("classProbabilities")}
            </p>
            <ProbabilityBars probabilities={result.class_probabilities} t={t} />
          </div>

          {/* Recommendation */}
          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4">
            <p className="text-xs font-semibold text-amber-700 dark:text-amber-400 uppercase tracking-wide mb-1">
              {t("recommendedAction")}
            </p>
            <p className="text-sm text-amber-800 dark:text-amber-200">{result.recommendation}</p>
          </div>

          {/* Medical explanation */}
          <div className="bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-xl p-4 flex-1">
            <p className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wide mb-1">
              {t("medicalExplanation")}
            </p>
            <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
              {result.medical_explanation}
            </p>
          </div>

          {/* Safety note */}
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
            <p className="text-xs font-semibold text-red-700 dark:text-red-400 uppercase tracking-wide mb-1">
              {t("safetyNote")}
            </p>
            <p className="text-sm text-red-800 dark:text-red-200">{result.safety_note}</p>
          </div>
        </div>
      )}
    </div>
  );
}
