import { InputWizard } from "@/components/input-wizard";

/**
 * Landing page.
 */
export default function HomePage() {
  return (
    <main className="shell">
      <header className="hero">
        <p className="kicker">Pixii Assessment Build</p>
        <h1>AEO Report Card</h1>
        <p className="muted">
          Diagnose whether GPT, Claude, and Gemini will recommend your Amazon listing for buyer-intent
          queries.
        </p>
      </header>
      <InputWizard />
    </main>
  );
}

