import { apiClient } from "./client";
import type { Review } from "../types/api";

export async function listReviews(): Promise<Review[]> {
  const { data } = await apiClient.get<Review[]>("/reviews");
  return data;
}

export async function getReview(id: number): Promise<Review> {
  const { data } = await apiClient.get<Review>(`/reviews/${id}`);
  return data;
}

export async function generateReview(submissionId: number): Promise<Review> {
  const { data } = await apiClient.post<Review>(`/reviews/generate/${submissionId}`);
  return data;
}

export async function exportReviewPdf(id: number): Promise<Blob> {
  const { data } = await apiClient.get<Blob>(`/reviews/${id}/pdf`, {
    responseType: "blob",
  });
  return data;
}
