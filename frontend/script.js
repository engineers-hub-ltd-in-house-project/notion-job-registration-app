document.getElementById('submitJob').addEventListener('click', async () => {
  const content = document.getElementById('jobContent').value;
  const resultDiv = document.getElementById('result');
  
  resultDiv.textContent = '処理中...';
  
  try {
    const response = await fetch('http://localhost:5555/process_job', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    });
    
    const data = await response.json();
    resultDiv.textContent = data.message;
    
    if (response.ok) {
      resultDiv.style.color = 'green';
    } else {
      resultDiv.style.color = 'red';
    }
  } catch (error) {
    resultDiv.textContent = `エラーが発生しました: ${error.message}`;
    resultDiv.style.color = 'red';
  }
}); 
