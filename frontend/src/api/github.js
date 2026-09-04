import api from "./axios";

const API_BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/+$/, "") || "";

export async function getGithubMe() {
  const response = await api.get("/api/v1/auth/github/me");
  return response.data;
}

export async function getGithubActivity(postTime) {
  const response = await api.get("/api/v1/auth/github/activity/today", {
    params: {
      post_time: postTime,
    },
  });

  return response.data;
}

export async function getGithubActivities(postTime) {
  const response = await api.get("/api/v1/auth/github/retrieve_activity", {
    params: {
      post_time: postTime,
    },
  });

  return response.data;
}

export async function getWorkSummary(postTime) {
  const response = await api.get("/api/v1/auth/github/retrieve_summary_llm", {
    params: {
      post_time: postTime,
    },
  });

  return response.data;
}
export function connectGithub() {
  window.location.href = `${API_BASE_URL}/api/v1/auth/github/login`;
}
