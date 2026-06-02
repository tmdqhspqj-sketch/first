import Link from "next/link";

const features = [
  {
    title: "Gemma 4 로컬 추론",
    desc: "Ollama로 PC에서 실행. RTX 4060에 맞춘 멀티모달 에이전트.",
  },
  {
    title: "RAG 검색",
    desc: "문서를 임베딩해 관련 내용만 골라 답변합니다.",
  },
  {
    title: "비전 · 툴",
    desc: "이미지 질의와 함수 호출을 LangGraph로 오케스트레이션.",
  },
];

export default function Landing() {
  return (
    <div className="landing">
      <header className="landing-header">
        <span className="logo">First Agent</span>
        <nav>
          <a href="#features">기능</a>
          <Link href="/chat" className="nav-cta">
            채팅 시작
          </Link>
        </nav>
      </header>

      <section className="hero">
        <p className="eyebrow">로컬 LLM · Ollama · Next.js</p>
        <h1>
          내 PC에서 돌아가는
          <br />
          <span className="gradient">AI 에이전트</span>
        </h1>
        <p className="hero-sub">
          Gemma 4, RAG, 비전, 툴 호출을 한 화면에서. 데이터는 내 장치에 남습니다.
        </p>
        <div className="hero-actions">
          <Link href="/chat" className="btn primary">
            지금 채팅하기
          </Link>
          <a
            href="https://github.com/tmdqhspqj-sketch/first"
            className="btn ghost"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </div>
      </section>

      <section id="features" className="features">
        {features.map((f) => (
          <article key={f.title} className="feature-card">
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </article>
        ))}
      </section>

      <footer className="landing-footer">
        <p>FastAPI · LangGraph · FastMCP · ChromaDB</p>
        <Link href="/chat">앱 열기 →</Link>
      </footer>
    </div>
  );
}
