import { useUser } from "@stackframe/stack";
import { useNavigate } from "react-router-dom";
import api from "@/api/client";

export default function NavBar() {
  const user = useUser();
  const navigate = useNavigate();

  const logout = async () => {
    await user?.signOut();
    navigate("/sign-in");
  };

  return (
    <nav className="bg-surface-900 border-b border-surface-800 px-8 py-4 flex justify-between items-center">
      <span
        className="text-brand-400 font-bold text-lg cursor-pointer"
        onClick={() => navigate("/")}
      >
        Sentinel
      </span>
      <div className="flex items-center gap-4">
        <span className="text-surface-400 text-sm">{user?.primaryEmail}</span>
        <button
          className="text-sm text-surface-400 hover:text-white"
          onClick={logout}
        >
          Sign out
        </button>
      </div>
    </nav>
  );
}
