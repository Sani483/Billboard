import React, { useState, useRef, useEffect } from "react";
import {
  Camera,
  Upload,
  Loader2,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";

const API_URL = "http://localhost:8000/api";

const Detect = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  // Camera Refs
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [showCamera, setShowCamera] = useState(false);

  // Stop camera on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  // File Upload Handling
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const triggerUpload = () =>
    fileInputRef.current && fileInputRef.current.click();

  // Open Camera
  const openCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
      });
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setShowCamera(true);
    } catch (err) {
      alert("Camera permission denied or not available.");
    }
  };

  // Close Camera
  const closeCamera = () => {
    setShowCamera(false);
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  };

  // Capture Photo
  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) return;

      const file = new File([blob], `capture-${Date.now()}.png`, {
        type: "image/png",
      });

      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(blob));
      closeCamera();
    });
  };

  // Analyze Image
  const handleAnalysis = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedImage);

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text);
      }

      const data = await response.json();

      setResult({
        isToxic: !data.analysis.is_compliant,
        detectedText: data.analysis.extracted_text,
        violations_found: data.analysis.violations_found || [],
        violation_count: data.analysis.violation_count || 0,
        reportId: data.report_id,
        complianceStatus: data.analysis.is_compliant
          ? "Compliant"
          : "Unauthorized",
      });
    } catch (err) {
      setError("Error analyzing image: " + err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-6 pb-20">
      <h2 className="text-2xl font-bold">Smart Detection</h2>

      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept="image/*"
      />

      {/* Preview Box */}
      <div className="w-full h-64 bg-gray-200 rounded-xl border-2 border-dashed flex items-center justify-center relative overflow-hidden">
        {previewUrl ? (
          <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
        ) : (
          <div className="text-gray-400 flex flex-col items-center">
            <Camera className="w-16 h-16 opacity-50" />
            No Image Selected
          </div>
        )}

        {showCamera && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
            <video ref={videoRef} className="w-full h-full object-cover" playsInline />
            <div className="absolute bottom-6 flex gap-4">
              <button className="bg-white px-4 py-2 rounded" onClick={capturePhoto}>
                Capture
              </button>
              <button className="bg-gray-300 px-4 py-2 rounded" onClick={closeCamera}>
                Close
              </button>
            </div>
            <canvas ref={canvasRef} className="hidden" />
          </div>
        )}
      </div>

      {/* Buttons */}
      <div className="flex w-full gap-4">
        {!previewUrl ? (
          <>
            <button
              onClick={openCamera}
              className="flex-1 bg-blue-700 text-white py-3 rounded-xl"
            >
              <Camera className="inline-block w-5 h-5 mr-2" /> Capture
            </button>

            <button
              onClick={triggerUpload}
              className="flex-1 bg-white text-blue-700 border border-blue-700 py-3 rounded-xl"
            >
              <Upload className="inline-block w-5 h-5 mr-2" /> Upload
            </button>
          </>
        ) : (
          <button
            onClick={handleAnalysis}
            disabled={isAnalyzing}
            className="w-full bg-green-700 text-white py-3 rounded-xl"
          >
            {isAnalyzing ? (
              <Loader2 className="w-5 h-5 animate-spin inline-block" />
            ) : (
              <Upload className="w-5 h-5 inline-block" />
            )}
            {isAnalyzing ? "Analyzing..." : "Analyze"}
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="w-full bg-red-100 border border-red-600 p-4 rounded-lg">
          <AlertTriangle className="inline-block w-5 h-5 text-red-600 mr-2" />
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="w-full bg-white p-6 rounded-xl shadow-md border">
          <h3 className="font-bold mb-3">Analysis Results</h3>

          <div
            className={`p-4 rounded-lg border ${
              result.isToxic
                ? "bg-red-50 border-red-300"
                : "bg-green-50 border-green-300"
            }`}
          >
            <span
              className={`font-bold ${
                result.isToxic ? "text-red-700" : "text-green-700"
              }`}
            >
              {result.complianceStatus}
            </span>
            <p className="text-sm">
              {result.isToxic
                ? `${result.violation_count} violations found`
                : "No violations detected"}
            </p>
          </div>

          {result.detectedText && (
            <div className="mt-4 p-4 bg-gray-50 border rounded">
              <p className="font-semibold text-sm">Extracted Text</p>
              <p className="text-gray-700">{result.detectedText}</p>
            </div>
          )}

          {result.violation_count > 0 && (
            <div className="mt-3 p-4 bg-red-50 border rounded">
              <p className="font-semibold text-sm text-red-700">Violations Found</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {result.violations_found.map((v, i) => (
                  <span key={i} className="bg-red-200 text-red-900 px-3 py-1 rounded-full text-xs">
                    {v}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Detect;