function Sources({ sources }) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <section className="sources-section">

      <h2>Retrieved Sources</h2>

      <div className="sources-list">

        {sources.map((source, index) => (

          <div
            className="source-card"
            key={`${source.standard}-${source.paragraph}-${index}`}
          >

            <div className="source-title">
              {source.standard}
            </div>

            <div>
              Paragraph: {source.paragraph}
            </div>

            <div>
              Relevance Score:{" "}
              {source.score
                ? source.score.toFixed(3)
                : "N/A"}
            </div>

          </div>

        ))}

      </div>

    </section>
  );
}

export default Sources;