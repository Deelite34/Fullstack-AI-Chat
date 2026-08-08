import api from "./api";

// base url is handled by vite proxy

export const registerAPI = async (
  username: string,
  email: string,
  password: string,
) => {
  try {
    const { data } = await api.post("/auth/register", {
      username,
      email,
      password,
    });

    console.info("Registered successfully", data);
    return data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const loginAPI = async (username: string, password: string) => {
  try {
    const { data } = await api.post("/auth/login", {
      username,
      password,
    });

    console.info("Logged in successfully", data);
    return data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const checkJWT = async (access_token: string) => {
  try {
    const { data } = await api.post("/auth/login", {
      username,
      password,
    });

    console.info("Logged in successfully", data);
    return data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};