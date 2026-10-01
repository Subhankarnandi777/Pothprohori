import { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { chatApi, type ChallanResponse } from '../utils/api';

const violations = [
  { value: 'no_helmet', label: 'Driving Without Helmet' },
  { value: 'overspeeding', label: 'Overspeeding' },
  { value: 'no_dl', label: 'Driving Without License' },
  { value: 'drunk_driving', label: 'Drunken Driving (DUI)' },
  { value: 'use_of_phone', label: 'Use of Mobile Phone while Driving' },
];

const states = [
  { value: 'National', label: 'National (Central Rules)' },
  { value: 'Delhi', label: 'Delhi' },
  { value: 'Maharashtra', label: 'Maharashtra' },
  { value: 'Karnataka', label: 'Karnataka' },
  { value: 'West Bengal', label: 'West Bengal' },
];

export default function Calculator() {
  const { t } = useLanguage();

  const vehicleTypes = [
    { value: '2W', label: t.twoWheeler, icon: 'two_wheeler' },
    { value: '3W', label: t.threeWheeler, icon: 'electric_rickshaw' },
    { value: '4W', label: t.fourWheeler, icon: 'directions_car' },
    { value: 'HV', label: t.heavyVehicle, icon: 'local_shipping' },
  ];
  const [vehicleType, setVehicleType] = useState('2W');
  const [violation, setViolation] = useState('no_helmet');
  const [stateName, setStateName] = useState('National');
  const [repeat, setRepeat] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<ChallanResponse | null>(null);

  const handleCalculate = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await chatApi.calculateChallan({ vehicle_type: vehicleType, violation, state: stateName, repeat });
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to calculate challan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-8 animate-fade-in-up">
      <div className="mb-7">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">{t.calcTitle}</h1>
        <p className="text-on-surface-variant text-sm mt-1.5">{t.calcSubtitle}</p>
      </div>

      <div className="bento-card p-6 sm:p-8 space-y-7">
        {/* Vehicle Type */}
        <div>
          <label className="block text-sm font-semibold text-on-surface mb-3">{t.vehicleType}</label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {vehicleTypes.map(v => (
              <button
                key={v.value}
                type="button"
                onClick={() => setVehicleType(v.value)}
                className={`flex flex-col items-center gap-1.5 p-3.5 rounded-xl border-2 text-sm font-semibold transition-all ${
                  vehicleType === v.value
                    ? 'border-secondary bg-secondary/10 text-secondary'
                    : 'border-outline-variant bg-surface text-on-surface-variant hover:border-secondary/40 hover:bg-surface-container-low'
                }`}
              >
                <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>{v.icon}</span>
                {v.label}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          {/* Violation */}
          <div>
            <label className="block text-sm font-semibold text-on-surface mb-1.5">{t.violationType}</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-outline text-sm">warning</span>
              <select
                value={violation}
                onChange={e => setViolation(e.target.value)}
                className="focus-ring w-full pl-10 pr-4 py-3 bg-white border border-outline-variant rounded-xl text-sm text-on-surface appearance-none transition-all"
              >
                {violations.map(v => (
                  <option key={v.value} value={v.value}>{v.label}</option>
                ))}
              </select>
              <span className="material-symbols-outlined absolute right-3.5 top-1/2 -translate-y-1/2 text-outline text-sm pointer-events-none">expand_more</span>
            </div>
          </div>

          {/* State */}
          <div>
            <label className="block text-sm font-semibold text-on-surface mb-1.5">{t.stateRegion}</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-outline text-sm">location_on</span>
              <select
                value={stateName}
                onChange={e => setStateName(e.target.value)}
                className="focus-ring w-full pl-10 pr-4 py-3 bg-white border border-outline-variant rounded-xl text-sm text-on-surface appearance-none transition-all"
              >
                {states.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
              <span className="material-symbols-outlined absolute right-3.5 top-1/2 -translate-y-1/2 text-outline text-sm pointer-events-none">expand_more</span>
            </div>
          </div>
        </div>

        {/* Repeat offence toggle */}
        <div>
          <button
            type="button"
            onClick={() => setRepeat(v => !v)}
            className={`flex items-center gap-3 w-full p-4 rounded-xl border-2 transition-all ${
              repeat ? 'border-amber-400 bg-amber-50 text-amber-700' : 'border-outline-variant bg-surface text-on-surface-variant hover:border-outline'
            }`}
          >
            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${repeat ? 'bg-amber-500 border-amber-500' : 'border-outline-variant'}`}>
              {repeat && <span className="material-symbols-outlined text-white text-xs">check</span>}
            </div>
            <div className="text-left">
              <p className="font-semibold text-sm">{t.repeatOffense}</p>
              <p className="text-xs opacity-70 mt-0.5">{t.repeatDesc}</p>
            </div>
            {repeat && <span className="ml-auto text-xs font-bold uppercase tracking-wide bg-amber-200 text-amber-800 px-2 py-0.5 rounded-full">{t.active}</span>}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm flex items-start gap-2">
            <span className="material-symbols-outlined text-sm mt-0.5">error</span>
            {error}
          </div>
        )}

        {/* Calculate button */}
        <button
          onClick={handleCalculate}
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-2 py-3.5 bg-secondary text-white rounded-xl font-bold text-sm hover:bg-secondary/90 transition-colors shadow-md disabled:opacity-60"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Calculating...
            </>
          ) : (
            <>
              <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>calculate</span>
              Calculate Fine
            </>
          )}
        </button>
      </div>

      {/* ── Result Card ── */}
      {result && (
        <div className="mt-6 bento-card p-6 sm:p-8 animate-fade-in-up border-l-4 border-amber-400">
          <div className="flex items-center gap-2 mb-5">
            <span className="material-symbols-outlined text-amber-500" style={{ fontVariationSettings: "'FILL' 1" }}>receipt_long</span>
            <h2 className="font-bold text-on-surface text-lg">{t.challanEstimate}</h2>
          </div>

          <div className="flex items-baseline gap-2 mb-6">
            <span className="text-5xl font-extrabold text-primary">₹{result.fine_inr.toLocaleString()}</span>
            {repeat && <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-bold rounded-full">{t.repeatOffense}</span>}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
            {[
              { label: t.violation, value: result.violation, icon: 'warning' },
              { label: t.legalSection, value: result.section, icon: 'gavel' },
              { label: t.region, value: result.state, icon: 'location_on' },
            ].map(item => (
              <div key={item.label} className="p-3.5 bg-surface-container-low rounded-xl">
                <div className="flex items-center gap-1.5 text-on-surface-variant text-xs mb-1.5">
                  <span className="material-symbols-outlined text-xs">{item.icon}</span>
                  {item.label}
                </div>
                <p className="font-semibold text-sm text-on-surface">{item.value}</p>
              </div>
            ))}
          </div>

          {result.explanation && (
            <div className="p-4 bg-blue-50 border border-blue-100 rounded-xl">
              <p className="text-xs font-semibold text-secondary mb-1 uppercase tracking-wide">{t.legalExplanation}</p>
              <p className="text-sm text-on-surface leading-relaxed">{result.explanation}</p>
            </div>
          )}

          <p className="text-xs text-on-surface-variant mt-4 flex items-center gap-1.5">
            <span className="material-symbols-outlined text-xs">info</span>
            This is an estimate. Actual fine may vary. Consult official sources.
          </p>
        </div>
      )}
    </div>
  );
}


