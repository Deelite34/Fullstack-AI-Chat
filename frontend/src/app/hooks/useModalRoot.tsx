import { useEffect, useState } from "react";

export function useModalRoot() {
  // Handles root div for modal. Intended for one modal open at once, may not support multiple modals at once.
  const [modalRoot, setModalRoot] = useState<HTMLElement | null>(null);

  useEffect(() => {
    let root = document.getElementById("modal-root");
    // Prevent other modals from doing duplicate clean up (and causing errors) when they also use useModalRoot
    // by keeping track of whether this hook created the root or not
    let rootCreated = false;
    if (!root) {
      root = document.createElement("div");
      root.id = "modal-root";
      root.classList.add("hidden", "-z-9999");
      document.body.appendChild(root);
      rootCreated = true;
    }

    setModalRoot(root);

    // cleanup
    return () => {
      if (rootCreated && root && root.childNodes.length === 0) {
        document.body.removeChild(root);
      }
    };
  }, []);
  return modalRoot;
}
