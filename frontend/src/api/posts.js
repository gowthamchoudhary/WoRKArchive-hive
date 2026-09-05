// import api from "./axios";

// export async function generatePost(workSummaryId) {
//   const response = await api.post("/post/generate_post", null, {
//     params: {
//       work_summary_id: workSummaryId,
//     },
//   });

//   return response.data;
// }
import api from "./axios";

export async function generatePost(
  workSummaryId,
  platform,
  postLength,
  style,
  inspiration,
  excludedTopics,
) {
  const response = await api.post("/post/generate_post", excludedTopics, {
    params: {
      work_summary_id: workSummaryId,
      platform,
      post_length: postLength,
      style,
      inspiration,
    },
  });

  return response.data;
}

export async function getPosts(workSummaryId) {
  const response = await api.get(`/post/retrieve_posts/${workSummaryId}`);

  return response.data;
}
