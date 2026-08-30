import { NextResponse } from "next/server";
import { buildAuthorizationUrl } from "@/lib/oauth";

export function GET() {
  const authorizationUrl = buildAuthorizationUrl();

  return NextResponse.redirect(authorizationUrl);
}