import { UserSearch } from "lucide-react";
import api from "./axios";

export const registerUser = async (userData) => {
  const response = await api.post("/v1/auth/register", userData);
  return response.data;
};
export const loginUser = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
  const response = await api.post("/v1/auth/login", formData);
  return response.data;
};

export const refreshToken = async () => {
  const response = await api.post("/v1/auth/refresh");

  return response.data;
};
export const logoutUser = async () => {
  const response = await api.post("/v1/auth/logout");

  return response.data;
};
