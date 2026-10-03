import React, { useState, useEffect } from 'react';
import { Search, FileText, AlertCircle, Bookmark, Copy, Check, Terminal } from 'lucide-react';
import { DocumentItem, SingleQuestionAnswer } from '../types';

interface DocumentResearchViewProps {
  selectedDocuments: DocumentItem[];
  onExecuteResearch: (prompt: string, documentIds: string[]) => Promise<SingleQuestionAnswer[]>;
  initialPrompt?: string;
  initialResults?: SingleQuestionAnswer[] | null;
}

const CodeBlock: React.FC<{ language: string; code: string }> = ({ language, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const displayLang = language.trim() || 'bash';

  return (
    <div className="markdown-code-block">
      <div className="code-header">
        <span className="code-lang-tag">
          <Terminal size={12} />
          {displayLang}
        </span>
        <button
          className={`code-copy-btn ${copied ? 'copied' : ''}`}
          onClick={handleCopy}
          type="button"
          title="Copy command to clipboard"
        >
          {copied ? (
            <>
              <Check size={12} />
              Copied!
            </>
          ) : (
            <>
              <Copy size={12} />
              Copy
            </>
          )}
        </button>
      </div>
      <pre className="code-body">
        <code>{code}</code>
      </pre>
    </div>
  );
};

const FormattedTextSegment: React.FC<{ text: string }> = ({ text }) => {
  if (!text) return null;

  // Split lines to preserve paragraphs
  const paragraphs = text.split('\n\n').filter((p) => p.trim().length > 0);

  return (
    <>
      {paragraphs.map((para, pIdx) => {
        // Parse inline code like `command`
        const parts = para.split(/(`[^`]+`)/g);

        return (
          <p key={pIdx} className="answer-paragraph">
            {parts.map((part, idx) => {
              if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
                return (
                  <code key={idx} className="inline-code">
                    {part.slice(1, -1)}
                  </code>
                );
              }
              return part;
            })}
          </p>
        );
      })}
    </>
  );
};

const FormattedAnswer: React.FC<{ answer: string }> = ({ answer }) => {
  if (!answer) return null;

  // Regex to extract ```lang ... ``` blocks
  const codeBlockRegex = /```([a-zA-Z0-9_\-\+]*)\n([\s\S]*?)```/g;
  const elements: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = codeBlockRegex.exec(answer)) !== null) {
    const textBefore = answer.slice(lastIndex, match.index);
    if (textBefore.trim()) {
      elements.push(
        <FormattedTextSegment key={`text-${lastIndex}`} text={textBefore} />
      );
    }

    const lang = match[1] || 'bash';
    const code = match[2].trimEnd();
    elements.push(
      <CodeBlock key={`code-${match.index}`} language={lang} code={code} />
    );

    lastIndex = match.index + match[0].length;
  }

  const remainingText = answer.slice(lastIndex);
  if (remainingText.trim()) {
    elements.push(
      <FormattedTextSegment key={`text-${lastIndex}`} text={remainingText} />
    );
  }

  return <div className="answer-text">{elements}</div>;
};

export const DocumentResearchView: React.FC<DocumentResearchViewProps> = ({
  selectedDocuments,
  onExecuteResearch,
  initialPrompt = '',
  initialResults = null,
}) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SingleQuestionAnswer[] | null>(initialResults);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (initialPrompt) setPrompt(initialPrompt);
    if (initialResults) setResults(initialResults);
  }, [initialPrompt, initialResults]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    if (selectedDocuments.length === 0) {
      setErrorMsg('Please select at least one document from the sidebar to research.');
      return;
    }

    setErrorMsg(null);
    setIsLoading(true);
    setResults(null);

    try {
      const docIds = selectedDocuments.map((d) => d.id);
      const res = await onExecuteResearch(prompt.trim(), docIds);
      setResults(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to execute document research.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div className="card">
        <div className="card-title">
          <Search size={20} color="var(--primary-blue)" />
          Document Research Mode (NVIDIA Grounded RAG)
        </div>
        <div className="card-desc">
          Ask single or multiple questions. Answers are <strong>strictly grounded</strong> in your selected document(s).
          If evidence is missing, the system will strictly return <em>"Not found in document."</em>
        </div>

        {selectedDocuments.length === 0 ? (
          <div style={{
            padding: '0.85rem 1rem',
            backgroundColor: '#fffbe8',
            border: '1px solid #fef08a',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.85rem',
            color: '#854d0e',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '1rem'
          }}>
            <AlertCircle size={16} />
            No document selected. Check one or more documents in the sidebar.
          </div>
        ) : (
          <div style={{
            fontSize: '0.825rem',
            color: 'var(--primary-blue)',
            fontWeight: 600,
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}>
            <FileText size={15} />
            Querying across {selectedDocuments.length} document{selectedDocuments.length > 1 ? 's' : ''}:{' '}
            {selectedDocuments.map(d => d.filename).join(', ')}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">
              Enter Question(s):
            </label>
            <textarea
              className="form-textarea"
              rows={4}
              placeholder="e.g. 1. How to install Sublime Text on Linux?&#10;2. What are the key features of the editor?"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
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
            disabled={isLoading || !prompt.trim() || selectedDocuments.length === 0}
          >
            <Search size={16} />
            {isLoading ? 'Retrieving Evidence & Querying NVIDIA...' : 'Research Document(s)'}
          </button>
        </form>
      </div>

      {results && (
        <div style={{ marginTop: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-dark)' }}>
            Research Results ({results.length} Question{results.length > 1 ? 's' : ''})
          </h3>

          {results.map((res, idx) => (
            <div key={idx} className="result-item">
              <div className="question-badge">
                {results.length > 1 ? `Q${idx + 1}: ${res.question}` : `Question: ${res.question}`}
              </div>

              {!res.found_in_document || res.answer === "Not found in document." ? (
                <div style={{ marginTop: '0.5rem', marginBottom: '0.5rem' }}>
                  <span className="not-found-tag">Not found in document.</span>
                </div>
              ) : (
                <FormattedAnswer answer={res.answer} />
              )}

              {res.sources && res.sources.length > 0 && (
                <div className="sources-box">
                  <div className="sources-header">
                    <Bookmark size={13} style={{ display: 'inline', marginRight: '4px' }} />
                    Real Grounded Sources ({res.sources.length} chunk{res.sources.length > 1 ? 's' : ''})
                  </div>
                  {res.sources.map((src, sIdx) => (
                    <div key={sIdx} className="source-chip">
                      <div className="source-meta">
                        {src.filename} • Page {src.page_number} • Chunk ID: {src.chunk_id}
                      </div>
                      <div className="source-snippet">
                        "{src.content}"
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
