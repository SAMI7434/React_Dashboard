const StatCard = ({ label, value, accent }) => {
  return (
    <div className="glass-panel rounded-2xl px-5 py-4">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
      <p className={`text-2xl font-semibold mt-2 ${accent || 'text-white'}`}>{value}</p>
    </div>
  )
}

export default StatCard
