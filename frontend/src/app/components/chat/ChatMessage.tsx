import "./ChatBox.css";
import { useEffect, useRef } from "react";
import { makeId } from "./common.tsx";
import type { ChatResponsesProps, ChatMessage } from "./types.tsx";
import { getAccessToken, refreshAccessToken } from "../../Services/api";

async function requestChatStream(chatText: string, signal: AbortSignal) {
  let token = getAccessToken();
  if (!token) {
    throw new Error("Please log in to send a message.");
  }

  const sendRequest = (accessToken: string) =>
    fetch("/api/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ chat_text: chatText }),
      signal,
    });

  let response = await sendRequest(token);
  if (response.status === 401) {
    token = await refreshAccessToken();
    response = await sendRequest(token);
  }
  if (!response.ok) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }
  if (!response.body) {
    throw new Error("No response from backend stream endpoint.");
  }
  return response.body;
}

export function ChatResponses({
  chatMsgs,
  setChatMsgs,
  userMessage,
  onStreamComplete,
}: ChatResponsesProps) {
  // Handles displaying all chatbox response messages and streaming new responses
  const tempBotIdRef = useRef<string | null>(null);
  const latestChatMsgsRef = useRef<ChatMessage[]>(chatMsgs);
  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

  useEffect(() => {
    latestChatMsgsRef.current = chatMsgs;
  }, [chatMsgs]);

  useEffect(() => {
    if (!userMessage) return;

    const controller = new AbortController();
    const { signal } = controller;
    const finishedRef = { current: false }; // whether this stream finished successfully

    const botId = makeId("bot");
    tempBotIdRef.current = botId;

    // Insert placeholder bot message immediately so streaming is visible even for the first message
    setChatMsgs((prev) => [
      ...prev,
      { id: botId, author: "bot", msg: "", streaming: true },
    ]);

    const streamNumbers = async () => {
      await sleep(30); // tiny delay for UX

      try {
        const stream = await requestChatStream(userMessage.msg, signal);
        const reader = stream.getReader();
        const decoder = new TextDecoder();
        let result = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done || signal.aborted) {
            console.log(latestChatMsgsRef.current);
            break;
          }
          const chunk = decoder.decode(value, { stream: true });
          console.log(`received chunk: ${chunk}`);
          for (const char of chunk) {
            result += char;
            // update the placeholder message in-place for live streaming effect
            setChatMsgs((prev) =>
              prev.map((m) => (m.id === botId ? { ...m, msg: result } : m)),
            );
            await sleep(30);
          }
        }

        // finalize placeholder (remove streaming flag) and mark finished
        if (!signal.aborted) {
          setChatMsgs((prev) => {
            const next = prev.map((m) =>
              m.id === botId ? { ...m, streaming: false } : m,
            );
            latestChatMsgsRef.current = next;
            onStreamComplete?.(next);
            return next;
          });
          finishedRef.current = true;
        }
      } catch (err: any) {
        // err is unknown in TS; narrow safely
        if (err?.name !== "AbortError") console.error(err);
        // on error/abort remove the placeholder to avoid orphaned/duplicated messages
        setChatMsgs((prev) => prev.filter((m) => m.id !== botId));
      }
    };

    streamNumbers();

    return () => {
      controller.abort();
      // only remove placeholder if the stream did NOT finish (was aborted/incomplete)
      if (!finishedRef.current) {
        setChatMsgs((prev) => prev.filter((m) => m.id !== botId));
      }
    };
  }, [userMessage, setChatMsgs]);

  return (
    <div className="w-full h-full overflow-auto">
      <div className="chatbox-msg-container flex flex-col gap-3">
        {chatMsgs.map((msg) => (
          <div
            key={msg.id}
            className={
              msg.author === "user"
                ? "chatbox-msg chatbox-output-user-msg text-slate-200 whitespace-pre-wrap overflow-x-hidden wrap-break-word"
                : "chatbox-msg chatbox-output-bot-msg text-slate-200 whitespace-pre-wrap overflow-x-hidden wrap-break-word"
            }
          >
            {msg.author === "user" ? "You: " : "Bot: "}
            <span className="whitespace-pre-wrap">
              {msg.msg ? msg.msg : "..."}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
