import axios from "axios";
import { useState } from "react";
import "./App.css";

function App() {
  const [jobContent, setJobContent] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("処理中...");
    try {
      const response = await axios.post("http://localhost:5555/process_job", {
        content: jobContent,
      });
      setMessage(response.data.message);
    } catch (error) {
      setMessage("エラーが発生しました");
      console.error(error);
    }
  };

  return (
    <div className='App'>
      <h1>求人情報入力</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={jobContent}
          onChange={(e) => setJobContent(e.target.value)}
          placeholder='求人情報を入力してください'
          rows='10'
          cols='50'
        />
        <br />
        <button type='submit'>送信</button>
      </form>
      <p>{message}</p>
    </div>
  );
}

export default App;
