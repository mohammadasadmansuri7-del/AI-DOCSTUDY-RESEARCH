import React, { useRef } from 'react';
import { BookOpen, Upload, FileText, Trash2, CheckSquare, Square, AlertCircle, RefreshCw } from 'lucide-react';
import { DocumentItem } from '../types';

interface SidebarProps {
  documents: DocumentItem[];
  selectedDocIds: string[];
  onToggleDocSelect: (id: string) => void;
  onSelectAllDocs: (select: boolean) => void;
  onUploadFile: (file: File) => void;
  onDeleteDoc: (id: string) => void;
  isUploading: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  documents,
  selectedDocIds,
  onToggleDocSelect,
  onSelectAllDocs,
  onUploadFile,
  onDeleteDoc,
  isUploading,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUploadFile(e.target.files[0]);
    }
  };

  const formatSize = (bytes: number) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const allSelected = documents.length > 0 && selectedDocIds.length === documents.length;

  return (
    <aside className="sidebar">
      <div className="brand-header">
        <div className="brand-icon">
          <BookOpen size={20} />
        </div>
        <div>
          <div className="brand-title">AI DocStudy</div>
          <div className="brand-subtitle">& Research Platform</div>
        </div>
      </div>

      <div className="section-title">Upload Document</div>
      
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        accept=".pdf,.docx,.doc,.pptx,.ppt,.txt,.md,.markdown"
      />

      <div
        className="upload-card"
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload className="upload-icon" size={24} />
        <div className="upload-text">
          {isUploading ? 'Uploading & Processing...' : 'Click to Upload Document'}
        </div>
        <div className="upload-subtext">PDF, DOCX, PPTX, TXT, MD (Max 200MB)</div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <div className="section-title" style={{ margin: 0 }}>
          Your Documents ({documents.length})
        </div>
        {documents.length > 0 && (
          <button
            onClick={() => onSelectAllDocs(!allSelected)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--primary-blue)',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.2rem'
            }}
          >
            {allSelected ? <CheckSquare size={14} /> : <Square size={14} />}
            {allSelected ? 'Deselect All' : 'Select All'}
          </button>
        )}
      </div>

      <div className="doc-list">
        {documents.length === 0 ? (
          <div style={{ fontSize: '0.825rem', color: 'var(--text-muted)', textAlign: 'center', padding: '1.5rem 0' }}>
            No documents uploaded yet. Upload a document to start research or study notes.
          </div>
        ) : (
          documents.map((doc) => {
            const isSelected = selectedDocIds.includes(doc.id);
            return (
              <div
                key={doc.id}
                className={`doc-card ${isSelected ? 'selected' : ''}`}
              >
                <input
                  type="checkbox"
                  className="doc-checkbox"
                  checked={isSelected}
                  onChange={() => onToggleDocSelect(doc.id)}
                />
                <div className="doc-info">
                  <div className="doc-name" title={doc.filename}>
                    {doc.filename}
                  </div>
                  <div className="doc-meta">
                    <span>{formatSize(doc.file_size_bytes)}</span>
                    {doc.status === 'indexed' && (
                      <>
                        <span>•</span>
                        <span>{doc.page_count} {doc.page_count === 1 ? 'page' : 'pages'}</span>
                      </>
                    )}
                  </div>
                  <div style={{ marginTop: '0.35rem' }}>
                    {doc.status === 'indexed' && (
                      <span className="status-badge status-indexed">
                        Indexed ({doc.chunk_count} chunks)
                      </span>
                    )}
                    {doc.status === 'processing' && (
                      <span className="status-badge status-processing">
                        Processing...
                      </span>
                    )}
                    {doc.status === 'error' && (
                      <span className="status-badge status-error" title={doc.error_message}>
                        Error
                      </span>
                    )}
                  </div>
                </div>
                <button
                  className="btn-delete"
                  onClick={() => onDeleteDoc(doc.id)}
                  title="Delete Document"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
};
