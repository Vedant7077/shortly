function LinkList({ links, onCopy }) {
  return (
    <section className="links-section">
      <div className="section-heading">
        <div>
          <h2>Your links</h2>
          <p>Manage and copy your shortened URLs.</p>
        </div>
        <span className="count">{links.length} links</span>
      </div>

      {links.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">↗</div>
          <h3>No links yet</h3>
          <p>Your shortened links will appear here.</p>
        </div>
      ) : (
        <div className="link-list">
          {links.map((link) => (
            <article className="link-card" key={link.id}>
              <div className="link-details">
                <strong className="short-url">
                  {link.shortUrl}
                </strong>
                <span className="original-url">
                  {link.originalUrl}
                </span>
              </div>

              <div className="link-actions">
                <span className="click-count">
                  {link.clicks} clicks
                </span>
                <button
                  className="copy-button"
                  onClick={() => onCopy(link.shortUrl)}
                >
                  Copy link
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default LinkList;