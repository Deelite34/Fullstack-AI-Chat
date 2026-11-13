import type React from "react";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import axios from "axios";
import { toast } from "react-toastify";
import {
  getCurrentUserAPI,
  loginAPI,
  logoutAPI,
  refreshAPI,
  type UserProfile,
} from "../Services/AuthService";
import {
  getAccessToken,
  setAccessToken,
  setSessionExpiredHandler,
} from "../Services/api";

type UserContextType = {
  user: UserProfile | null;
  sessionState: "checking" | "ready" | "unavailable";
  retrySessionCheck: () => Promise<void>;
  loginUser: (username: string, password: string) => Promise<void>;
  logoutUser: () => Promise<void>;
};

type Props = { children: React.ReactNode };

const UserContext = createContext<UserContextType>({} as UserContextType);

export const UserProvider = ({ children }: Props) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [sessionState, setSessionState] = useState<
    UserContextType["sessionState"]
  >("checking");

  const retrySessionCheck = useCallback(async () => {
    setSessionState("checking");
    try {
      const { data: tokenResponse } = await refreshAPI();
      setAccessToken(tokenResponse.token);
      const { data: currentUser } = await getCurrentUserAPI();
      setUser(currentUser);
      setSessionState("ready");
    } catch (error) {
      setAccessToken(null);
      setUser(null);
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        setSessionState("ready");
      } else {
        console.error("Could not restore the authentication session", error);
        setSessionState("unavailable");
      }
    }
  }, []);

  useEffect(() => {
    setSessionExpiredHandler(() => {
      setUser(null);
      setSessionState("ready");
    });

    const startupCheck = window.setTimeout(() => {
      void retrySessionCheck();
    }, 0);
    return () => {
      window.clearTimeout(startupCheck);
      setSessionExpiredHandler(() => {});
    };
  }, [retrySessionCheck]);

  const loginUser = async (username: string, password: string) => {
    const { data: tokenResponse } = await loginAPI(username, password);
    setAccessToken(tokenResponse.token);
    try {
      const { data: currentUser } = await getCurrentUserAPI();
      setUser(currentUser);
      setSessionState("ready");
      toast.success("Logged in successfully");
    } catch (error) {
      setAccessToken(null);
      setUser(null);
      setSessionState("ready");
      throw error;
    }
  };

  const logoutUser = async () => {
    const token = getAccessToken();
    if (token) {
      await logoutAPI(token);
    }
    setAccessToken(null);
    setUser(null);
    setSessionState("ready");
    toast.success("Logged out");
  };

  return (
    <UserContext.Provider
      value={{ loginUser, user, logoutUser, sessionState, retrySessionCheck }}
    >
      {children}
    </UserContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(UserContext);
