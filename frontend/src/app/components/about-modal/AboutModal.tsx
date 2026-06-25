import { useState } from "react";
import "./debug.css"
import {useModalRoot } from "../../hooks/useModalRoot"
import { createPortal } from "react-dom";
import ButtonForStreaming from "./StreamDebug";

function AboutModal() {
    const [isAboutModalOpen, setIsAboutModalOpen] = useState<boolean>(false);
    const modalRoot = useModalRoot();
    const modalNonFocusBg: HTMLElement | null = document.getElementById("nonfocus-bg");

    function toggleModalClasses(element: HTMLElement | null, stateShow: boolean): void{
        // hide/reveal modal through changing classes
        if (!element) return;
        let classes = [];
        
        !stateShow ? 
          classes.push("z-9999"):
          classes.push("hidden", "-z-9999");

        element.removeAttribute("class")
        for (const cls of classes) {
            element.classList.add(cls)
        }
    }


    const handleToggleModal = () => {
        setIsAboutModalOpen(!isAboutModalOpen);
        // toggle hiding/showing modal
        if(!isAboutModalOpen){
            if (modalNonFocusBg) modalNonFocusBg.style.display = "block";
            toggleModalClasses(modalRoot, isAboutModalOpen)

        } else {
            if (modalNonFocusBg) modalNonFocusBg.style.display = "none";
            toggleModalClasses(modalRoot, isAboutModalOpen);
        }

    }

    if (!modalRoot) return null;

    return (
        <>
            <button className="generic-btn" onClick={handleToggleModal}>About</button>
            {isAboutModalOpen && createPortal(
                <ModalDisplay handleToggleModal={handleToggleModal}/>,
                modalRoot
            )}
        </>
    );
}

function ModalDisplay({handleToggleModal}: { handleToggleModal: () => void }) {
    return (
            <div className="about-modal">
                <h2>About this app</h2>
                <div className="about-modal-content">
                    <p>This is a simple chatbot application, that uses Ollama (Local LLM) to generate responses. It is built with React and Typescript, with a FastAPI backend.</p>
                    <p>It is a learning experience for me, to learn new topics in frontend/full-stack programming.</p>
                    <p>Features AI chat built with React and Typescript, with Ollama (Local LLM) responses streamed from async FastAPI backend. Check README.md for up to date details.</p>
                </div>
                <button onClick={handleToggleModal}>close</button>
            </div>
        
    )
}

export default AboutModal;
