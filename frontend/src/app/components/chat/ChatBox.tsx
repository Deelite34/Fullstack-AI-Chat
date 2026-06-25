import "./ChatBox.css";
import { useState, type RefObject } from "react";
import type { ChatMessage } from "./types.tsx";
import { ChatInput } from "./ChatInput.tsx";
import { ChatOutput } from "./ChatOutput.tsx";


function ConversationChatBox() {
  // Chatbox input and output component
  const [showChatResponses, setShowChatResponses] = useState<boolean>(false);
  const [chatMsgs, setChatMsgs] = useState<Array<ChatMessage>>([]);
  const [latestUserMessage, setLatestUserMessage] = useState<ChatMessage | null>(null);

  const handleStreamComplete = (finalChatMsgs: ChatMessage[]) => {
    console.log("Stream finished, final chat history:", finalChatMsgs);
    // persist finalChatMsgs here in the future
  };

  return (
    <div className="chatbox flex flex-col shrink-0 border-4 border-slate-600 h-[68vh]">
      <ChatOutput
        showChatResponses={showChatResponses}
        chatMsgs={chatMsgs}
        setChatMsgs={setChatMsgs}
        latestUserMessage={latestUserMessage}
        onStreamComplete={handleStreamComplete}
      />
      
      <ChatInput
        setShowChatResponses={setShowChatResponses}
        setChatMsgs={setChatMsgs}
        setLatestUserMessage={setLatestUserMessage}
      />
    </div>
  );
}

export default ConversationChatBox;
