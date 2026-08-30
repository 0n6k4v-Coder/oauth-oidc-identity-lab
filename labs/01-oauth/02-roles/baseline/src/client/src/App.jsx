import { useEffect, useState } from "react";
import { getProfile } from "./api/profile";

function App() {
  const [profile, setProfile] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;

    async function loadProfile() {
      try {
        const data = await getProfile();

        if (!ignore) {
          setProfile(data);
          setStatus("success");
        }
      } catch (err) {
        if (!ignore) {
          setError(
            err instanceof Error ? err.message : "Unknown error",
          );
          setStatus("error");
        }
      }
    }

    loadProfile();

    return () => {
      ignore = true;
    };
  }, []);

  return (
    <main>
      <h1>OAuth 2.0 Identity Lab</h1>
      <p>Role: OAuth Client</p>

      {status === "loading" && (
        <p>Loading protected resource...</p>
      )}

      {status === "error" && (
        <p role="alert">
          Failed to load resource: {error}
        </p>
      )}

      {status === "success" && profile && (
        <section>
          <h2>Resource Server Response</h2>

          <dl>
            <dt>ID</dt>
            <dd>{profile.id}</dd>

            <dt>Display Name</dt>
            <dd>{profile.display_name}</dd>

            <dt>Resource</dt>
            <dd>{profile.resource}</dd>
          </dl>
        </section>
      )}
    </main>
  );
}

export default App;