export interface DetectionBatch {
  id: number;
  created_at: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  total_papers: number;
  processed_papers: number;
}

export interface Paper {
  id: number;
  batch_id: number;
  filename: string;
  student_id: string | null;
  student_name: string | null;
  class_name: string | null;
  ai_score: number | null;
  status: string;
}

export interface Paragraph {
  id: number;
  paragraph_index: number;
  content: string;
  ai_score: number;
  confidence: string;
  reasons: string[];
}

export interface PaperDetail extends Paper {
  paragraphs: Paragraph[];
}
