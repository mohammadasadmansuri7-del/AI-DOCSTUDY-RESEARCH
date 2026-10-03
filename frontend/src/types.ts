export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  status: 'processing' | 'indexed' | 'error';
  error_message?: string;
  chunk_count: number;
  page_count: number;
  created_at: string;
}

export interface Citation {
  document_id: string;
  filename: string;
  page_number: number;
  chunk_id: string;
  content: string;
}

export interface SingleQuestionAnswer {
  question: string;
  answer: string;
  sources: Citation[];
  found_in_document: boolean;
}

export interface StudyNote {
  id: string;
  mode: 'ai';
  title: string;
  topic_or_doc_ids: string;
  sections: {
    [key: string]: any;
  };
  created_at: string;
}

export interface ResearchHistoryItem {
  id: string;
  type: 'research';
  question: string;
  selected_doc_ids: string[];
  answers: SingleQuestionAnswer[];
  created_at: string;
}

export interface NotesHistoryItem {
  id: string;
  type: 'note';
  title: string;
  topic: string;
  sections: { [key: string]: any };
  created_at: string;
}

export interface HistoryData {
  research: ResearchHistoryItem[];
  notes: NotesHistoryItem[];
}
