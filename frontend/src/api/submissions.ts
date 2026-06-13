import { apiClient } from "./client";
import type { Submission, SubmissionCreate } from "../types/api";

export async function listSubmissions(): Promise<Submission[]> {
  const { data } = await apiClient.get<Submission[]>("/submissions");
  return data;
}

export async function createSubmission(payload: SubmissionCreate): Promise<Submission> {
  const { data } = await apiClient.post<Submission>("/submissions", payload);
  return data;
}

export async function getSubmission(id: number): Promise<Submission> {
  const { data } = await apiClient.get<Submission>(`/submissions/${id}`);
  return data;
}
