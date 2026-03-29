import { useUser } from "@stackframe/stack";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "@/api/client";

interface KeyFactor {
  factor: string;
  signal: "bullish" | "bearish" | "neutral";
  weight: number;
}

interface Belief {
  id: string;
  asset_id: string;
  conviction: number;
  thesis: string;
  key_factors: KeyFactor[];
  created_at: string;
}

export default function AgentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const user = useUser();
  const navigate = useNavigate();
  const [beliefs, setBeliefs] = useState<Belief[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user === null) navigate("/sign-in");
  }, [user, navigate]);

  useEffect(() => {
    if (!user || !id) return;
    user
      .getAuthJson()
      .then((auth) => {
        api.setToken(auth.accessToken);
        return api.get<Belief[]>(`/agents/${id}/beliefs`);
      })
      .then((res) => {
        setBeliefs(res);
        setLoading(false);
      });
  }, [user, id]);

  if (!user || loading) return <div className="p-8 text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-surface-950 text-white p-8">
      <button
        className="text-surface-400 hover:text-white text-sm mb-6"
        onClick={() => navigate("/")}
      >
        ← Back to agents
      </button>

      <h1 className="text-2xl font-bold mb-6">Belief History</h1>

      {beliefs.length === 0 ? (
        <p className="text-surface-400">
          No beliefs yet — run the agent first.
        </p>
      ) : (
        <div className="grid gap-6">
          {beliefs.map((b) => (
            <div
              key={b.id}
              className="bg-surface-800 border border-surface-700 rounded-lg p-5"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <span className="text-lg font-semibold">{b.asset_id}</span>
                  <span className="text-surface-400 text-sm ml-3">
                    {new Date(b.created_at).toLocaleString()}
                  </span>
                </div>
                <div
                  className={`text-xl font-bold ${
                    b.conviction >= 0.6
                      ? "text-bullish"
                      : b.conviction <= 0.4
                        ? "text-bearish"
                        : "text-neutral"
                  }`}
                >
                  {Math.round(b.conviction * 100)}%
                </div>
              </div>

              <p className="text-surface-300 text-sm mb-4">{b.thesis}</p>

              {b.key_factors?.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {b.key_factors.map((f, i) => (
                    <span
                      key={i}
                      className={`text-xs px-2 py-1 rounded-full ${
                        f.signal === "bullish"
                          ? "bg-bullish/20 text-bullish"
                          : f.signal === "bearish"
                            ? "bg-bearish/20 text-bearish"
                            : "bg-neutral/20 text-neutral"
                      }`}
                    >
                      {f.factor}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
