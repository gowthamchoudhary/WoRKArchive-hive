import api from "./axios";

export async function loginUser(email, password) {
  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);

  const response = await api.post("/v1/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return response.data;
}

export async function registerUser(username, email, password) {
  const response = await api.post("/v1/auth/register", {
    username,
    email,
    password,
  });

  return response.data;
}

export async function logoutUser() {
  const response = await api.post("/v1/auth/logout");
  return response.data;
}
