const Badge = ({ variant, children }) => {
  const styles = {
    pending: 'bg-amber-500/20 text-amber-200',
    approved: 'bg-emerald-500/20 text-emerald-200',
    rejected: 'bg-rose-500/20 text-rose-200',
    warning: 'bg-orange-500/20 text-orange-200',
    error: 'bg-rose-500/20 text-rose-200'
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs ${styles[variant] || 'bg-slate-500/20 text-slate-200'}`}>
      {children}
    </span>
  )
}

export default Badge
