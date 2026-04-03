import { useState } from "react";
import Header from "./components/Header";
import UploadForm from "./components/UploadForm";
import ResultCard from "./components/ResultCard";
import "./styles/global.css";

function App() {
  const [result, setResult] = useState(null);

  return (
    <div className="container">
      <Header />
      <UploadForm onResult={setResult} />
      <ResultCard result={result} />
    </div>
  );
}

export default App;