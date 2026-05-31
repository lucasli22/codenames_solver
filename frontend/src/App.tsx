import { useState } from "react";

const identityColors: Record<string, string> = {
  red_agent: "#c0392b",
  blue_agent: "#2980b9",
  neutral: "#9e9e9e",
  assassin: "#2c2c2c",
  "": "#f7cba6",
};

type CardState = { word: string; identity: string | null; is_revealed: boolean };

function Square({ card, onChange }: { card: CardState; onChange: (changes: Partial<CardState>) => void }) {
  const bg = identityColors[card.identity ?? ""];
  return (
    <div style={{
      backgroundColor: bg,
      borderRadius: "8px",
      padding: "10px",
      display: "flex",
      flexDirection: "column",
      gap: "6px",
      opacity: card.is_revealed ? 0.4 : 1,
    }}>
      <input
        type="text"
        value={card.word}
        onChange={e => onChange({ word: e.target.value })}
        placeholder="Enter word"
        style={{
          textAlign: "center",
          fontWeight: "bold",
          fontSize: "14px",
          border: "none",
          borderRadius: "4px",
          padding: "4px",
          background: "rgba(255,255,255,0.85)",
          color: "#1a1a1a",
          width: "100%",
          boxSizing: "border-box",
        }}
      />
      <select
        value={card.identity ?? ""}
        onChange={e => onChange({ identity: e.target.value || null })}
        style={{ borderRadius: "4px", padding: "2px", fontSize: "12px" }}
      >
        <option value="">Unknown</option>
        <option value="red_agent">Red Agent</option>
        <option value="blue_agent">Blue Agent</option>
        <option value="neutral">Neutral</option>
        <option value="assassin">Assassin</option>
      </select>
      <label style={{ fontSize: "11px", color: "black", display: "flex", alignItems: "center", gap: "4px" }}>
        <input
          type="checkbox"
          checked={card.is_revealed}
          onChange={e => onChange({ is_revealed: e.target.checked })}
        />
        Revealed
      </label>
    </div>
  );
}

function Board({ role }) {
  const [cards, setCards] = useState(Array(25).fill(null).map(() => ({
    word: "", identity: null, is_revealed: false,
  })));
  const [showWarning, setShowWarning] = useState(false);

  function handleInput(i: number, changes: Partial<typeof cards[0]>) {
    setCards(cards.map((card, index) => index === i ? { ...card, ...changes } : card));
  }

  function handleSubmit() {
    const valid = role === "Spymaster" ? cards.every(card => card.word !== "" && card.identity != null) : 
    cards.every(card => card.word !== "");
    if (valid) {
      setShowWarning(false);
      if (role === "Spymaster") {
      } else if (role === "Operative") {
      }
    } else {
      setShowWarning(true);
    }
  }

  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "10px", padding: "16px" }}>
        {cards.map((card, i) => (
          <Square key={i} card={card} onChange={(changes) => handleInput(i, changes)} />
        ))}
      </div>
      {showWarning && <p style={{ color: "red", textAlign: "center" }}>Please fill in all words and identities.</p>}
      <div style={{ textAlign: "center", marginTop: "12px" }}>
        <button onClick={handleSubmit} style={{ padding: "10px 24px", fontSize: "16px", borderRadius: "6px", cursor: "pointer" }}>
          {role === "Spymaster" ? "Find Clue" : "Find Best Guess"}
        </button>
      </div>
    </>
  );
}

function App() {
  const [role, setRole] = useState<"Spymaster" | "Operative" | null>(null);

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ textAlign: "center", marginTop: "24px" }}>
        <h1 style={{ textAlign: "center" }}>CODENAMES SOLVER</h1>
        <p>Select your role:</p>
        <button onClick={() => setRole("Spymaster")} style={{ marginRight: "8px", padding: "8px 20px", borderRadius: "6px", cursor: "pointer" }}>
          Spymaster
        </button>
        <button onClick={() => setRole("Operative")} style={{ padding: "8px 20px", borderRadius: "6px", cursor: "pointer" }}>
          Operative
        </button>
        {role && <p style={{ marginTop: "8px" }}>Current role: <strong>{role}</strong></p>}
      </div>
      
      <Board role={role} />

    </div>
  );
}

export default App;