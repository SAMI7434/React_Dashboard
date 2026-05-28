import DataTable from '../components/DataTable.jsx'
import Badge from '../components/Badge.jsx'
import { useIssues } from '../hooks/useIssues.js'

const IssuesPage = () => {
  const { issues, isLoading, error } = useIssues()

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Validation issues</h2>
        <p className="text-slate-400">Review data quality warnings and errors.</p>
      </div>

      {isLoading ? <p className="text-slate-400">Loading issues...</p> : null}
      {error ? <p className="text-rose-300">{error}</p> : null}

      <DataTable
        columns={[
          { key: 'severity', label: 'Severity', render: (row) => <Badge variant={row.severity}>{row.severity}</Badge> },
          { key: 'message', label: 'Message' },
          { key: 'created_at', label: 'Detected' }
        ]}
        rows={issues}
        emptyState="No issues detected"
      />
    </div>
  )
}

export default IssuesPage
