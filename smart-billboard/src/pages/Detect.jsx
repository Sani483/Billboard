import React, { useState, useRef } from 'react';
import { Camera, Upload, Loader2, AlertTriangle, Ruler, CheckCircle } from 'lucide-react';

const API_URL = 'http://localhost:8000/api';

const Detect = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // Handle File Selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  // Trigger File Input Click
  const triggerUpload = () => {
    fileInputRef.current.click();
  };

  // Analyze Image with Backend
  const handleAnalysis = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);
      
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      setResult({
        isToxic: !data.analysis.is_compliant,
        status: data.analysis.status,
        detectedText: data.analysis.extracted_text,
        violations_found: data.analysis.violations_found,
        violation_count: data.analysis.violation_count,
        violation_context: data.analysis.violation_context,
        reportId: data.report_id,
        complianceStatus: !data.analysis.is_compliant ? "Unauthorized" : "Compliant"
      });
    } catch (err) {
      setError(`Error analyzing image: ${err.message}`);
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-6 pb-20">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-800">Smart Detection</h2>
        <p className="text-gray-500 text-sm px-4">
          Capture billboard images to scan for prohibited content and measure dimensions.
        </p>
      </div>

      {/* Hidden File Input */}
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        className="hidden" 
        accept="image/*"
      />

      {/* Image Preview Area */}
      <div className="w-full h-64 bg-gray-100 rounded-2xl border-2 border-dashed border-gray-300 flex flex-col items-center justify-center overflow-hidden relative">
        {previewUrl ? (
          <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
        ) : (
          <div className="text-gray-400 flex flex-col items-center">
            <Camera className="w-16 h-16 mb-2 opacity-50" />
            <span className="text-sm">No Image Selected</span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex w-full gap-4">
        {!previewUrl ? (
          <>
            <button className="flex-1 bg-blue-900 text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 shadow-lg active:scale-95 transition-transform">
              <Camera className="w-5 h-5" />
              Capture
            </button>
            <button 
              onClick={triggerUpload}
              className="flex-1 bg-white text-blue-900 border border-blue-900 py-3 rounded-xl font-semibold flex items-center justify-center gap-2 shadow-sm active:scale-95 transition-transform">
              <Upload className="w-5 h-5" />
              Upload
            </button>
          </>
        ) : (
          <button 
            onClick={handleAnalysis}
            disabled={isAnalyzing}
            className="w-full bg-green-700 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg active:scale-95 transition-transform disabled:opacity-70 disabled:cursor-not-allowed">
            {isAnalyzing ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
            {isAnalyzing ? "Analyzing Image..." : "Analyze Compliance"}
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="w-full bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-700">Error</p>
              <p className="text-sm text-red-600">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results Display */}
      {result && (
        <div className="w-full bg-white p-6 rounded-xl shadow-lg border border-gray-200 animate-in fade-in">
          <h3 className="font-bold text-lg mb-4 border-b pb-2">Analysis Results</h3>
          
          <div className="space-y-4">
            {/* Compliance Status */}
            <div className={`p-4 rounded-lg border ${result.isToxic ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
              <div className="flex items-center gap-2 mb-2">
                {result.isToxic ? (
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                ) : (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
                <span className={`font-bold ${result.isToxic ? 'text-red-700' : 'text-green-700'}`}>
                  {result.complianceStatus}
                </span>
              </div>
              <p className="text-xs text-gray-600">
                {result.isToxic 
                  ? `Found ${result.violation_count} violation(s)` 
                  : "No violations detected"}
              </p>
            </div>

            {/* Extracted Text */}
            {result.detectedText && (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-xs font-semibold text-gray-600 mb-2">Extracted Text</p>
                <p className="text-sm text-gray-700 line-clamp-3">{result.detectedText}</p>
              </div>
            )}

            {/* Violations Found */}
            {result.violation_count > 0 && (
              <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                <p className="text-xs font-semibold text-red-700 mb-2">Violations Found</p>
                <div className="flex flex-wrap gap-2">
                  {result.violations_found.map((violation, idx) => (
                    <span key={idx} className="bg-red-200 text-red-800 px-3 py-1 rounded-full text-xs font-semibold">
                      {violation}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Detect;