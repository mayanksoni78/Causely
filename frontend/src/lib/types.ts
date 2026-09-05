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
  metadata: Record<string, unknown>;
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
  status: 'queued' | 'investigating' | 'failed' | 'insufficient_evidence' | 'completed';
  createdAt: string;
  hypotheses: Hypothesis[];
  evidence: EvidenceChunk[];
  trace: InvestigationTraceStep[];
  final_report?: Record<string, unknown>;
  confidence_level?: string;
  confidence_score?: number;
  confidence?: ConfidenceScore;
}

export interface Source {
  id: string;
  type: string;
  category?: string;
  provider?: string;
  name: string;
  status: 'connected' | 'disconnected' | 'error' | 'coming_soon' | 'connecting';
  config?: Record<string, unknown>;
  capabilities?: string[];
}

export interface DashboardStats {
  total_incidents: number;
  completed_investigations: number;
  active: number;
  avg_confidence: number;
  avg_confidence_level: string;
  sources_connected: number;
}
