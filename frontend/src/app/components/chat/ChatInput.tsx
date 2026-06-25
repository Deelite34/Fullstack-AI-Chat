import type { ChatInputProps, ChatMessage } from "./types";
import { makeId } from "./common";
import { useState } from "react";


export function ChatInput(props: ChatInputProps) {
  // Component with chat text input and button to sent it
  const { setShowChatResponses, setChatMsgs, setLatestUserMessage } = props;
  const [inputValue, setInputValue] = useState("");
  
  const handleSubmit = (event: React.SubmitEvent<HTMLFormElement>) => {
    // handle form submit event for chat input
    event.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed) return;

    const newMsg: ChatMessage = { id: makeId("user"), author: "user", msg: trimmed };
    setChatMsgs((prev) => [...prev, newMsg]);
    setLatestUserMessage(newMsg);
    setShowChatResponses(true);
    setInputValue("");
  };

  function handleFormCtrlEnter(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    // send chat input if we press ctrl+enter while focus is in input box
    if(event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        handleSubmit(event as unknown as React.SubmitEvent<HTMLFormElement>);
    }
  }
  
  return (
    <div className="w-full sm:min-w-68 min-w-0 flex items-center py-2 flex-row mt-0 min-h-[20%] bg-slate-800 text-slate-200">
      <form id="chat-input" onSubmit={handleSubmit} className="input-container flex flex-row justify-between w-full items-center px-8" action="">
        <textarea
          className="bg-slate-900 text-slate-400 text-wrap p-2 resize-none input w-full rounded-xl field-sizing-content overflow-y-scroll h-24 max-h-24"
          autoFocus={true}
          id="chatbox_input"
          name="chatbox_input"
          placeholder="Ask chatbot!"
          wrap="soft"
          rows={4}
          value={inputValue}
          onChange={(e)=>setInputValue(e.target.value)}
          onKeyDown={handleFormCtrlEnter}
        />
        <button
          className="cursor-pointer chat-send-msg-btn w-16 h-16 p-2 border-4 border-slate-600 bg-slate-600 rounded-3xl"
          type="submit"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 20.25c4.97 0 9-3.694 9-8.25s-4.03-8.25-9-8.25S3 7.444 3 12c0 2.104.859 4.023 2.273 5.48.432.447.74 1.04.586 1.641a4.483 4.483 0 0 1-.923 1.785A5.969 5.969 0 0 0 6 21c1.282 0 2.47-.402 3.445-1.087.81.22 1.668.337 2.555.337Z"
            />
          </svg>
        </button>
      </form>
    </div>
  )
}