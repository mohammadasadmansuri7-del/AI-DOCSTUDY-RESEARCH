import React, { useState, useEffect } from 'react';
import { Search, BookOpen, Clock } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { DocumentResearchView } from './components/DocumentResearchView';
import { AINotesView } from './components/AINotesView';
import { HistoryDrawer } from './components/HistoryDrawer';
import {
  DocumentItem,
  SingleQuestionAnswer,
  StudyNote,
  HistoryData,
  ResearchHistoryItem,
  NotesHistoryItem
} from './types';

type Mode = 'research' | 'ai_notes';

export const App: React.FC = () => {
  const [currentMode, setCurrentMode] = useState<Mode>('research');
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  // History state
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [history, setHistory] = useState<HistoryData>({ research: [], notes: [] });

  // Workspace restoration state
  const [restoredResearchPrompt, setRestoredResearchPrompt] = useState<string>('');
  const [restoredResearchResults, setRestoredResearchResults] = useState<SingleQuestionAnswer[] | null>(null);
  const [restoredNoteTopic, setRestoredNoteTopic] = useState<string>('');
  const [restoredNote, setRestoredNote] = useState<StudyNote | null>(null);

  useEffect(() => {
    fetchDocuments();
    fetchHistory();
    const interval = setInterval(fetchDocuments, 4000);
    return () => clearInterval(interval);
  }, []);

  const fetchDocuments = async () => {
    try {
      const resp = await fetch('/api/documents');
      if (resp.ok) {
        const data: DocumentItem[] = await resp.json();
        setDocuments(data);
        
        setSelectedDocIds((prev) => {
          if (prev.length === 0 && data.length > 0) {
            const indexed = data.filter(d => d.status === 'indexed');
            return indexed.length > 0 ? [indexed[0].id] : [];
          }
          return prev.filter(id => data.some(d => d.id === id));
        });
      }
    } catch (e) {
      console.error('Fetch documents error:', e);
    }
  };

  const fetchHistory = async () => {
    try {
      const resp = await fetch('/api/history');
      if (resp.ok) {
        const data: HistoryData = await resp.json();
        setHistory(data);
      }
    } catch (e) {
      console.error('Fetch history error:', e);
    }
  };

  const handleToggleDocSelect = (id: string) => {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleSelectAllDocs = (select: boolean) => {
    if (select) {
      setSelectedDocIds(documents.map((d) => d.id));
    } else {
      setSelectedDocIds([]);
    }
  };

  const handleUploadFile = async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const resp = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!resp.ok) {
        const errData = await resp.json();
        throw new Error(errData.detail || 'Failed to upload document.');
      }

      await fetchDocuments();
    } catch (e: any) {
      alert(`Upload Error: ${e.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDoc = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;

    try {
      const resp = await fetch(`/api/documents/${id}`, {
        method: 'DELETE',
      });
      if (resp.ok) {
        setSelectedDocIds((prev) => prev.filter((item) => item !== id));
        fetchDocuments();
      }
    } catch (e) {
      console.error('Delete error:', e);
    }
  };

  const handleExecuteResearch = async (prompt: string, docIds: string[]): Promise<SingleQuestionAnswer[]> => {
    const resp = await fetch('/api/research/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: prompt, document_ids: docIds }),
    });

    if (!resp.ok) {
      const errData = await resp.json();
      throw new Error(errData.detail || 'Research request failed.');
    }

    const data = await resp.json();
    fetchHistory();
    return data.results;
  };

  const handleGenerateAINotes = async (topic: string): Promise<StudyNote> => {
    const resp = await fetch('/api/notes/ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic }),
    });

    if (!resp.ok) {
      const errData = await resp.json();
      throw new Error(errData.detail || 'AI study notes request failed.');
    }

    const noteData = await resp.json();
    fetchHistory();
    return noteData;
  };

  // History restoration handlers
  const handleSelectResearchHistory = (item: ResearchHistoryItem) => {
    setCurrentMode('research');
    setRestoredResearchPrompt(item.question);
    setRestoredResearchResults(item.answers);
  };

  const handleSelectNoteHistory = (item: NotesHistoryItem) => {
    setCurrentMode('ai_notes');
    setRestoredNoteTopic(item.topic);
    setRestoredNote({
      id: item.id,
      mode: 'ai',
      title: item.title,
      topic_or_doc_ids: item.topic,
      sections: item.sections,
      created_at: item.created_at,
    });
  };

  const handleDeleteResearchHistory = async (id: string) => {
    try {
      const resp = await fetch(`/api/history/research/${id}`, { method: 'DELETE' });
      if (resp.ok) {
        setHistory((prev) => ({
          ...prev,
          research: prev.research.filter((r) => r.id !== id),
        }));
      }
    } catch (e) {
      console.error('Delete research history error:', e);
    }
  };

  const handleDeleteNoteHistory = async (id: string) => {
    try {
      const resp = await fetch(`/api/history/notes/${id}`, { method: 'DELETE' });
      if (resp.ok) {
        setHistory((prev) => ({
          ...prev,
          notes: prev.notes.filter((n) => n.id !== id),
        }));
      }
    } catch (e) {
      console.error('Delete note history error:', e);
    }
  };

  const handleClearAllHistory = async () => {
    if (!window.confirm('Are you sure you want to clear all history?')) return;
    try {
      const resp = await fetch('/api/history', { method: 'DELETE' });
      if (resp.ok) {
        setHistory({ research: [], notes: [] });
      }
    } catch (e) {
      console.error('Clear history error:', e);
    }
  };

  const selectedDocs = documents.filter((d) => selectedDocIds.includes(d.id));
  const totalHistoryCount = history.research.length + history.notes.length;

  return (
    <div className="app-container">
      <Sidebar
        documents={documents}
        selectedDocIds={selectedDocIds}
        onToggleDocSelect={handleToggleDocSelect}
        onSelectAllDocs={handleSelectAllDocs}
        onUploadFile={handleUploadFile}
        onDeleteDoc={handleDeleteDoc}
        isUploading={isUploading}
      />

      <main className="main-content">
        <header className="top-nav">
          <button
            className={`nav-tab ${currentMode === 'research' ? 'active' : ''}`}
            onClick={() => setCurrentMode('research')}
          >
            <Search size={17} />
            1. Document Research
          </button>
          <button
            className={`nav-tab ${currentMode === 'ai_notes' ? 'active' : ''}`}
            onClick={() => setCurrentMode('ai_notes')}
          >
            <BookOpen size={17} />
            2. AI Study Notes
          </button>

          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center' }}>
            <button
              className="btn-history-toggle"
              onClick={() => setIsHistoryOpen(true)}
              title="View past searches & notes"
            >
              <Clock size={16} />
              <span>History</span>
              {totalHistoryCount > 0 && (
                <span className="history-badge-count">{totalHistoryCount}</span>
              )}
            </button>
          </div>
        </header>

        <div className="workspace-body">
          {currentMode === 'research' && (
            <DocumentResearchView
              selectedDocuments={selectedDocs}
              onExecuteResearch={handleExecuteResearch}
              initialPrompt={restoredResearchPrompt}
              initialResults={restoredResearchResults}
            />
          )}

          {currentMode === 'ai_notes' && (
            <AINotesView
              onGenerateAINotes={handleGenerateAINotes}
              initialTopic={restoredNoteTopic}
              initialNote={restoredNote}
            />
          )}
        </div>
      </main>

      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={history}
        onSelectResearch={handleSelectResearchHistory}
        onSelectNote={handleSelectNoteHistory}
        onDeleteResearch={handleDeleteResearchHistory}
        onDeleteNote={handleDeleteNoteHistory}
        onClearAll={handleClearAllHistory}
      />
    </div>
  );
};
