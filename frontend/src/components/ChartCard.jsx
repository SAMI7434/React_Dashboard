const ChartCard = ({ title, children, subtitle }) => {
  return (
    <div className="glass-panel rounded-2xl p-5">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold">{title}</h3>
          {subtitle ? <p className="text-sm text-slate-400">{subtitle}</p> : null}
        </div>
      </div>
      <div className="mt-4 h-72">{children}</div>
    </div>
  )
}

export default ChartCard
