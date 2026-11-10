function StatsCards({ links }) {
  const totalClicks = links.reduce(
    (total, link) => total + link.clicks,
    0
  );

  return (
    <section className="stats">
      <article className="stat-card">
        <span>Total links</span>
        <strong>{links.length}</strong>
        <small>Links created in this session</small>
      </article>

      <article className="stat-card">
        <span>Total clicks</span>
        <strong>{totalClicks}</strong>
        <small>Tracked link visits</small>
      </article>

      <article className="stat-card">
        <span>Active links</span>
        <strong>{links.length}</strong>
        <small>Links in this session</small>
      </article>
    </section>
  );
}

export default StatsCards;