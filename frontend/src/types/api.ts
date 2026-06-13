export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface SignupPayload extends LoginPayload {
  username: string;
}

export interface Submission {
  id: number;
  user_id: number;
  language: string;
  code: string;
  created_at: string;
}

export interface SubmissionCreate {
  language: string;
  code: string;
}

export interface ReviewComment {
  id: number;
  review_id: number;
  line_number: number;
  severity: string;
  category: string;
  comment: string;
}

export interface Review {
  id: number;
  submission_id: number;
  overall_score: number;
  security_score: number;
  performance_score: number;
  maintainability_score: number;
  readability_score: number;
  summary: string;
  created_at: string;
  comments: ReviewComment[];
}

export interface RepositoryFinding {
  file: string;
  line_number: number;
  severity: "critical" | "high" | "medium" | "low" | string;
  category: string;
  comment: string;
}

export interface RepositoryReviewResult {
  files_scanned: number;
  issues_found: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  repository_health_score: number;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  findings: RepositoryFinding[];
}

export interface ApiErrorResponse {
  detail?: string | { status?: string; checks?: Record<string, string> };
}
