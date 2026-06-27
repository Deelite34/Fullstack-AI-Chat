import reactLogo from '../assets/react.svg'
import viteLogo from '../assets/vite.svg'
import heroImg from '../assets/hero.png'
import AboutModal from "./components/about-modal/AboutModal"
import './App.css'
import ConversationChatBox from './components/chat/ChatBox';

function App() {
  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="" />
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>
        <div>
          <h1>Chatbot app</h1>
          <main className="flex flex-col items-center justify-center">
            <div className="modal-nonfocus-bg" id="nonfocus-bg"/>
            <AboutModal />
            <ConversationChatBox />
          </main>
        </div>
        
      </section>

      <div className="ticks"></div>

      

      <div className="ticks"></div>
      <section id="spacer"></section>
    
    </>
  )
}

export default App
