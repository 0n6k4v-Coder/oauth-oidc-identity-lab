import { buildAuthorizationUrl } from "./api/authorization";

function App() {
  function startAuthorization(): void {
    window.location.href = buildAuthorizationUrl();
  }

  return (
    <main>
      <h1>OAuth 2.0 Authorization Request Lab</h1>

      <p>Client Type: Public Client</p>

      <button type="button" onClick={startAuthorization}>
        Start Authorization Request
      </button>
    </main>
  );
}

export default App;