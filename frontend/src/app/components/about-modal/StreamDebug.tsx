import { useState, useEffect } from "react";
import DOMPurify from "dompurify";

// THIS MODULE IS EXAMPLE OF STREAMING RESPONSES FROM BACKEND
// NOT INTENDED TO BE USED FOR MORE THAN TESTING

function StreamExample() {
  // Send request, and stream data, both from separate endpoints
  // and display result on the page with delay between chars appearing.
  const [data, setData]: [string | undefined, Function] = useState();
  const [streamData, setStreamData]: [string | null, Function] = useState(null);
  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

  // send request to backend with sample data
  useEffect(() => {
    const fetchData = async () => {
      await sleep(500);

      let responseData = "";
      await fetch("/api")
        .then((response) => response.text())
        .then((json) => {
          responseData = DOMPurify.sanitize(json);
          console.info(responseData);
        })
        .catch((error) => console.error(error));
      let text = "";
      for (let char of responseData) {
        text += char;
        await sleep(30); // delay between chars appearing
        setData(text);
      }
    };

    fetchData();
  }, []);

  // Stream some sample text from backend
  useEffect(() => {
    const streamNumbers = async () => {
      await sleep(1000);

      const response = await fetch("/api/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          chat_text: "Respond in 1 concise sentence, confirming that AI model response stream endpoint is ready.",
        }),
      });
      if (!response.body) {
        console.error("ReadableStream is not available on the response body.");
        return;
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let result = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        for (const char of chunk) {
          result += char;
          await sleep(10); // delay between different chars appearing
          setStreamData(result);
        }
      }
    };
    streamNumbers().catch(console.error);
  }, []);
  return (
    <div>
      {" "}
      <div className="text-slate-200">
        <b>Health check:</b>
        <div>{data || "\u00A0"}</div>
      </div>
      <div className="text-slate-200">
        <strong>Streamed data: </strong> 
        <div>{streamData}</div>
      </div>
    </div>
  );
}

function ButtonForStreaming() {
  // button wrapper around StreamExample - click to stream data from backend
  const [showStream, setShowStream] = useState(false);
  return (
    <div className="m-5 mt-0">
      {showStream && <StreamExample />}
      <button
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        onClick={() => setShowStream(true)}
      >
        Test backend connection
      </button>
    </div>
  );
}


export default ButtonForStreaming;