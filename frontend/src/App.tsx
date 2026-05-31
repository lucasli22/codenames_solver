import { useState, useEffect } from "react";
import { api } from "./api";

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

function Board({ role, colour, firstTeam }) {
  const [cards, setCards] = useState(Array(25).fill(null).map(() => ({
    word: "", identity: null, is_revealed: false,
  })));
  const [showWarning, setShowWarning] = useState(false);
  const [game, setGame] = useState(null);
  const [redHints, setRedHints] = useState<{clue: string, num: number}[]>([]);
  const [blueHints, setBlueHints] = useState<{clue: string, num: number}[]>([]);
  const [clueInput, setClueInput] = useState("");
  const [numInput, setNumInput] = useState(1);
  const [currentTurn, setCurrentTurn] = useState<"Red" | "Blue" | null>(null);

  useEffect(() => {
    setCurrentTurn(firstTeam);
  }, [firstTeam]);

  function addHint() {
    const hint = { clue: clueInput, num: numInput };
    if (!clueInput) return;
    if (!(/^[a-zA-Z]+$/.test(clueInput))) return;
    
    if (currentTurn == "Red") {
      setRedHints([...redHints, hint]);
    } else {
      setBlueHints([...blueHints, hint]);
    }

    setClueInput("");
    setCurrentTurn(currentTurn === "Red" ? "Blue" : "Red");
  }


  function handleInput(i: number, changes: Partial<typeof cards[0]>) {
    setCards(cards.map((card, index) => index === i ? { ...card, ...changes } : card));
  }

  async function handleSubmit() {
    const valid = role === "Spymaster" ? cards.every(card => card.word !== "" && card.identity != null) : 
    cards.every(card => card.word !== "");

    if (valid) {
      setShowWarning(false);
      if (role === "Spymaster") {
        const newGame = await api.createSpymasterGame(cards);
        if (colour === "Red") {
          newGame.game_state = "red_spymaster";
        } else {
          newGame.game_state = "blue_spymaster";
        }
        setGame(newGame);
        const result = await api.scoreSpymaster(newGame);
        console.log(result);

      } else if (role === "Operative") {
        const first_team = firstTeam === "Red" ? "red_spymaster" : "blue_spymaster";
        const newGame = await api.createOperativeGame(cards.map(card => card.word), first_team, redHints, blueHints);
        if (colour === "Red") {
          newGame.game_state = "red_operative";
        } else {
          newGame.game_state = "blue_operative";
        }
        setGame(newGame);
        const result = await api.scoreOperative(newGame);
        console.log(result);
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
      {role === "Operative" && (
        <div style={{ textAlign: "center", marginTop: "16px" }}>
          <p>Current turn: <strong style={{ color: currentTurn === "Red" ? "#c0392b" : "#2980b9" }}>{currentTurn}</strong></p>
          <input
            type="text"
            value={clueInput}
            onChange={e => setClueInput(e.target.value)}
            placeholder="Enter hint"
            style={{ marginRight: "8px", padding: "6px", borderRadius: "4px" }}
          />
          <input
            type="number"
            value={numInput}
            min={1}
            max={13}
            onChange={e => setNumInput(Number(e.target.value))}
            style={{ width: "60px", marginRight: "8px", padding: "6px", borderRadius: "4px" }}
          />
          <button onClick={addHint} style={{ padding: "6px 16px", borderRadius: "4px", cursor: "pointer" }}>
            Add Hint
          </button>
          <div style={{ marginTop: "8px" }}>
            <strong>Red hints:</strong> {redHints.map(h => `${h.clue} (${h.num})`).join(", ")}
          </div>
          <div>
            <strong>Blue hints:</strong> {blueHints.map(h => `${h.clue} (${h.num})`).join(", ")}
          </div>
        </div>
      )}
      {showWarning && <p style={{ color: "red", textAlign: "center" }}>Please fill in all cards.</p>}
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
  const [colour, setColour] = useState<"Red" | "Blue" | null>(null);
  const [firstTeam, setFirstTeam] = useState<"Red" | "Blue" | null>(null);
  return (
    <div style={{ padding: "20px" }}>
      <div style={{ textAlign: "center", marginTop: "24px" }}>
        <h1 style={{ textAlign: "center" }}>CODENAMES SOLVER</h1>
        <p>Select your role:</p>
        <button onClick={() => setRole("Spymaster")} style={{ marginRight: "8px", padding: "8px 20px", borderRadius: "6px", cursor: "pointer", backgroundColor: role === "Spymaster" ? "#333333" : "", color: role === "Spymaster" ? "white" : "" }}>
          Spymaster
        </button>
        <button onClick={() => setRole("Operative")} style={{ padding: "8px 20px", borderRadius: "6px", cursor: "pointer", backgroundColor: role === "Operative" ? "#333333" : "", color: role === "Operative" ? "white" : "" }}>
          Operative
        </button>
        <p>Select your colour:</p>
        <button onClick={() => setColour("Red")} style={{ marginRight: "8px", padding: "8px 20px", borderRadius: "6px", cursor: "pointer", backgroundColor: colour === "Red" ? "#c0392b" : "", color: colour === "Red" ? "white" : "" }}>
          Red
        </button>
        <button onClick={() => setColour("Blue")} style={{ marginRight: "8px", padding: "8px 20px", borderRadius: "6px", cursor: "pointer", backgroundColor: colour === "Blue" ? "#2980b9" : "", color: colour === "Blue" ? "white" : "" }}>
          Blue
        </button>
        <p>Select the colour that starts:</p>
        <button onClick={() => setFirstTeam("Red")} style={{ marginRight: "8px", padding: "8px 20px", borderRadius: "6px", cursor: "pointer", backgroundColor: firstTeam === "Red" ? "#c0392b" : "", color: firstTeam === "Red" ? "white" : "" }}>
          Red
        </button>
        <button onClick={() => setFirstTeam("Blue")} style={{ marginRight: "8px", padding: "8px 20px", borderRadius: "6px", cursor: "pointer", backgroundColor: firstTeam === "Blue" ? "#2980b9" : "", color: firstTeam === "Blue" ? "white" : "" }}>
          Blue
        </button>
        {role && <p style={{ marginTop: "8px" }}>Current role: <strong>{colour}</strong> <strong>{role}</strong></p>}
      </div>
      
      <Board role={role} colour={colour} firstTeam={firstTeam}/>

    </div>
  );
}

export default App;