import { useState } from 'react';

const categories = ['All', 'Motor Vehicles Act', 'Traffic Rules', 'State Laws', 'Amendments'];

const laws = [
  { id: 1, title: 'Motor Vehicles Act, 1988', category: 'Motor Vehicles Act', section: 'Full Act', desc: 'The comprehensive central legislation governing all aspects of road transport and motor vehicles in India.', badge: 'Central', badgeColor: 'bg-blue-100 text-blue-700' },
  { id: 2, title: 'MV Amendment Act, 2019', category: 'Amendments', section: 'Amendment', desc: 'Significantly increased penalties for traffic violations, introduced provisions for good samaritans, and tightened road safety norms.', badge: 'Amendment', badgeColor: 'bg-purple-100 text-purple-700' },
  { id: 3, title: 'Central Motor Vehicles Rules, 1989', category: 'Traffic Rules', section: 'Rules', desc: 'Detailed rules covering licensing, registration, insurance, and traffic control signals across India.', badge: 'Rules', badgeColor: 'bg-green-100 text-green-700' },
  { id: 4, title: 'Delhi Motor Vehicles Rules', category: 'State Laws', section: 'State Rules', desc: 'State-specific rules for Delhi covering metropolitan traffic management and parking regulations.', badge: 'Delhi', badgeColor: 'bg-amber-100 text-amber-700' },
  { id: 5, title: 'Section 177 – General Offences', category: 'Motor Vehicles Act', section: 'Section 177', desc: 'Fine of ₹500 for first offence and ₹1,500 for subsequent offences for general traffic violations.', badge: 'Fine', badgeColor: 'bg-red-100 text-red-700' },
  { id: 6, title: 'Section 194D – Mobile Phone Use', category: 'Amendments', section: 'Section 194D', desc: 'Use of handheld device while driving — ₹1,000 (first) and ₹10,000 (subsequent). License suspension may apply.', badge: 'Penalty', badgeColor: 'bg-red-100 text-red-700' },
  { id: 7, title: 'Section 185 – Drunken Driving', category: 'Motor Vehicles Act', section: 'Section 185', desc: 'Driving under influence of alcohol — ₹10,000 fine or 6 months imprisonment or both for first offence.', badge: 'Criminal', badgeColor: 'bg-red-100 text-red-700' },
  { id: 8, title: 'Maharashtra Traffic Rules', category: 'State Laws', section: 'State Rules', desc: 'State-specific regulations for Maharashtra including Mumbai city traffic ordinances and highway rules.', badge: 'Maharashtra', badgeColor: 'bg-amber-100 text-amber-700' },
];

export default function Library() {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [search, setSearch] = useState('');

  const filtered = laws.filter(law => {
    const matchCat = selectedCategory === 'All' || law.category === selectedCategory;
    const matchSearch = !search || law.title.toLowerCase().includes(search.toLowerCase()) || law.desc.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8 animate-fade-in-up">
      <div className="mb-7">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">Law Library</h1>
        <p className="text-on-surface-variant text-sm mt-1.5">Browse Indian traffic laws, sections, and state-specific regulations.</p>
      </div>

      {/* Search bar */}
      <div className="relative mb-5">
        <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline">search</span>
        <input
          type="text"
          placeholder="Search laws, sections, or topics..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="focus-ring w-full pl-11 pr-4 py-3.5 bg-white border border-outline-variant rounded-2xl text-sm text-on-surface placeholder:text-outline shadow-sm transition-all"
        />
        {search && (
          <button onClick={() => setSearch('')} className="absolute right-4 top-1/2 -translate-y-1/2 text-outline hover:text-on-surface-variant">
            <span className="material-symbols-outlined text-sm">close</span>
          </button>
        )}
      </div>

      {/* Category chips */}
      <div className="flex gap-2 flex-wrap mb-6">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-colors border ${
              selectedCategory === cat
                ? 'bg-secondary text-white border-secondary shadow-sm'
                : 'bg-white text-on-surface-variant border-outline-variant hover:border-secondary/40 hover:bg-surface-container-low'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Results count */}
      <p className="text-xs text-on-surface-variant mb-4">{filtered.length} {filtered.length === 1 ? 'result' : 'results'}</p>

      {/* Law cards */}
      {filtered.length > 0 ? (
        <div className="space-y-4">
          {filtered.map(law => (
            <div key={law.id} className="bento-card p-5 sm:p-6 flex gap-4">
              <div className="shrink-0 mt-0.5">
                <div className="w-9 h-9 rounded-lg bg-secondary/10 flex items-center justify-center">
                  <span className="material-symbols-outlined text-secondary text-base" style={{ fontVariationSettings: "'FILL' 1" }}>description</span>
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2 mb-1.5">
                  <h3 className="font-bold text-on-surface text-sm">{law.title}</h3>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${law.badgeColor}`}>{law.badge}</span>
                </div>
                <p className="text-xs font-medium text-secondary mb-2">{law.section}</p>
                <p className="text-on-surface-variant text-xs leading-relaxed">{law.desc}</p>
                <button className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-secondary hover:underline">
                  Read more <span className="material-symbols-outlined text-xs">arrow_forward</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-16 text-on-surface-variant">
          <span className="material-symbols-outlined text-5xl mb-3 opacity-30">search_off</span>
          <p className="font-semibold text-sm">No results found</p>
          <p className="text-xs mt-1">Try a different search term or category.</p>
        </div>
      )}

      {/* Disclaimer */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-100 rounded-xl flex items-start gap-3">
        <span className="material-symbols-outlined text-secondary text-sm mt-0.5">info</span>
        <p className="text-xs text-on-surface-variant leading-relaxed">
          <strong className="text-on-surface">Disclaimer:</strong> This library is for educational purposes only.
          Always verify with official government sources before making legal decisions.
        </p>
      </div>
    </div>
  );
}


