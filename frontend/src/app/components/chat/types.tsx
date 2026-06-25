import type { Dispatch, SetStateAction } from "react";


export type ChatMessage = {
  id: string;
  author: "user" | "bot";
  msg: string;
  streaming?: boolean;
};

type UserMessage = {
  msg: string;
};

export type ChatResponsesProps = {
  chatMsgs: ChatMessage[];
  setChatMsgs: Dispatch<SetStateAction<ChatMessage[]>>;
  userMessage: UserMessage | null;
  onStreamComplete?: (chatMsgs: ChatMessage[]) => void;
};

export type ChatInputProps = {
  setShowChatResponses: React.Dispatch<React.SetStateAction<boolean>>;
  setChatMsgs: React.Dispatch<React.SetStateAction<Array<ChatMessage>>>;
  setLatestUserMessage: React.Dispatch<React.SetStateAction<ChatMessage | null>>;
};


export type ChatOutputProps = {
  showChatResponses: boolean;
  chatMsgs: ChatMessage[];
  setChatMsgs: Dispatch<SetStateAction<ChatMessage[]>>;
  latestUserMessage: ChatMessage | null;
  onStreamComplete?: (chatMsgs: ChatMessage[]) => void;
}