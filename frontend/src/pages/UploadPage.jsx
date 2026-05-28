import { useState } from 'react'
import UploadDropzone from '../components/UploadDropzone.jsx'
import { uploadCsv } from '../api/ingest.js'
import DataTable from '../components/DataTable.jsx'
import Badge from '../components/Badge.jsx'

const UploadPage = () => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadResult, setUploadResult] = useState(null)
  const [error, setError] = useState(null)
  const [isUploading, setIsUploading] = useState(false)

  const handleFileSelected = (file) => {
    setSelectedFile(file)
    setUploadResult(null)
    setError(null)
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      return
    }
    setIsUploading(true)
    setError(null)
    try {
      const result = await uploadCsv(selectedFile)
      setUploadResult(result)
    } catch (err) {
      setError('Upload failed. Please check the CSV format.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Upload utility export</h2>
        <p className="text-slate-400">
          Drag and drop a utility CSV export. We will normalize dates, units, and cost fields.
        </p>
      </div>
      <UploadDropzone onFileSelected={handleFileSelected} />

      {selectedFile ? (
        <div className="glass-panel rounded-2xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <p className="text-sm text-slate-400">Selected file</p>
            <p className="font-medium">{selectedFile.name}</p>
          </div>
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className="px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-100 hover:bg-cyan-500/30"
          >
            {isUploading ? 'Uploading...' : 'Start ingestion'}
          </button>
        </div>
      ) : null}

      {error ? <p className="text-rose-300">{error}</p> : null}

      {uploadResult ? (
        <div className="glass-panel rounded-2xl p-5">
          <h3 className="text-lg font-semibold">Ingestion summary</h3>
          <p className="text-slate-400 text-sm mt-1">
            Batch {uploadResult.batch?.id} · {uploadResult.records_created} rows processed
          </p>
          <div className="grid md:grid-cols-3 gap-4 mt-4">
            <div>
              <p className="text-xs text-slate-400">Failed records</p>
              <p className="text-xl font-semibold text-rose-300">{uploadResult.failed_records}</p>
            </div>
            <div>
              <p className="text-xs text-slate-400">Suspicious records</p>
              <p className="text-xl font-semibold text-amber-300">{uploadResult.suspicious_records}</p>
            </div>
            <div>
              <p className="text-xs text-slate-400">Status</p>
              <p className="text-xl font-semibold text-cyan-200">{uploadResult.batch?.status}</p>
            </div>
          </div>
        </div>
      ) : null}

      {uploadResult?.failed_rows?.length ? (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-rose-200">Failed records (with row data)</h3>
          <DataTable
            columns={[
              { key: 'row_number', label: 'Row', render: (row) => row.raw_record?.row_number },
              { key: 'meter_id', label: 'Meter' },
              { key: 'facility_name', label: 'Facility' },
              { key: 'original_energy_value', label: 'Energy' },
              { key: 'original_energy_unit', label: 'Unit' },
              { key: 'original_cost_value', label: 'Cost' },
              { key: 'original_cost_unit', label: 'Cost unit' },
              {
                key: 'issues',
                label: 'Issues',
                render: (row) =>
                  row.issues?.map((issue) => issue.message).join(' | ') || '—'
              }
            ]}
            rows={uploadResult.failed_rows}
            emptyState="No failed rows"
          />
        </div>
      ) : null}

      {uploadResult?.suspicious_rows?.length ? (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-amber-200">Suspicious records (with row data)</h3>
          <DataTable
            columns={[
              { key: 'row_number', label: 'Row', render: (row) => row.raw_record?.row_number },
              { key: 'meter_id', label: 'Meter' },
              { key: 'facility_name', label: 'Facility' },
              { key: 'normalized_mwh', label: 'MWh' },
              { key: 'normalized_thousand_dollars', label: 'Cost (k$)' },
              {
                key: 'issues',
                label: 'Flags',
                render: (row) => (
                  <div className="flex flex-wrap gap-2">
                    {row.issues?.map((issue) => (
                      <Badge key={issue.id} variant={issue.severity}>
                        {issue.message}
                      </Badge>
                    ))}
                  </div>
                )
              }
            ]}
            rows={uploadResult.suspicious_rows}
            emptyState="No suspicious rows"
          />
        </div>
      ) : null}
    </div>
  )
}

export default UploadPage
