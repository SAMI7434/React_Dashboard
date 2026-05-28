const DataTable = ({ columns, rows, emptyState }) => {
  return (
    <div className="glass-panel rounded-2xl overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-900/60 text-slate-300">
          <tr>
            {columns.map((column) => (
              <th key={column.key} className="text-left px-4 py-3 font-medium">
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-6 text-slate-400">
                {emptyState || 'No rows to display'}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={row.id} className="border-t border-slate-800/70">
                {columns.map((column) => (
                  <td key={column.key} className="px-4 py-3">
                    {column.render ? column.render(row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

export default DataTable
