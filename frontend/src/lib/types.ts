export type ConfidenceLevel = 'high' | 'medium' | 'low' | 'insufficient';

export interface ConfidenceScore {
  overall: ConfidenceLevel;
  retrievalScore: number;
  sourceAgreement: number;
  coverage: number;
  recency: number;
  corroborationCount: number;
}

export interface EvidenceChunk {
  id: string;
  sourceId: string;
  type: 'log' | 'commit' | 'pr' | 'metric' | 'docs';
  content: string;
  url?: string;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface Hypothesis {
  id: string;
  title: string;
  description: string;
  confidence: ConfidenceScore;
  evidenceIds: string[];
  remediation: string;
}

export interface InvestigationTraceStep {
  id: string;
  timestamp: string;
  action: string;
  details: string;
  status: 'pending' | 'success' | 'failed' | 'skipped';
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  affectedService?: string;
  timeframe: { from: string; to: string };
  status: 'open' | 'queued' | 'investigating' | 'failed' | 'insufficient_evidence' | 'resolved' | 'completed';
  createdAt: string;
  hypotheses: Hypothesis[];
  evidence: EvidenceChunk[];
  trace: InvestigationTraceStep[];
  final_report?: any;
  confidence_level?: string;
  confidence_score?: number;
  confidence?: any;
}

export interface Source {
  id: string;
  type: string;
  category?: string;
  provider?: string;
  name: string;
  status: 'connected' | 'disconnected' | 'error' | 'coming_soon' | 'connecting';
  config?: Record<string, any>;
  capabilities?: string[];
}
