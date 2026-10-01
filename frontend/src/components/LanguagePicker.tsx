import { useState, useRef, useEffect } from "react";
import { LANGUAGES, useLanguage } from "../context/LanguageContext";

export default function LanguagePicker() {
  const { language, setLanguage, currentLang, t } = useLanguage();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        title={t.responseLanguage}
        className="flex items-center gap-2 px-3 py-2 rounded-xl border border-outline-variant bg-surface-container-low hover:bg-secondary/10 hover:border-secondary/40 text-sm font-bold text-on-surface transition-all shadow-sm"
      >
        <span className="material-symbols-outlined text-secondary text-base" style={{ fontVariationSettings: "'FILL' 1" }}>translate</span>
        <span className="hidden sm:inline text-secondary">{currentLang.nativeLabel}</span>
        <span className="text-xs font-black text-on-surface-variant sm:hidden">{currentLang.flag}</span>
        <span
          className="material-symbols-outlined text-xs text-outline"
          style={{ transition: "transform 0.2s", transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
        >expand_more</span>
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-52 bg-white rounded-2xl shadow-2xl border border-outline-variant/60 z-50 overflow-hidden">
          <div className="px-4 py-2.5 border-b border-outline-variant/40 bg-surface-container-lowest">
            <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant flex items-center gap-1.5">
              <span className="material-symbols-outlined text-xs text-secondary">translate</span>
              {t.responseLanguage}
            </p>
          </div>
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => { setLanguage(lang.code); setOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors ${
                language === lang.code
                  ? "bg-secondary/10 text-secondary"
                  : "hover:bg-surface-container-low text-on-surface"
              }`}
            >
              <span className="w-8 h-8 rounded-xl flex items-center justify-center text-xs font-black bg-surface-container border border-outline-variant/40 text-on-surface">
                {lang.flag}
              </span>
              <div className="text-left flex-1">
                <p className="font-bold leading-tight">{lang.nativeLabel}</p>
                <p className="text-[11px] text-on-surface-variant">{lang.label}</p>
              </div>
              {language === lang.code && (
                <span className="material-symbols-outlined text-secondary text-sm">check_circle</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
