import { ChatResponses } from "./ChatMessage";
import type { ChatOutputProps } from "./types";


export function ChatOutput(props: ChatOutputProps) {
  // wrapper around chat output message list inside chatbox
  const { showChatResponses, chatMsgs, setChatMsgs, latestUserMessage, onStreamComplete } = props;
  return (
      <div className="w-full sm:min-w-68 min-w-0 flex flex-col items-center mb-0 justify-center h-[80%] p-8 bg-slate-800 text-slate-200 border-slate-600 border-b-2  rounded-t-md">
        <div
          className="bg-slate-900 text-slate-400 input w-full h-full rounded-xl py-6 overflow-auto"
          id="chatbox_output"
        >
          {showChatResponses ? (
            <ChatResponses
              chatMsgs={chatMsgs}
              setChatMsgs={setChatMsgs}
              userMessage={latestUserMessage}
              onStreamComplete={onStreamComplete}
            />
          ) : (
            "Send your message and ChatBot will respond."
          )}
        </div>
      </div>
  )
}
