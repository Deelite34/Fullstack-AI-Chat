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
        <div>
          <div id="header-logo" className="flex flex-row sm:flex-col">
            <div className="hero">
              TODO:fix scaling of the hero image, it is currently too small and not responsive. The image should scale properly with different screen sizes and maintain its aspect ratio. Consider using CSS properties like `max-width`, `height`, and `object-fit` to achieve this. Additionally, ensure that the image is optimized for web use to improve loading times and performance.
            <img src={heroImg} className="base" width="170" height="179" alt="" />
            <img src={reactLogo} className="framework" alt="React logo" />
            <img src={viteLogo} className="vite" alt="Vite logo" />
          </div>
          <h1>Chatbot app</h1>
        </div>
        <main className="flex flex-col items-center justify-center">
          <div className="modal-nonfocus-bg" id="nonfocus-bg"/>
          <div className="flex flex-row w-full gap-1">
            <button className="generic-btn w-1/3 hover:cursor-pointer grow">sign up</button>
            <button className="generic-btn w-1/3 hover:cursor-pointer grow">sign in</button>
            <AboutModal />
          </div>
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
