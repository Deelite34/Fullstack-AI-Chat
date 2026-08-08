import type React from "react";
import { createContext, useContext, useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { loginAPI, registerAPI } from "../Services/AuthService";
import axios from "axios";
import type { UserProfile } from "../models/User";

// TODO: MIGRATE FROM FETCH API TO AXIOS AND USE DEFAULT(AUTO INJECTED AUTH HEADERS)
// https://youtu.be/h3_YKC2VGfE?si=wdlmuBOcHE_AFzcJ&t=1141
type UserContextType = {
  user: UserProfile | null;
  token: string | null;
  loginUser: (username: string, password: string) => void;
  registerUser: (email: string, username: string, password: string) => void;
  logoutUser: () => void;
  isLoggedIn: () => boolean;
};

type Props = { children: React.ReactNode };

const UserContext = createContext<UserContextType>({} as UserContextType);

export const UserProvider = ({ children }: Props) => {
  // const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const user = localStorage.getItem("user");
    const token = localStorage.getItem("token");
    if (user && token) {
      setUser(JSON.parse(user));
      setToken(token);
      axios.defaults.headers.common["Authorization"] = "Bearer " + token;
    }
    setIsReady(true);
  }, []);

  const registerUser = async (
    email: string,
    username: string,
    password: string,
  ) => {
    await registerAPI(email, username, password)
      .then((res) => {
        if (res) {
          localStorage.setItem("token", res?.data.token);
          const userObj = {
            username: res?.data.username,
            email: res?.data.email,
          };
          setToken(res?.data.access_token!);
          setUser(userObj!);
          toast.success("Registration succesful");
        }
      })
      .catch((e) => toast.warning(`Server error occured: ${e}`));
  };

  const loginUser = async (username: string, password: string) => {
    await loginAPI(username, password)
      .then((res) => {
        if (res) {
          localStorage.setItem("token", res?.data.token);
          // TODO login endpoint returns access/refresh tokens, not username/email
          const userObj = {
            username: res?.data.username,
            email: res?.data.email,
          };
          setToken(res?.data.access_token!);
          setUser(userObj!);
          toast.success("Login succesful");
        }
      })
      .catch((e) => toast.warning(`Server error occured: ${e}`));
  };

  const isLoggedIn = () => {
    return !!user;
  };

  const validateSession = () => {
    // explicitly log user out
    const session_valid = !!user;
    if(!!user) {logoutUser()};
    

  }

  const logoutUser = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setToken("");
  };

  return (
    <UserContext.Provider
      value={{ loginUser, user, token, logoutUser, isLoggedIn, registerUser }}
    >
      {isReady ? children : null}
    </UserContext.Provider>
  );
};

export const useAuth = () => useContext(UserContext);
