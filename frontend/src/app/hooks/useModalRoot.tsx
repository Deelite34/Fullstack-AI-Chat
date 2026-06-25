import {useEffect, useState} from "react";


export function useModalRoot() {
    // Handles root div for 'about' modal
    const [modalRoot, setModalRoot] = useState<HTMLElement | null>(null);

    useEffect(() => {
        let root = document.getElementById("modal-root");

        if (!root) {
            root = document.createElement("div")
            root.id = "modal-root";
            root.classList.add("hidden", "-z-9999")
            document.body.appendChild(root);
        }

        setModalRoot(root);

        // cleanup
        return () => {
            if (root && root.childNodes.length === 0) {
                document.body.removeChild(root)
            }
        };
    }, []);
    return modalRoot
}