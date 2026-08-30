const AUTHORIZATION_ENDPOINT =
  "http://localhost:8500/authorize";

const CLIENT_ID = "public-client";

const REDIRECT_URI =
  "http://localhost:5473/callback";

const SCOPE = "read";

export function buildAuthorizationUrl(): string {
  const url = new URL(AUTHORIZATION_ENDPOINT);

  url.searchParams.set("response_type", "code");
  url.searchParams.set("client_id", CLIENT_ID);
  url.searchParams.set("redirect_uri", REDIRECT_URI);
  url.searchParams.set("scope", SCOPE);

  return url.toString();
}