import { describe, expect, it } from "vitest";

import { buildAuthorizationUrl } from "./authorization";

describe("buildAuthorizationUrl", () => {
  it("builds the minimal OAuth authorization request", () => {
    const url = new URL(buildAuthorizationUrl());

    expect(url.origin).toBe("http://localhost:8500");

    expect(url.pathname).toBe("/authorize");

    expect(url.searchParams.get("response_type")).toBe(
      "code",
    );

    expect(url.searchParams.get("client_id")).toBe(
      "public-client",
    );

    expect(url.searchParams.get("redirect_uri")).toBe(
      "http://localhost:5473/callback",
    );

    expect(url.searchParams.get("scope")).toBe("read");

    expect(
      url.searchParams.has("state"),
    ).toBe(false);

    expect(
      url.searchParams.has("code_challenge"),
    ).toBe(false);

    expect(
      url.searchParams.has("client_secret"),
    ).toBe(false);
  });
});