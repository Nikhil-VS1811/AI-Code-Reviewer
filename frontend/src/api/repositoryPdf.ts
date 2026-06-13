import { apiClient } from "./client";

export async function exportRepositoryPdf(repoUrl: string) {
  const response = await apiClient.post(
    "/repository-review/export-pdf",
    {
      repo_url: repoUrl,
    },
    {
      responseType: "blob",
    }
  );

  return response.data;
}