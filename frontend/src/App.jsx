import { useState } from "react";
import "./App.css";


const API_URL = "http://127.0.0.1:8000";


function App() {

  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const askQuestion = async () => {

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setError("Please enter an accounting question.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {

      const response = await fetch(
        `${API_URL}/ask`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            question: trimmedQuestion
          })
        }
      );


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Unable to process the question."
        );
      }


      setResult(data);

    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Unable to connect to the IFRS/IAS assistant."
      );

    } finally {

      setLoading(false);

    }
  };


  const handleKeyDown = (event) => {

    if (event.key === "Enter" && !event.shiftKey) {

      event.preventDefault();

      askQuestion();

    }
  };


  const clearAll = () => {

    setQuestion("");
    setResult(null);
    setError("");

  };


  return (

    <div className="app">

      <header className="header">

        <div className="header-content">

          <h1>
            IFRS / IAS Research Assistant
          </h1>

          <p>
            AI-powered accounting research using
            Retrieval-Augmented Generation
          </p>

        </div>

      </header>


      <main className="container">

        <section className="question-card">

          <h2>
            Ask an accounting question
          </h2>

          <p className="helper-text">
            Enter an IFRS or IAS accounting question.
            The relevant standard is detected automatically.
          </p>


          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Example: What are the recognition criteria for a contract under IFRS 15?"
            maxLength={2000}
          />


          <div className="button-row">

            <button
              className="ask-button"
              onClick={askQuestion}
              disabled={loading}
            >

              {loading
                ? "Researching..."
                : "Ask Question"
              }

            </button>


            <button
              className="clear-button"
              onClick={clearAll}
              disabled={loading}
            >
              Clear
            </button>

          </div>


          {loading && (

            <div className="loading">

              <div className="spinner"></div>

              <span>
                Searching IFRS/IAS material and generating
                an answer...
              </span>

            </div>

          )}


          {error && (

            <div className="error">

              {error}

            </div>

          )}

        </section>


        {result && (

          <section className="result-card">

            <div className="result-header">

              <h2>
                Answer
              </h2>

            </div>


            <div className="answer">

              {result.answer}

            </div>


            <div className="sources-section">

              <h3>
                Retrieved Sources
              </h3>


              <p className="source-description">
                The following IFRS/IAS paragraphs were
                retrieved as supporting material.
              </p>


              <div className="sources">

                {result.sources.map(
                  (source, index) => (

                    <div
                      className="source"
                      key={`${source.standard}-${source.paragraph}-${index}`}
                    >

                      <div className="source-main">

                        <strong>
                          {source.standard}
                        </strong>

                        <span>
                          Paragraph {source.paragraph}
                        </span>

                      </div>


                      <div className="source-score">

                        Relevance:{" "}
                        {source.score.toFixed(3)}

                      </div>

                    </div>

                  )
                )}

              </div>

            </div>

          </section>

        )}

      </main>


      <footer className="footer">

        <p>
          IFRS / IAS Research Assistant
        </p>

        <p>
          RAG • FAISS • TF-IDF • Sentence Transformers • Qwen3
        </p>

      </footer>

    </div>

  );
}


export default App;