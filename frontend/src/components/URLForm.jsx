import { useState } from "react";
import { API_BASE_URL } from "../config";

function URLForm({ onShorten}) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");


async function handleSubmit() {
  setError("");

  let parsedUrl;

  try {
    parsedUrl = new URL(url.trim());
  } catch {
    setError("Please enter a valid URL.");
    return;
  }

  if (!["http:", "https:"].includes(parsedUrl.protocol)) {
    setError("Only HTTP and HTTPS URLs are supported.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/links`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: parsedUrl.href }),
    });

    if (!response.ok) {
      throw new Error("Unable to create short link.");
    }

    const data = await response.json();

    onShorten(data);
    setUrl("");
  } catch (error) {
    setError(error.message || "Could not connect to the backend.");
  }
}


  return (
    <section className="hero">
      <span className="eyebrow">YOUR LINKS, SIMPLIFIED</span>
      <h1>Short links. Big possibilities.</h1>
      <p>
        Create short links and keep all your URLs organized
        in one simple dashboard.
      </p>

      <div className="shorten-form">
        <label htmlFor="url-input">Long URL</label>

        <div className="input-row">
          <input
            id="url-input"
            type="url"
            placeholder="https://example.com/your/long/url"
            value={url}
            onChange={(event) => {
              setUrl(event.target.value);
              setError("");
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter") handleSubmit();
            }}
          />

          <button onClick={handleSubmit}>
            Shorten URL <span>→</span>
          </button>
        </div>

        {error && <p className="error">{error}</p>}

        <p className="helper">
          Free to use · No account required for this demo
        </p>
      </div>
    </section>
  );
}

export default URLForm;
