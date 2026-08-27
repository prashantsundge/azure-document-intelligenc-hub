import { useEffect, useState, type FormEvent } from "react";

import { api } from "./api";
import type {
  AskResponse,
  DocumentDetail,
  DocumentSummary,
  SearchResult,
} from "./types";

function App() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<DocumentDetail | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AskResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDocuments() {
      try {
        const data = await api.getDocuments();
        setDocuments(data);
        if (data.length > 0) {
          setSelectedDocument(await api.getDocument(data[0].id));
        }
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Unable to load documents.");
      } finally {
        setLoading(false);
      }
    }

    void loadDocuments();
  }, []);

  async function selectDocument(documentId: string) {
    try {
      setError("");
      setSelectedDocument(await api.getDocument(documentId));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to load document.");
    }
  }

  async function handleSearch(event: FormEvent) {
    event.preventDefault();

    if (searchQuery.trim().length < 3) {
      setError("Enter at least three characters to search.");
      return;
    }

    try {
      setError("");
      const response = await api.search(searchQuery);
      setSearchResults(response.results);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Search failed.");
    }
  }

  async function handleAsk(event: FormEvent) {
    event.preventDefault();

    if (question.trim().length < 3) {
      setError("Enter a longer question.");
      return;
    }

    try {
      setError("");
      setAnswer(await api.ask(question));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Question failed.");
    }
  }

  if (loading) {
    return <main className="loading">Loading public documents…</main>;
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Azure AI portfolio project</p>
        <h1>Document Intelligence Hub</h1>
        <p>
          Search and question curated public documents with transparent, grounded citations.
        </p>
      </header>

      {error && <p className="error-banner" role="alert">{error}</p>}

      <section className="search-panel" aria-label="Search documents">
        <form onSubmit={handleSearch}>
          <label htmlFor="search">Search the document catalogue</label>
          <div className="form-row">
            <input
              id="search"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Try: remote work or invoice"
            />
            <button type="submit">Search</button>
          </div>
        </form>

        {searchResults.length > 0 && (
          <ul className="results-list">
            {searchResults.map((result) => (
              <li key={result.document.id}>
                <button
                  className="result-button"
                  onClick={() => void selectDocument(result.document.id)}
                >
                  <strong>{result.document.title}</strong>
                  <span>Relevance: {Math.round(result.score * 100)}%</span>
                  <p>{result.excerpt}</p>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="workspace">
        <aside className="catalogue" aria-label="Document catalogue">
          <h2>Documents</h2>
          {documents.map((document) => (
            <button
              key={document.id}
              className={selectedDocument?.id === document.id ? "document active" : "document"}
              onClick={() => void selectDocument(document.id)}
            >
              <strong>{document.title}</strong>
              <span>{document.document_type}</span>
            </button>
          ))}
        </aside>

        <article className="document-view">
          {selectedDocument && (
            <>
              <p className="eyebrow">{selectedDocument.document_type} · {selectedDocument.language}</p>
              <h2>{selectedDocument.title}</h2>
              <p>{selectedDocument.description}</p>

              <h3>Extracted content</h3>
              <p>{selectedDocument.extracted_text}</p>

              <h3>AI enrichment</h3>
              <div className="tag-group">
                {[...selectedDocument.key_phrases, ...selectedDocument.entities].map((item) => (
                  <span className="tag" key={item}>{item}</span>
                ))}
              </div>
                            {selectedDocument.analysis_fields.length > 0 && (
                <>
                  <h3>Invoice fields extracted by Azure AI</h3>
                  <div className="field-grid">
                    {selectedDocument.analysis_fields.map((field) => (
                      <div className="field-card" key={field.name}>
                        <strong>{field.name}</strong>
                        <span>{field.content ?? "No extracted value"}</span>
                        <small>
                          Confidence:{" "}
                          {field.confidence === null
                            ? "not available"
                            : `${Math.round(field.confidence * 100)}%`}
                        </small>
                      </div>
                    ))}
                  </div>
                </>
              )}
              <h3>Privacy review</h3>
              <div className="privacy-review">
                {selectedDocument.pii_entities.length === 0 ? (
                  <p>No PII was detected in this synthetic document.</p>
                ) : (
                  <ul>
                    {selectedDocument.pii_entities.map((entity) => (
                      <li key={`${entity.text}-${entity.category}`}>
                        {entity.category}: {entity.text} (
                        {Math.round(entity.confidence * 100)}% confidence)
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              {selectedDocument.quality && (
                <>
                  <h3>Extraction quality</h3>
                  <div className={`quality ${selectedDocument.quality.status}`}>
                    <strong>{selectedDocument.quality.status.replace("_", " ")}</strong>
                    <p>
                      Review threshold:{" "}
                      {Math.round(selectedDocument.quality.minimum_confidence * 100)}%
                    </p>

                    {selectedDocument.quality.issues.length > 0 && (
                      <ul>
                        {selectedDocument.quality.issues.map((issue) => (
                          <li key={`${issue.field}-${issue.reason}`}>{issue.message}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </>
              )}
              <h3>Detected tables</h3>
              {selectedDocument.tables.map((table, tableIndex) => (
                <table key={tableIndex}>
                  <tbody>
                    {table.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {row.map((cell, cellIndex) =>
                          rowIndex === 0 ? <th key={cellIndex}>{cell}</th> : <td key={cellIndex}>{cell}</td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ))}
            </>
          )}
        </article>
      </section>

      <section className="chat-panel">
        <h2>Ask the knowledge base</h2>
        <p>Answers are restricted to the curated documents and include evidence.</p>

        <form onSubmit={handleAsk}>
          <label htmlFor="question">Your question</label>
          <div className="form-row">
            <input
              id="question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="What equipment is provided for remote work?"
            />
            <button type="submit">Ask</button>
          </div>
        </form>

        {answer && (
          <div className="answer">
            <p><strong>Answer:</strong> {answer.answer}</p>
            <h3>Sources</h3>
            <ul>
              {answer.citations.map((citation) => (
                <li key={citation.document_id}>
                  {citation.document_title}, page {citation.page_number}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </main>
  );
}

export default App;