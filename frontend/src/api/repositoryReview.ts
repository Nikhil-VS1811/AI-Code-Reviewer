import { apiClient } from "./client";
import type { RepositoryReviewResult } from "../types/api";

export async function analyzeRepository(repoUrl: string): Promise<RepositoryReviewResult> {
  const { data } = await apiClient.post<RepositoryReviewResult>("/repository-review/", {
    repo_url: repoUrl,
  });

  return data;
}
