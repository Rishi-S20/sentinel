import { useUser } from "@stackframe/stack";

export default function DashboardPage() {
  const user = useUser();

  const showToken = async () => {
    if (user) {
      const auth = await user.getAuthJson();
      console.log("ACCESS TOKEN:", auth.accessToken);
      alert(auth.accessToken);
    }
  };

  return (
    <div>
      <button onClick={showToken}>Show Token</button>
    </div>
  );
}
