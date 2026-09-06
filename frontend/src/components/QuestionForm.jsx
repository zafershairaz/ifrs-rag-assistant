import { useState } from "react";

function QuestionForm({ onSubmit, loading }) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!question.trim()) {
      return;
    }

    onSubmit(question.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="question-form">

      <label htmlFor="question">
        Ask an IFRS or IAS Question
      </label>

      <textarea
        id="question"
        value={question}
        onChange={(event) =>
          setQuestion(event.target.value)
        }
        placeholder="Example: What are the recognition criteria for revenue under IFRS 15?"
        rows="5"
        disabled={loading}
      />

      <button
        type="submit"
        disabled={loading || !question.trim()}
      >
        {loading ? "Generating Answer..." : "Ask Question"}
      </button>

    </form>
  );
}

export default QuestionForm;