import { useState, type FormEvent, type SubmitEventHandler } from "react";
import "./style.css";
import { useModalRoot } from "../../hooks/useModalRoot";
import { createPortal } from "react-dom";
import { toast } from "react-toastify";

function SignUpModal() {
  const [isSignUpModalOpen, setIsSignUpModalOpen] = useState<boolean>(false);
  const modalRoot = useModalRoot();
  const modalNonFocusBg: HTMLElement | null =
    document.getElementById("nonfocus-bg");

  async function handleSignUp(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const form = e.currentTarget;
    const formData = new FormData(form);
    const username = String(formData.get("username") ?? "");
    const email = String(formData.get("email") ?? "");
    const password = String(formData.get("password") ?? "");

    try {
      const response = await fetch("/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Registration failed");
      }
      form.reset();
      handleToggleModal();
      toast.success("Registration succesfull");
      console.info("Registered successfully", data);
    } catch (error) {
      toast.error(`Registration failed: \n${error}`);
      console.error(error);
    }
  }

  // TODO: refactor style.css, so common modal classess can be reused, and specific ones can be added for each modal.
  // Currently, the about and SignUp modals have duplicate code in their respective style.css files.
  function toggleModalClasses(
    element: HTMLElement | null,
    stateShow: boolean,
  ): void {
    // hide/reveal modal through changing classes
    if (!element) return;
    let classes = [];

    !stateShow ? classes.push("z-9999") : classes.push("hidden", "-z-9999");

    element.removeAttribute("class");
    for (const cls of classes) {
      element.classList.add(cls);
    }
  }

  const handleToggleModal = () => {
    setIsSignUpModalOpen(!isSignUpModalOpen);
    // toggle hiding/showing modal
    if (!isSignUpModalOpen) {
      if (modalNonFocusBg) modalNonFocusBg.style.display = "block";
      toggleModalClasses(modalRoot, isSignUpModalOpen);
    } else {
      if (modalNonFocusBg) modalNonFocusBg.style.display = "none";
      toggleModalClasses(modalRoot, isSignUpModalOpen);
    }
  };

  if (!modalRoot) return null;

  return (
    <>
      <button
        className="generic-btn hover:cursor-pointer grow"
        onClick={handleToggleModal}
      >
        Sign up
      </button>
      {isSignUpModalOpen &&
        createPortal(
          <ModalDisplay
            handleToggleModal={handleToggleModal}
            handleSignUp={handleSignUp}
          />,
          modalRoot,
        )}
    </>
  );
}

function ModalDisplay({
  handleToggleModal,
  handleSignUp,
}: {
  handleToggleModal: () => void;
  handleSignUp: SubmitEventHandler<HTMLFormElement>;
}) {
  return (
    <>
      <div className="modal">
        <h2>Sign up</h2>
        <div className="modal-content">
          <p>Please enter your credentials to register.</p>
          <form className="flex flex-col m-2" onSubmit={handleSignUp}>
            <div className="flex flex-row justify-center gap-2 m-5">
              <input name="username" type="text" placeholder="Username" />
              <input name="email" type="email" placeholder="email" />
              <input name="password" type="password" placeholder="Password" />
            </div>
            <button type="submit">Sign up</button>
          </form>
        </div>
        <button className="hover:cursor-pointer" onClick={handleToggleModal}>
          close
        </button>
      </div>
    </>
  );
}

export default SignUpModal;
