import { useRef } from 'react'

const UploadDropzone = ({ onFileSelected }) => {
  const inputRef = useRef(null)

  const handleDrop = (event) => {
    event.preventDefault()
    const file = event.dataTransfer.files?.[0]
    if (file) {
      onFileSelected(file)
    }
  }

  const handleFileChange = (event) => {
    const file = event.target.files?.[0]
    if (file) {
      onFileSelected(file)
    }
  }

  return (
    <div
      className="glass-panel rounded-2xl border border-dashed border-slate-600/70 p-8 text-center"
      onDragOver={(event) => event.preventDefault()}
      onDrop={handleDrop}
    >
      <p className="text-lg font-semibold">Drop your utility CSV here</p>
      <p className="text-sm text-slate-400 mt-2">
        We will parse, normalize, and flag suspicious rows before review.
      </p>
      <button
        className="mt-5 px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-200 hover:bg-cyan-500/30"
        onClick={() => inputRef.current?.click()}
      >
        Browse file
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        className="hidden"
      />
    </div>
  )
}

export default UploadDropzone
