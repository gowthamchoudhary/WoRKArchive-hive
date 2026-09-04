import api from "./axios";

export async function generatePost(workSummaryId) {
  const response = await api.post("/post/generate_post", null, {
    params: {
      work_summary_id: workSummaryId,
    },
  });

  return response.data;
}
