const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type Persona = {
  id: string;
  name: string;
  description?: string;
};

export type ModelConfig = {
  id: string;
  name: string;
  ollama_model?: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatResult = {
  answer: string;
  retrieved: { content: string; metadata?: Record<string, string> }[];
  tool_name?: string;
  tool_result?: string;
};

export async function fetchHealth() {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}

export async function fetchPersonas(): Promise<Persona[]> {
  const res = await fetch(`${API_URL}/v1/personas`);
  const data = await res.json();
  return data.personas ?? [];
}

export async function fetchModels(): Promise<ModelConfig[]> {
  const res = await fetch(`${API_URL}/v1/models`);
  const data = await res.json();
  return data.models ?? [];
}

export async function sendChat(params: {
  message: string;
  history: ChatMessage[];
  persona_id: string;
  model_id: string;
  use_rag: boolean;
  use_tools: boolean;
  stream: boolean;
  images_base64?: string[];
  onToken?: (chunk: string) => void;
}): Promise<ChatResult> {
  const res = await fetch(`${API_URL}/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: params.message,
      history: params.history,
      persona_id: params.persona_id,
      model_id: params.model_id,
      use_rag: params.use_rag,
      use_tools: params.use_tools,
      stream: params.stream,
      images_base64: params.images_base64 ?? [],
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Chat failed (${res.status})`);
  }

  if (!params.stream) {
    return res.json();
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let answer = "";
  let meta: ChatResult = { answer: "", retrieved: [] };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const text = decoder.decode(value, { stream: true });
    for (const line of text.split("\n")) {
      if (!line.startsWith("data: ")) continue;
      try {
        const payload = JSON.parse(line.slice(6));
        if (payload.type === "token") {
          answer += payload.content;
          params.onToken?.(payload.content);
        } else if (payload.type === "done") {
          meta = {
            answer,
            retrieved: payload.retrieved ?? [],
            tool_name: payload.tool_name,
            tool_result: payload.tool_result,
          };
        }
      } catch {
        /* ignore partial JSON */
      }
    }
  }

  return { ...meta, answer };
}
