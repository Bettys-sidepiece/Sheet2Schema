"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud } from "lucide-react";
import axios from "axios";

export default function FileUpload() {

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);


  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    // TODO: Send to backend /api/upload
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const formData = new FormData();
      formData.append("file", acceptedFiles[0]);

      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/upload`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      )
      console.log("File uploaded successfully:", res.data);
      setSuccess(true);
    } catch (err: any) {
      console.error("Upload error:", err);
      setError("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/json": [".json"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ],
    },
  });

  return (
    <div
      {...getRootProps()}
      className="cursor-pointer border-2 border-dashed border-gray-300 rounded-2xl bg-white p-12 text-center hover:border-indigo-500 transition"
    >
      <input {...getInputProps()} />
      <UploadCloud className="mx-auto h-10 w-10 text-gray-400" />
      {isDragActive ? (
        <p className="mt-4 text-indigo-600 font-medium">Drop your file here…</p>
      ) : (
        <p className="mt-4 text-gray-600">
          Drag & drop a file here, or{" "}
          <span className="text-indigo-600 font-medium">click to upload</span>
        </p>
      )}
      <p className="mt-2 text-xs text-gray-400">
        Supported formats: CSV, Excel (.xlsx), JSON
      </p>

      {loading && <p className="mt-4 text-blue-600">Uploading...</p>}
      {error && <p className="mt-4 text-red-600">{error}</p>}
      {success && <p className="mt-4 text-green-600">Upload successful!</p>}
    </div>
  );
}
