import React, { useState } from 'react';
import { Clock, Search, BookOpen, Trash2, X, ChevronRight, FileText } from 'lucide-react';
import { HistoryData, ResearchHistoryItem, NotesHistoryItem } from '../types';

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: HistoryData;
  onSelectResearch: (item: ResearchHistoryItem) => void;
  onSelectNote: (item: NotesHistoryItem) => void;
  onDeleteResearch: (id: string) => void;
  onDeleteNote: (id: string) => void;
  onClearAll: () => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  history,
  onSelectResearch,
  onSelectNote,
  onDeleteResearch,
  onDeleteNote,
  onClearAll,
}) => {
  const [filterType, setFilterType] = useState<'all' | 'research' | 'notes'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  if (!isOpen) return null;

  const formatDate = (isoStr: string) => {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoStr;
    }
  };

  const filteredResearch = history.research.filter(
    (item) =>
      item.question.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredNotes = history.notes.filter(
    (item) =>
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.topic.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalCount = history.research.length + history.notes.length;

  return (
    <div className="history-drawer-overlay" onClick={onClose}>
      <div className="history-drawer" onClick={(e) => e.stopPropagation()}>
        <div className="history-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Clock size={20} color="var(--primary-blue)" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-dark)', margin: 0 }}>
              Search & Notes History
            </h3>
            <span style={{
              fontSize: '0.75rem',
              backgroundColor: 'var(--bg-sky-hover)',
              color: 'var(--primary-blue)',
              padding: '0.15rem 0.5rem',
              borderRadius: '12px',
              fontWeight: 600,
            }}>
              {totalCount}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {totalCount > 0 && (
              <button
                className="btn-clear-history"
                onClick={onClearAll}
                title="Clear all saved history"
              >
                Clear All
              </button>
            )}
            <button className="btn-close-drawer" onClick={onClose}>
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Search input */}
        <div style={{ padding: '0.75rem 1.25rem', borderBottom: '1px solid var(--border-color)' }}>
          <div className="history-search-box">
            <Search size={15} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search past queries or notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="history-search-input"
            />
          </div>
        </div>

        {/* Filter subtabs */}
        <div className="history-tabs">
          <button
            className={`history-tab-btn ${filterType === 'all' ? 'active' : ''}`}
            onClick={() => setFilterType('all')}
          >
            All ({totalCount})
          </button>
          <button
            className={`history-tab-btn ${filterType === 'research' ? 'active' : ''}`}
            onClick={() => setFilterType('research')}
          >
            Research ({history.research.length})
          </button>
          <button
            className={`history-tab-btn ${filterType === 'notes' ? 'active' : ''}`}
            onClick={() => setFilterType('notes')}
          >
            AI Notes ({history.notes.length})
          </button>
        </div>

        {/* List of history items */}
        <div className="history-list">
          {totalCount === 0 ? (
            <div className="history-empty">
              <Clock size={32} color="var(--text-light)" style={{ marginBottom: '0.5rem' }} />
              <p>No search or study history yet.</p>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Your Document Research queries and AI Study Notes will appear here automatically.
              </span>
            </div>
          ) : (
            <>
              {(filterType === 'all' || filterType === 'research') &&
                filteredResearch.map((item) => (
                  <div
                    key={`res-${item.id}`}
                    className="history-card"
                    onClick={() => {
                      onSelectResearch(item);
                      onClose();
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span className="history-tag tag-research">
                        <Search size={11} style={{ display: 'inline', marginRight: 3 }} />
                        Document Research
                      </span>
                      <span className="history-date">{formatDate(item.created_at)}</span>
                    </div>

                    <div className="history-query-title" title={item.question}>
                      {item.question}
                    </div>

                    <div className="history-footer">
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {item.answers?.length || 0} answer(s) • {item.selected_doc_ids?.length || 0} doc(s)
                      </span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <button
                          className="btn-history-delete"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteResearch(item.id);
                          }}
                          title="Delete from history"
                        >
                          <Trash2 size={13} />
                        </button>
                        <ChevronRight size={15} color="var(--primary-blue)" />
                      </div>
                    </div>
                  </div>
                ))}

              {(filterType === 'all' || filterType === 'notes') &&
                filteredNotes.map((item) => (
                  <div
                    key={`note-${item.id}`}
                    className="history-card"
                    onClick={() => {
                      onSelectNote(item);
                      onClose();
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span className="history-tag tag-notes">
                        <BookOpen size={11} style={{ display: 'inline', marginRight: 3 }} />
                        AI Study Notes
                      </span>
                      <span className="history-date">{formatDate(item.created_at)}</span>
                    </div>

                    <div className="history-query-title" title={item.title}>
                      {item.title}
                    </div>

                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      Topic: {item.topic}
                    </div>

                    <div className="history-footer">
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {Object.keys(item.sections || {}).length} sections generated
                      </span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <button
                          className="btn-history-delete"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteNote(item.id);
                          }}
                          title="Delete from history"
                        >
                          <Trash2 size={13} />
                        </button>
                        <ChevronRight size={15} color="var(--primary-blue)" />
                      </div>
                    </div>
                  </div>
                ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
