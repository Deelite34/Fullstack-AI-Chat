import { useEffect, useState } from "react";

export function useModalRoot() {
  // Handles root div for modal. Intended for one modal open at once, may not support multiple modals at once.
  const [modalRoot, setModalRoot] = useState<HTMLElement | null>(null);

  useEffect(() => {
    let root = document.getElementById("modal-root");
    if (!root) {
      root = document.createElement("div");
      root.id = "modal-root";
      root.classList.add("hidden", "-z-9999");
      document.body.appendChild(root);
    }

    setModalRoot(root);
  }, []);
  return modalRoot;
}
