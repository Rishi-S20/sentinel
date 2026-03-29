import { useUser } from "@stackframe/stack";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import api from "@/api/client";
import NavBar from "@/components/NavBar";

interface Briefing {
  id: string;
  content_md: string;
  created_at: string;
}

export default function BriefingsPage() {
  const { id } = useParams<{ id: string }>();
  const user = useUser();
  const navigate = useNavigate();
  const [briefings, setBriefings] = useState<Briefing[]>([]);
  const [selected, setSelected] = useState<Briefing | null>(null);
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
        return api.get<Briefing[]>(`/agents/${id}/briefings`);
      })
      .then((res) => {
        setBriefings(res);
        if (res.length > 0) setSelected(res[0]);
        setLoading(false);
      });
  }, [user, id]);

  if (!user || loading) return <div className="p-8 text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-surface-950 text-white">
      <NavBar />
      <div className="flex h-[calc(100vh-57px)]">
        {/* Sidebar — briefing list */}
        <div className="w-64 border-r border-surface-800 p-4 overflow-y-auto shrink-0">
          <button
            className="text-surface-400 hover:text-white text-sm mb-4 block"
            onClick={() => navigate(`/agents/${id}`)}
          >
            ← Back to agent
          </button>
          <h2 className="text-sm font-semibold text-surface-400 mb-3">
            Briefings
          </h2>
          {briefings.length === 0 ? (
            <p className="text-surface-500 text-xs">No briefings yet.</p>
          ) : (
            <div className="grid gap-2">
              {briefings.map((b) => (
                <button
                  key={b.id}
                  className={`text-left text-sm px-3 py-2 rounded ${selected?.id === b.id ? "bg-surface-700 text-white" : "text-surface-400 hover:text-white hover:bg-surface-800"}`}
                  onClick={() => setSelected(b)}
                >
                  {new Date(b.created_at).toLocaleDateString()}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Main — briefing content */}
        <div className="flex-1 p-8 overflow-y-auto">
          {selected ? (
            <div className="prose prose-invert max-w-3xl">
              <ReactMarkdown>{selected.content_md}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-surface-400">Select a briefing from the left.</p>
          )}
        </div>
      </div>
    </div>
  );
}
