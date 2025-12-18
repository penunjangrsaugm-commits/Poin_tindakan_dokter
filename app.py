
import React, { useState, useEffect, useRef } from 'react';
import { extractMedicalParams } from './geminiService';
import { calculateScores } from './calculatorLogic';
import { ExtractedParams, CalculationResult, JenisTindakan, JumlahDokter, JenisAnestesi, PerawatanPasca, KategoriKesetaraan } from './types';
import { 
  ClipboardList, 
  Calculator, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCcw, 
  ChevronRight, 
  Stethoscope, 
  Mic, 
  MicOff, 
  History,
  Info
} from 'lucide-react';

const SAMPLES = [
  {
    title: "Bedah Appendectomy",
    text: "Pasien menjalani operasi Appendectomy selama 90 menit oleh 1 dokter bedah. Menggunakan bius umum. Pasca operasi pasien dibawa ke PACU untuk observasi. Kategori besar."
  },
  {
    title: "Tindakan Endoskopi",
    text: "Tindakan endoskopi diagnostik dilakukan selama 45 menit. Invasif non bedah. Menggunakan bius lokal (sedasi ringan). Pasien rawat jalan tanpa pengawasan khusus. Kategori sedang."
  },
  {
    title: "Konsultasi Spesialis",
    text: "Konsultasi spesialis di poliklinik rawat jalan. Tidak ada tindakan invasif. Durasi 20 menit. Tidak perlu pengawasan pasca. Kategori biasa."
  }
];

const App: React.FC = () => {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [narrative, setNarrative] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [params, setParams] = useState<ExtractedParams | null>(null);
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'id-ID';

      recognitionRef.current.onresult = (event: any) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        setNarrative(prev => prev + ' ' + finalTranscript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech recognition error", event.error);
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  }, []);

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
    } else {
      setIsRecording(true);
      recognitionRef.current?.start();
    }
  };

  const handleAnalysis = async () => {
    if (!narrative.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await extractMedicalParams(narrative);
      setParams(data);
      setStep(2);
    } catch (err) {
      console.error(err);
      setError("Gagal menganalisis narasi. Pastikan API KEY valid dan narasi cukup jelas.");
    } finally {
      setLoading(false);
    }
  };

  const handleFinalCalculation = () => {
    if (!params) return;
    const res = calculateScores(params);
    setResult(res);
    setStep(3);
  };

  const reset = () => {
    setStep(1);
    setNarrative('');
    setParams(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <header className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-600 rounded-2xl shadow-lg shadow-indigo-100">
            <Stethoscope className="text-white w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Expert Remunerasi</h1>
            <p className="text-xs text-indigo-600 font-bold uppercase tracking-widest">RSA UGM • Scoring 2021</p>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm border border-gray-100">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-all duration-500 ${step === s ? 'bg-indigo-600 text-white scale-110 shadow-md' : step > s ? 'bg-emerald-500 text-white' : 'bg-gray-100 text-gray-400'}`}>
                {step > s ? <CheckCircle2 size={16} /> : s}
              </div>
              {s < 3 && <div className={`w-10 h-1 mx-1 rounded-full transition-all duration-500 ${step > s ? 'bg-emerald-500' : 'bg-gray-100'}`} />}
            </div>
          ))}
        </div>
      </header>

      <main className="glass border border-white shadow-2xl rounded-[2.5rem] overflow-hidden">
        {step === 1 && (
          <div className="p-8 md:p-12">
            <div className="mb-8">
              <div className="flex justify-between items-end mb-3">
                <label className="block text-xl font-bold text-gray-800">Narasi Tindakan Medis</label>
                <div className="flex gap-2">
                  <button 
                    onClick={toggleRecording}
                    className={`p-2 rounded-full transition-all ${isRecording ? 'bg-red-100 text-red-600 animate-pulse' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                    title={isRecording ? "Berhenti Merekam" : "Rekam Suara"}
                  >
                    {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
                  </button>
                </div>
              </div>
              <p className="text-gray-500 text-sm mb-6 flex items-center gap-2 italic">
                <Info size={14} /> AI akan mengekstraksi parameter kualifikasi, jumlah dokter, jenis anestesi, dan durasi secara otomatis.
              </p>
              <div className="relative">
                <textarea
                  value={narrative}
                  onChange={(e) => setNarrative(e.target.value)}
                  placeholder="Ketik atau rekam narasi tindakan medis di sini..."
                  className="w-full h-56 p-6 bg-gray-50 border border-gray-200 rounded-3xl focus:ring-4 focus:ring-indigo-100 focus:border-indigo-400 outline-none transition-all resize-none text-gray-700 leading-relaxed font-medium"
                />
                {loading && (
                  <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] rounded-3xl flex flex-col items-center justify-center gap-4 animate-in fade-in duration-300">
                    <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                    <p className="text-indigo-900 font-bold animate-pulse">Menganalisis Narasi Medis...</p>
                  </div>
                )}
              </div>
            </div>

            <div className="mb-8">
              <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Atau pilih contoh:</p>
              <div className="flex flex-wrap gap-2">
                {SAMPLES.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => setNarrative(s.text)}
                    className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-semibold text-gray-600 hover:border-indigo-300 hover:text-indigo-600 transition-all flex items-center gap-2"
                  >
                    <History size={14} />
                    {s.title}
                  </button>
                ))}
              </div>
            </div>
            
            {error && (
              <div className="mb-8 p-4 bg-red-50 border border-red-100 rounded-2xl flex items-center gap-3 text-red-600 animate-in slide-in-from-bottom-2">
                <AlertCircle className="shrink-0" />
                <p className="text-sm font-semibold">{error}</p>
              </div>
            )}

            <button
              onClick={handleAnalysis}
              disabled={loading || !narrative.trim()}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 text-white font-black py-5 rounded-3xl flex items-center justify-center gap-3 transition-all transform hover:scale-[1.01] active:scale-95 shadow-xl shadow-indigo-200"
            >
              {loading ? <RefreshCcw className="animate-spin" /> : <ChevronRight />}
              Mulai Analisis Parameter
            </button>
          </div>
        )}

        {step === 2 && params && (
          <div className="p-8 md:p-12 animate-in fade-in slide-in-from-right-4 duration-500">
            <div className="flex items-center gap-3 mb-8">
              <div className="p-2 bg-emerald-100 text-emerald-600 rounded-full">
                <CheckCircle2 size={24} />
              </div>
              <div>
                <h2 className="text-2xl font-black text-gray-900">Validasi Parameter</h2>
                <p className="text-sm text-gray-500 font-medium italic mt-1">
                  "Mohon koreksi data berikut jika ada ketidaksesuaian narasi:"
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6 mb-10 bg-gray-50/50 p-6 rounded-3xl border border-gray-100">
              <InputField label="Nama Tindakan" value={params.namaTindakan} onChange={(v) => setParams({...params, namaTindakan: v})} />
              <SelectField label="Jenis Tindakan (F1)" value={params.jenisTindakan} options={Object.values(JenisTindakan)} onChange={(v) => setParams({...params, jenisTindakan: v as JenisTindakan})} />
              <SelectField label="Jumlah Dokter (F2.1)" value={params.jumlahDokter} options={Object.values(JumlahDokter)} onChange={(v) => setParams({...params, jumlahDokter: v as JumlahDokter})} />
              <SelectField label="Penunjang/Bius (F2.2)" value={params.jenisAnestesi} options={Object.values(JenisAnestesi)} onChange={(v) => setParams({...params, jenisAnestesi: v as JenisAnestesi})} />
              <SelectField label="Pengawasan (F3)" value={params.perawatanPasca} options={Object.values(PerawatanPasca)} onChange={(v) => setParams({...params, perawatanPasca: v as PerawatanPasca})} />
              <InputField label="Durasi (Menit)" value={params.durasiMenit.toString()} type="number" onChange={(v) => setParams({...params, durasiMenit: parseInt(v) || 0})} />
              <div className="md:col-span-2">
                <SelectField label="Kategori Kesetaraan (F5)" value={params.kategoriKesetaraan} options={Object.values(KategoriKesetaraan)} onChange={(v) => setParams({...params, kategoriKesetaraan: v as KategoriKesetaraan})} />
              </div>
            </div>

            {params.notes && (
              <div className="mb-10 p-5 bg-indigo-50 border border-indigo-100 rounded-2xl flex gap-3 text-indigo-900 text-sm leading-relaxed">
                <Info size={18} className="shrink-0 text-indigo-400 mt-0.5" />
                <div>
                  <span className="font-black text-indigo-600 uppercase tracking-widest text-[10px] block mb-1">Catatan Analisis AI</span>
                  {params.notes}
                </div>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-4">
              <button onClick={() => setStep(1)} className="flex-1 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 font-bold py-5 rounded-3xl transition-all">Kembali</button>
              <button onClick={handleFinalCalculation} className="flex-[2] bg-indigo-600 hover:bg-indigo-700 text-white font-black py-5 rounded-3xl flex items-center justify-center gap-3 shadow-xl shadow-indigo-100 transition-all transform hover:scale-[1.01] active:scale-95">
                <Calculator size={20} />
                Hitung Skor Akhir
              </button>
            </div>
          </div>
        )}

        {step === 3 && result && params && (
          <div className="p-8 md:p-12 animate-in fade-in zoom-in-95 duration-500">
            <div className="mb-10 text-center">
              <span className="inline-block px-4 py-1.5 bg-indigo-100 text-indigo-600 rounded-full text-[10px] font-black uppercase tracking-widest mb-4">Laporan Perhitungan</span>
              <h2 className="text-3xl font-black text-gray-900 mb-2">{params.namaTindakan}</h2>
              <div className="w-24 h-1.5 bg-indigo-600 mx-auto rounded-full" />
            </div>

            <div className="overflow-x-auto mb-10">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b-2 border-gray-100">
                    <th className="py-5 font-black text-gray-400 text-[10px] uppercase tracking-widest">Kode</th>
                    <th className="py-5 font-black text-gray-800 text-sm">Komponen Penilaian</th>
                    <th className="py-5 font-black text-gray-800 text-sm text-right">Poin</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  <ResultRow code="F1" label="Kualifikasi Tindakan" value={params.jenisTindakan} score={result.f1} />
                  <ResultRow code="F2.1" label="Kompleksitas (Dokter)" value={params.jumlahDokter} score={result.f2_1} />
                  <ResultRow code="F2.2" label="Bantuan Penunjang (Bius)" value={params.jenisAnestesi} score={result.f2_2} />
                  <ResultRow code="F3" label="Tanggung Jawab (Pasca)" value={params.perawatanPasca} score={result.f3} />
                  <ResultRow code="F4" label="Waktu Tindakan" value={`${params.durasiMenit} menit`} score={result.f4} />
                  <tr className="bg-indigo-50/50">
                    <td className="py-5 px-4 font-black text-indigo-600 text-[10px]">SUM</td>
                    <td className="py-5 text-indigo-900 font-black text-lg">JUMLAH SKOR</td>
                    <td className="py-5 text-right font-black text-indigo-600 text-2xl">{result.jumlahSkor}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
              <div className="bg-white border-2 border-gray-50 rounded-[2rem] p-8 flex flex-col justify-center">
                <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest mb-2">Faktor Pengali (F5)</p>
                <div className="flex justify-between items-end">
                  <div>
                    <p className="text-2xl font-black text-gray-900">{params.kategoriKesetaraan}</p>
                    <p className="text-sm text-indigo-600 font-bold">{params.jenisTindakan}</p>
                  </div>
                  <div className="text-5xl font-black text-indigo-900 leading-none">{result.f5}</div>
                </div>
              </div>

              <div className="bg-indigo-900 text-white rounded-[2rem] p-8 text-center shadow-2xl shadow-indigo-200 flex flex-col justify-center">
                <p className="text-indigo-300 font-black text-[10px] uppercase tracking-widest mb-4">Total Skor Kalkulasi</p>
                <div className="text-4xl font-black tracking-tight mb-2">
                  {result.totalSkor.toLocaleString()}
                </div>
                <div className="text-xs font-bold text-indigo-400">
                  {result.jumlahSkor} × {result.f5}
                </div>
              </div>
            </div>

            <div className="bg-emerald-500 text-white rounded-[2.5rem] p-10 text-center shadow-2xl shadow-emerald-200 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 opacity-10">
                <Calculator size={120} />
              </div>
              <p className="text-emerald-100 font-black text-[10px] uppercase tracking-widest mb-6 relative z-10">Skor Akhir Remunerasi (Divided by 150)</p>
              <div className="relative z-10">
                <div className="text-lg font-bold text-emerald-100 mb-2 italic">
                  {result.totalSkor} / 150 =
                </div>
                <div className="text-8xl font-black tracking-tighter leading-none">{result.skorAkhir.toFixed(4)}</div>
                <div className="mt-8 flex items-center justify-center gap-2 text-xs font-black bg-emerald-600/30 py-2 px-4 rounded-full w-fit mx-auto">
                  <CheckCircle2 size={14} />
                  SESUAI PEDOMAN RSA UGM 2021
                </div>
              </div>
            </div>

            <button
              onClick={reset}
              className="w-full mt-10 bg-gray-900 hover:bg-black text-white font-black py-5 rounded-3xl flex items-center justify-center gap-3 transition-all transform hover:scale-[1.01] active:scale-95 shadow-xl shadow-gray-200"
            >
              <RefreshCcw size={20} />
              Analisis Tindakan Baru
            </button>
          </div>
        )}
      </main>

      <footer className="mt-16 text-center text-gray-400 text-[10px] font-black uppercase tracking-[0.2em] pb-12">
        <p>&copy; 2024 RS Akademik UGM - Sistem Pakar Manajemen Remunerasi</p>
      </footer>
    </div>
  );
};

// UI Components
const InputField = ({ label, value, type = "text", onChange }: { label: string, value: string, type?: string, onChange: (v: string) => void }) => (
  <div className="space-y-2">
    <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">{label}</label>
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full p-4 bg-white border border-gray-200 rounded-2xl focus:ring-4 focus:ring-indigo-50 focus:border-indigo-400 outline-none transition-all font-bold text-gray-800"
    />
  </div>
);

const SelectField = ({ label, value, options, onChange }: { label: string, value: string, options: string[], onChange: (v: string) => void }) => (
  <div className="space-y-2">
    <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">{label}</label>
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full p-4 bg-white border border-gray-200 rounded-2xl focus:ring-4 focus:ring-indigo-50 focus:border-indigo-400 outline-none transition-all font-bold text-gray-800 cursor-pointer appearance-none"
      style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236366f1'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 1rem center', backgroundSize: '1.5em' }}
    >
      {options.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
    </select>
  </div>
);

const ResultRow = ({ code, label, value, score }: { code: string, label: string, value: string, score: number }) => (
  <tr className="hover:bg-gray-50/50 transition-colors">
    <td className="py-5 font-black text-gray-300 text-[10px]">{code}</td>
    <td className="py-5">
      <div className="text-gray-900 font-bold text-sm">{label}</div>
      <div className="text-gray-400 text-xs font-semibold">{value}</div>
    </td>
    <td className="py-5 text-right font-mono font-black text-gray-800 text-lg">{score}</td>
  </tr>
);

export default App;
