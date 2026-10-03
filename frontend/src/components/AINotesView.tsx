import React, { useState, useEffect } from 'react';
import { BookOpen, Sparkles, HelpCircle, ArrowRight } from 'lucide-react';
import { StudyNote } from '../types';

interface AINotesViewProps {
  onGenerateAINotes: (topic: string) => Promise<StudyNote>;
  initialTopic?: string;
  initialNote?: StudyNote | null;
}

export const AINotesView: React.FC<AINotesViewProps> = ({
  onGenerateAINotes,
  initialTopic = '',
  initialNote = null,
}) => {
  const [topic, setTopic] = useState(initialTopic);
  const [isLoading, setIsLoading] = useState(false);
  const [note, setNote] = useState<StudyNote | null>(initialNote);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (initialTopic) setTopic(initialTopic);
    if (initialNote) setNote(initialNote);
  }, [initialTopic, initialNote]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setErrorMsg(null);
    setIsLoading(true);

    try {
      const res = await onGenerateAINotes(topic.trim());
      setNote(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to generate AI study notes.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChipClick = (sampleQuery: string) => {
    setTopic(sampleQuery);
  };

  const renderSectionContent = (title: string, content: any) => {
    if (!content) return <p style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>N/A</p>;

    if (Array.isArray(content)) {
      if (content.length === 0) return <p style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>N/A</p>;

      // Check if item is { term, definition }
      if (typeof content[0] === 'object' && content[0] !== null && 'term' in content[0]) {
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {content.map((item: any, idx: number) => (
              <div key={idx} className="term-item">
                <span className="term-title">{item.term}: </span>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-dark)' }}>{item.definition}</span>
              </div>
            ))}
          </div>
        );
      }

      return (
        <ul className="note-list">
          {content.map((item: any, idx: number) => (
            <li key={idx}>
              {typeof item === 'string' ? item : JSON.stringify(item)}
            </li>
          ))}
        </ul>
      );
    }

    if (typeof content === 'string') {
      return <p style={{ fontSize: '0.875rem', lineHeight: '1.6' }}>{content}</p>;
    }

    return <pre style={{ fontSize: '0.8rem' }}>{JSON.stringify(content, null, 2)}</pre>;
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div className="card">
        <div className="card-title">
          <BookOpen size={20} color="var(--primary-blue)" />
          AI Study Notes Engine (Groq High-Speed Generation)
        </div>
        <div className="card-desc">
          Enter any academic topic OR complex question. The engine generates exhaustive, exam-oriented 9-part structured study notes.
        </div>

        {/* Quick sample chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <HelpCircle size={13} /> Try asking:
          </span>
          {[
            'Explain normalization and compare 2NF with 3NF with examples',
            'Operating System Deadlock: 4 Conditions & Prevention',
            'Binary Search Tree vs AVL Tree with operations',
            'Dijkstra vs Bellman-Ford Shortest Path Algorithms'
          ].map((sample, idx) => (
            <button
              key={idx}
              type="button"
              className="quick-chip-btn"
              onClick={() => handleChipClick(sample)}
            >
              {sample.length > 42 ? sample.slice(0, 42) + '...' : sample}
            </button>
          ))}
        </div>

        <form onSubmit={handleGenerate}>
          <div className="form-group">
            <label className="form-label">
              Enter Topic or Question:
            </label>
            <textarea
              className="form-textarea"
              rows={3}
              placeholder="e.g. Explain Database Normalization and compare 2NF with 3NF with examples"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>

          {errorMsg && (
            <div style={{ color: 'var(--accent-red)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
              {errorMsg}
            </div>
          )}

          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading || !topic.trim()}
          >
            <Sparkles size={16} />
            {isLoading ? 'Synthesizing 9-Part Study Notes via Groq...' : 'Generate 9-Part Study Notes'}
          </button>
        </form>
      </div>

      {note && note.sections && (
        <div style={{ marginTop: '1.5rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1rem',
            paddingBottom: '0.5rem',
            borderBottom: '1px solid var(--border-color)'
          }}>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-dark)', margin: 0 }}>
                {note.title}
              </h2>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Topic / Query: {note.topic_or_doc_ids}
              </div>
            </div>
            <span style={{
              fontSize: '0.75rem',
              backgroundColor: 'var(--bg-sky-light)',
              color: 'var(--primary-blue)',
              padding: '0.3rem 0.75rem',
              borderRadius: '16px',
              fontWeight: 600,
              border: '1px solid #bae6fd'
            }}>
              9-Part Academic Notes
            </span>
          </div>

          <div className="notes-section-grid">
            {Object.entries(note.sections).map(([secTitle, secData]) => (
              <div key={secTitle} className="note-box">
                <div className="note-box-title">{secTitle}</div>
                {renderSectionContent(secTitle, secData)}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
