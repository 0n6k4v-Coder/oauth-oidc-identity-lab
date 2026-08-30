const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getProfile() {
  const response = await fetch(`${API_BASE_URL}/api/profile`);

  if (!response.ok) {
    throw new Error(`Resource Server returned ${response.status}`);
  }

  return response.json();
}