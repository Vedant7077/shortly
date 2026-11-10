import { useEffect, useState } from "react";
import Header from "./components/Header";
import URLForm from "./components/URLForm";
import StatsCards from "./components/StatsCards";
import LinkList from "./components/LinkList";
import { API_BASE_URL } from "./config";

function App() {
  const [links, setLinks] = useState([]);

  // Load saved links when the dashboard opens

useEffect(() => {
  let isMounted = true;

  async function fetchLinks() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/links`);

      if (!response.ok) {
        throw new Error("Failed to fetch links");
      }

      const data = await response.json();

      const formattedLinks = data.map((link) => ({
        id: link.id,
        originalUrl: link.original_url,
        shortUrl: link.short_url,
        clicks: link.clicks,
      }));

      if (isMounted) {
        setLinks(formattedLinks);
      }
    } catch (error) {
      console.error("Error loading saved links:", error);
    }
  }

  fetchLinks();

  const intervalId = setInterval(fetchLinks, 5000);

  return () => {
    isMounted = false;
    clearInterval(intervalId);
  };
}, []);


  // Create a link and add it to the dashboard
  function createShortLink(data) {
    const newLink = {
      id: data.id,
      originalUrl: data.original_url,
      shortUrl: data.short_url,
      clicks: data.clicks,
    };

    setLinks((previousLinks) => [newLink, ...previousLinks]);
  }

  async function handleCopy(shortUrl) {
    try {
      await navigator.clipboard.writeText(shortUrl);
      alert("Short link copied!");
    } catch {
      alert("Unable to copy. Please copy the link manually.");
    }
  }

  return (
    <main className="app">
      <Header />
      <URLForm onShorten={createShortLink} />
      <StatsCards links={links} />
      <LinkList links={links} onCopy={handleCopy} />
      <footer>Shortly · A System Design learning project</footer>
    </main>
  );
}

export default App;
