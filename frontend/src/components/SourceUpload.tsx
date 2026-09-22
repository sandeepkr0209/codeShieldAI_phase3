import { useRef, useState } from "react";
import { UploadCloud, FileArchive } from "lucide-react";
import { cn } from "../lib/utils";

interface SourceUploadProps {
  onUpload: (file: File) => void;
  uploading: boolean;
}

export function SourceUpload({ onUpload, uploading }: SourceUploadProps) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFiles(files: FileList | null) {
    const file = files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".zip")) return;
    onUpload(file);
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
      className={cn(
        "rounded-xl border-2 border-dashed p-8 text-center cursor-pointer transition-colors",
        dragOver ? "border-primary bg-primary/5" : "border-border hover:border-slate-600"
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".zip"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      {uploading ? (
        <>
          <FileArchive className="h-8 w-8 text-primary mx-auto mb-3 animate-pulse" />
          <p className="text-sm text-slate-300">Uploading and extracting…</p>
        </>
      ) : (
        <>
          <UploadCloud className="h-8 w-8 text-slate-500 mx-auto mb-3" />
          <p className="text-sm text-slate-300">Drag & drop a ZIP file here, or click to browse</p>
          <p className="text-xs text-slate-600 mt-1">.zip only, up to 100MB</p>
        </>
      )}
    </div>
  );
}
