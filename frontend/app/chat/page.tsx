import Chat from "@/components/Chat";
import Link from "next/link";

export default function ChatPage() {
  return (
    <>
      <div className="chat-bar">
        <Link href="/" className="chat-back">
          ← 홈
        </Link>
      </div>
      <Chat />
    </>
  );
}
