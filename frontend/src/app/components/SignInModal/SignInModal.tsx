import { useState } from "react";
import "./style.css"
import {useModalRoot } from "../../hooks/useModalRoot"
import { createPortal } from "react-dom";

function SignInModal() {
    const [isLogInModalOpen, setIsLogInModalOpen] = useState<boolean>(false);
    const modalRoot = useModalRoot();
    const modalNonFocusBg: HTMLElement | null = document.getElementById("nonfocus-bg");

    // TODO: refactor style.css, so common modal classess can be reused, and specific ones can be added for each modal. 
    // Currently, the about and login modals have duplicate code in their respective style.css files.
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
        setIsLogInModalOpen(!isLogInModalOpen);
        // toggle hiding/showing modal
        if(!isLogInModalOpen){
            if (modalNonFocusBg) modalNonFocusBg.style.display = "block";
            toggleModalClasses(modalRoot, isLogInModalOpen)

        } else {
            if (modalNonFocusBg) modalNonFocusBg.style.display = "none";
            toggleModalClasses(modalRoot, isLogInModalOpen);
        }

    }

    if (!modalRoot) return null;

    return (
        <>
            <button className="generic-btn hover:cursor-pointer grow" onClick={handleToggleModal}>Sign in</button>
            {isLogInModalOpen && createPortal(
                <ModalDisplay handleToggleModal={handleToggleModal}/>,
                modalRoot
            )}
        </>
    );
}

function ModalDisplay({handleToggleModal}: { handleToggleModal: () => void }) {
    return (
            <div className="modal">
                <h2>Sign in PLACEHOLDER</h2>
                <div className="modal-content">
                    <p>Please enter your credentials to sign in.</p>
                    <form className="flex flex-col m-2">
                        <div className="flex flex-row justify-center gap-2 m-5">
                            <input type="text" placeholder="Username" />
                            <input type="password" placeholder="Password" />
                        </div>
                        <button type="submit">Sign in</button>
                    </form>
                
                </div>
                <button className="hover:cursor-pointer" onClick={handleToggleModal}>close</button>
            </div>
        
    )
}

export default SignInModal;
