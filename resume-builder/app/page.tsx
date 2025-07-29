'use client';

import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState('');
  const [inputMethod, setInputMethod] = useState<'pdf' | 'text'>('pdf');
  const [jobDescription, setJobDescription] = useState('');
  interface AnalysisResult {
    similarity_score: number;
    resume_text: string;
    job_desc: string;
    resume_skills: string[];
    job_skills: string[];
    missing_skills: string[];
    matching_skills: string[];
    recommendations: string[];
    improved_resume: string;
    analysis: {
      total_resume_skills: number;
      total_job_skills: number;
      skill_match_percentage: number;
    };
  }

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [showImprovedResume, setShowImprovedResume] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if ((inputMethod === 'pdf' && !file) || (inputMethod === 'text' && !resumeText) || !jobDescription) return;

    setLoading(true);
    setError('');
    setResult(null);
    
    const formData = new FormData();
    if (inputMethod === 'pdf') {
      formData.append('resume', file!);
    } else {
      formData.append('resume_text', resumeText);
    }
    formData.append('job_desc', jobDescription);

    try {
      const endpoint = inputMethod === 'pdf' ? '/tailor-resume' : '/tailor-resume-text';
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze resume');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      setError(error instanceof Error ? error.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-800 dark:text-white mb-4">
            AI Resume Builder
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Upload your resume and job description to get AI-powered tailoring suggestions
          </p>
        </div>

        {/* Main Form */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Input Method Selector */}
              <div className="flex justify-center mb-6">
                <div className="bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
                  <button
                    type="button"
                    onClick={() => setInputMethod('pdf')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      inputMethod === 'pdf'
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white'
                    }`}
                  >
                    📄 Upload PDF
                  </button>
                  <button
                    type="button"
                    onClick={() => setInputMethod('text')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      inputMethod === 'text'
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white'
                    }`}
                  >
                    📝 Paste Text
                  </button>
                </div>
              </div>

              {/* Resume Input */}
              {inputMethod === 'pdf' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Upload Resume (PDF)
                  </label>
                <div className="relative">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-500 dark:text-gray-400
                             file:mr-4 file:py-3 file:px-6
                             file:rounded-lg file:border-0
                             file:text-sm file:font-medium
                             file:bg-blue-50 file:text-blue-700
                             hover:file:bg-blue-100
                             dark:file:bg-blue-900 dark:file:text-blue-300
                             border border-gray-300 dark:border-gray-600 rounded-lg
                             bg-gray-50 dark:bg-gray-700 p-3"
                  />
                </div>
                  {file && (
                    <p className="mt-2 text-sm text-green-600 dark:text-green-400">
                      ✓ {file.name} selected
                    </p>
                  )}
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Resume Text
                  </label>
                  <textarea
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                    placeholder="Paste your resume text here...

Example:
John Doe
john.doe@email.com
(555) 123-4567

Objective
Looking for a software development position

Experience
Software Developer at Tech Corp
- Worked on web applications
- Used Python and JavaScript

Skills
Python, JavaScript, HTML, CSS"
                    rows={12}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 
                             rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                             placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  {resumeText && (
                    <p className="mt-2 text-sm text-green-600 dark:text-green-400">
                      ✓ Resume text added ({resumeText.length} characters)
                    </p>
                  )}
                </div>
              )}

              {/* Job Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Job Description
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here..."
                  rows={8}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 
                           rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                           placeholder-gray-500 dark:placeholder-gray-400"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={((inputMethod === 'pdf' && !file) || (inputMethod === 'text' && !resumeText)) || !jobDescription || loading}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 
                         hover:from-blue-700 hover:to-indigo-700 
                         disabled:from-gray-400 disabled:to-gray-500
                         text-white font-medium py-4 px-6 rounded-lg 
                         transition-all duration-200 transform hover:scale-[1.02]
                         disabled:cursor-not-allowed disabled:transform-none
                         shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Analyzing Resume...
                  </div>
                ) : (
                  'Tailor My Resume'
                )}
              </button>
            </form>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 mb-8">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800 dark:text-red-300">
                    Error
                  </h3>
                  <div className="mt-2 text-sm text-red-700 dark:text-red-400">
                    {error}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
                Analysis Results
              </h2>
              
              <div className="grid md:grid-cols-3 gap-6 mb-8">
                {/* Similarity Score */}
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 
                              rounded-xl p-6 border border-green-200 dark:border-green-800">
                  <h3 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-2">
                    Similarity Score
                  </h3>
                  <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                    {(result.similarity_score * 100).toFixed(1)}%
                  </div>
                  <p className="text-sm text-green-700 dark:text-green-300 mt-2">
                    Overall match with job requirements
                  </p>
                </div>

                {/* Skill Match */}
                <div className="bg-gradient-to-r from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 
                              rounded-xl p-6 border border-purple-200 dark:border-purple-800">
                  <h3 className="text-lg font-semibold text-purple-800 dark:text-purple-300 mb-2">
                    Skill Match
                  </h3>
                  <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                    {result.analysis?.skill_match_percentage?.toFixed(0) || 0}%
                  </div>
                  <p className="text-sm text-purple-700 dark:text-purple-300 mt-2">
                    {result.matching_skills?.length || 0} of {result.job_skills?.length || 0} skills matched
                  </p>
                </div>

                {/* Skills Found */}
                <div className="bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 
                              rounded-xl p-6 border border-orange-200 dark:border-orange-800">
                  <h3 className="text-lg font-semibold text-orange-800 dark:text-orange-300 mb-2">
                    Skills Detected
                  </h3>
                  <div className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                    {result.resume_skills?.length || 0}
                  </div>
                  <p className="text-sm text-orange-700 dark:text-orange-300 mt-2">
                    Skills found in your resume
                  </p>
                </div>
              </div>

              {/* Recommendations */}
              {result.recommendations && result.recommendations.length > 0 && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 
                              rounded-xl p-6 border border-blue-200 dark:border-blue-800 mb-8">
                  <h3 className="text-lg font-semibold text-blue-800 dark:text-blue-300 mb-4">
                    Recommendations
                  </h3>
                  <div className="space-y-3">
                    {result.recommendations.map((rec: string, index: number) => (
                      <div key={index} className="flex items-start text-sm text-blue-700 dark:text-blue-300">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Skills Analysis */}
              <div className="grid md:grid-cols-2 gap-6 mb-8">
                {/* Missing Skills */}
                {result.missing_skills && result.missing_skills.length > 0 && (
                  <div className="bg-red-50 dark:bg-red-900/20 rounded-xl p-6 border border-red-200 dark:border-red-800">
                    <h3 className="text-lg font-semibold text-red-800 dark:text-red-300 mb-4">
                      Missing Skills ({result.missing_skills.length})
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {result.missing_skills.slice(0, 10).map((skill: string, index: number) => (
                        <span key={index} className="px-3 py-1 bg-red-100 dark:bg-red-800/30 text-red-800 dark:text-red-300 
                                                   text-sm rounded-full border border-red-200 dark:border-red-700">
                          {skill}
                        </span>
                      ))}
                      {result.missing_skills.length > 10 && (
                        <span className="px-3 py-1 text-red-600 dark:text-red-400 text-sm">
                          +{result.missing_skills.length - 10} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Matching Skills */}
                {result.matching_skills && result.matching_skills.length > 0 && (
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
                    <h3 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-4">
                      Matching Skills ({result.matching_skills.length})
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {result.matching_skills.slice(0, 10).map((skill: string, index: number) => (
                        <span key={index} className="px-3 py-1 bg-green-100 dark:bg-green-800/30 text-green-800 dark:text-green-300 
                                                     text-sm rounded-full border border-green-200 dark:border-green-700">
                          {skill}
                        </span>
                      ))}
                      {result.matching_skills.length > 10 && (
                        <span className="px-3 py-1 text-green-600 dark:text-green-400 text-sm">
                          +{result.matching_skills.length - 10} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Improved Resume Section */}
              {result.improved_resume && (
                <div className="mt-8">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold text-gray-800 dark:text-white">
                      ✨ AI-Enhanced Resume
                    </h3>
                    <div className="flex items-center space-x-4">
                      <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                        <button
                          onClick={() => setShowImprovedResume(false)}
                          className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                            !showImprovedResume
                              ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                              : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                          }`}
                        >
                          Original
                        </button>
                        <button
                          onClick={() => setShowImprovedResume(true)}
                          className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                            showImprovedResume
                              ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                              : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                          }`}
                        >
                          AI Enhanced
                        </button>
                      </div>
                      <button
                        onClick={() => {
                          const element = document.createElement('a');
                          const file = new Blob([result.improved_resume], { type: 'text/plain' });
                          element.href = URL.createObjectURL(file);
                          element.download = 'improved_resume.txt';
                          document.body.appendChild(element);
                          element.click();
                          document.body.removeChild(element);
                        }}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium 
                                 transition-colors flex items-center space-x-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span>Download</span>
                      </button>
                    </div>
                  </div>

                  <div className="bg-white dark:bg-gray-900 rounded-xl border-2 border-gray-200 dark:border-gray-700 overflow-hidden">
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 
                                  px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                        <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                        <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                        <span className="ml-4 text-sm font-medium text-gray-600 dark:text-gray-300">
                          {showImprovedResume ? 'AI-Enhanced Resume' : 'Original Resume'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="p-6 max-h-96 overflow-y-auto">
                      <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono leading-relaxed">
                        {showImprovedResume ? result.improved_resume : result.resume_text}
                      </pre>
                    </div>
                  </div>

                  {showImprovedResume && (
                    <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <svg className="w-5 h-5 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-1">
                            AI Enhancement Features
                          </h4>
                          <ul className="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                            <li>• Improved formatting and structure</li>
                            <li>• Job-relevant keywords integration</li>
                            <li>• Enhanced professional summary</li>
                            <li>• Optimized skills section</li>
                            <li>• Actionable improvement suggestions</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="text-center mt-16 text-gray-600 dark:text-gray-400">
          <p>Powered by AI • Built with Next.js & Tailwind CSS</p>
        </footer>
      </div>
    </div>
  );
}
