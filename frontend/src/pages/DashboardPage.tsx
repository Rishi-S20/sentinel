import { useUser } from "@stackframe/stack";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "@/api/client";
import NavBar from "@/components/NavBar";

interface Agent {
  id: string;
  name: string;
  status: string;
  created_at: string;
}

export default function DashboardPage() {
  const user = useUser();
  const navigate = useNavigate();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [agentName, setAgentName] = useState("");
  const [symbol, setSymbol] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (user === null) {
      navigate("/sign-in");
    }
  }, [user, navigate]);

  useEffect(() => {
    if (!user) return;
    user
      .getAuthJson()
      .then((auth) => {
        api.setToken(auth.accessToken);
        return api.get<Agent[]>("/agents");
      })
      .then((res) => {
        setAgents(res);
        setLoading(false);
      });
  }, [user]);

  const createAgent = async () => {
    if (!agentName || !symbol) return;
    setCreating(true);
    const auth = await user!.getAuthJson();
    api.setToken(auth.accessToken);
    await api.post("/agents", {
      name: agentName,
      asset_symbols: [symbol.toUpperCase()],
    });
    const res = await api.get<Agent[]>("/agents");
    setAgents(res);
    setAgentName("");
    setSymbol("");
    setCreating(false);
  };

  if (!user || loading) return <div className="p-8 text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-surface-950 text-white p-8">
      <div className="min-h-screen bg-surface-950 text-white">
        <NavBar />
        <div className="p-8">{/* existing content */}</div>
      </div>
      <h1 className="text-2xl font-bold mb-6">My Agents</h1>

      {/* Create agent form */}
      <div className="flex gap-3 mb-8">
        <input
          className="bg-surface-800 border border-surface-700 rounded px-3 py-2 text-sm"
          placeholder="Agent name"
          value={agentName}
          onChange={(e) => setAgentName(e.target.value)}
        />
        <input
          className="bg-surface-800 border border-surface-700 rounded px-3 py-2 text-sm w-28"
          placeholder="Symbol (e.g. AAPL)"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
        />
        <button
          className="bg-brand-600 hover:bg-brand-700 px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
          onClick={createAgent}
          disabled={creating}
        >
          {creating ? "Creating..." : "Create Agent"}
        </button>
      </div>

      {/* Agent list */}
      {agents.length === 0 ? (
        <p className="text-surface-400">No agents yet. Create one above.</p>
      ) : (
        <div className="grid gap-4">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="bg-surface-800 border border-surface-700 rounded-lg p-4 cursor-pointer hover:border-brand-500"
              onClick={() => navigate(`/agents/${agent.id}`)}
            >
              <div className="flex justify-between items-center">
                <h2 className="font-semibold">{agent.name}</h2>
                <span
                  className={`text-xs px-2 py-1 rounded-full ${agent.status === "active" ? "bg-bullish/20 text-bullish" : "bg-surface-700 text-surface-400"}`}
                >
                  {agent.status}
                </span>
              </div>
              <p className="text-surface-400 text-sm mt-1">
                Created {new Date(agent.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
