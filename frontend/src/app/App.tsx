import AboutModal from "./components/about-modal/AboutModal";
import "./App.css";
import ConversationChatBox from "./components/chat/ChatBox";
import SignInModal from "./components/SignInModal/SignInModal";
import SignUpModal from "./components/SignUpModal/SignUpModal";
import { useAuth, UserProvider } from "./Context/useAuth";
import { toast, ToastContainer } from "react-toastify";

function App() {
  return (
    <UserProvider>
      <AppContent />
    </UserProvider>
  );
}

function AppContent() {
  const auth = useAuth();
  return (
    <>
      <ToastContainer position="top-center" />
      {auth.sessionState === "checking" && (
        <p className="p-4 text-center" role="status">
          Checking your session...
        </p>
      )}
      {auth.sessionState === "unavailable" && (
        <section className="flex flex-col items-center gap-3 p-4" role="alert">
          <p>Could not check your session. Check your connection and try again.</p>
          <button
            className="generic-btn hover:cursor-pointer"
            onClick={() => void auth.retrySessionCheck()}
          >
            Retry
          </button>
        </section>
      )}
      {auth.sessionState === "ready" && (
        <>
          <section id="center">
            <div>
              <h1>Chatbot app</h1>
            </div>
            <main className="flex flex-col items-center justify-center">
              <div className="modal-nonfocus-bg" id="nonfocus-bg" />
              <div className="flex flex-row w-full gap-1">
                {auth.user ? (
                  <>
                    <span className="grow self-center">
                      Signed in as {auth.user.username}
                    </span>
                    <button
                      className="generic-btn hover:cursor-pointer grow"
                      onClick={() => {
                        void auth.logoutUser().catch((error: unknown) => {
                          toast.error(`Logout failed: ${error}`);
                        });
                      }}
                    >
                      Log out
                    </button>
                  </>
                ) : (
                  <>
                    <SignUpModal />
                    <SignInModal />
                  </>
                )}
                <AboutModal />
              </div>
              <ConversationChatBox />
            </main>
          </section>
          <div className="ticks"></div>
          <div className="ticks"></div>
          <section id="spacer"></section>
        </>
      )}
    </>
  );
}

export default App;
