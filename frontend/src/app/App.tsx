import AboutModal from "./components/about-modal/AboutModal"
import './App.css'
import ConversationChatBox from './components/chat/ChatBox';
import SignInModal from './components/SignInModal/SignInModal'
import SignUpModal from './components/SignUpModal/SignUpModal'


function App() {
  return (
    <>
      <section id="center">
        <div>
          <h1>Chatbot app</h1>
        </div>
        <main className="flex flex-col items-center justify-center">
          <div className="modal-nonfocus-bg" id="nonfocus-bg"/>
          <div className="flex flex-row w-full gap-1">
            <SignUpModal />
            <SignInModal />
            <AboutModal />
          </div>
          <ConversationChatBox />
        </main>
      </section>
      <div className="ticks"></div>
      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  )
}

export default App
