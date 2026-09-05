import { AuthProvider, useAuth } from "./auth";
import AuthScreen from "./components/AuthScreen";
import Feed from "./components/Feed";

function Shell() {
  const { user, loading, logout } = useAuth();

  if (loading) return <div className="center muted">Loading…</div>;
  if (!user) return <AuthScreen />;

  return (
    <div className="app">
      <header className="topbar">
        <span className="brand small">Signal</span>
        <div className="spacer" />
        <span className="muted">{user.email}</span>
        <button className="link" onClick={logout}>
          Log out
        </button>
      </header>
      <main className="content">
        <Feed />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  );
}
