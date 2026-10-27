import { useState } from "react";
import Header from "./components/Header";
import UploadForm from "./components/UploadForm";
import Dashboard from "./components/Dashboard";
import "./styles/global.css";

function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="app-root">
      <div className="container">
        <Header />
        <main className="layout">
          <aside className="sidebar">
            <UploadForm onResult={setResult} onLoading={setIsLoading} />
          </aside>
          <section className="main-panel">
            <Dashboard result={result} isLoading={isLoading} />
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;