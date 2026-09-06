function Answer({ answer }) {
  if (!answer) {
    return null;
  }

  return (
    <section className="answer-section">

      <h2>Answer</h2>

      <div className="answer-content">
        {answer}
      </div>

    </section>
  );
}

export default Answer;