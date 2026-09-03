import api from "./axios";


export const current_user = () => {
  return api.get("/auth/me");
};