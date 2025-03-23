// ローカル開発環境ではプロキシを使用
const apiUrl = '/api';
console.log('API URL:', apiUrl);

document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('jobModal');
  const openBtn = document.getElementById('openModal');
  const closeBtn = document.querySelector('.close-button');
  const submitBtn = document.getElementById('submitJob');
  const clearBtn = document.getElementById('clearBtn');
  const resultDiv = document.getElementById('result');
  const jobContentTextarea = document.getElementById('jobContent');
  
  openBtn.onclick = function() {
    modal.style.display = "block";
  }
  
  closeBtn.onclick = function() {
    modal.style.display = "none";
    jobContentTextarea.value = "";
    resultDiv.textContent = "";
  }
  
  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
      jobContentTextarea.value = "";
      resultDiv.textContent = "";
    }
  }
  
  clearBtn.addEventListener('click', function() {
    jobContentTextarea.value = "";
    resultDiv.textContent = "";
  });
  
  // APIの接続テスト
  fetch(`${apiUrl}/ping`, {
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(data => {
      console.log('API connection test:', data);
    })
    .catch(error => {
      console.error('API connection test failed:', error);
    });
  
  submitBtn.addEventListener('click', async () => {
    const content = jobContentTextarea.value;
    
    if (!content.trim()) {
      resultDiv.textContent = "求人情報を入力してください";
      resultDiv.style.color = "red";
      return;
    }
    
    resultDiv.textContent = '処理中...';
    
    try {
      console.log('Sending request to:', apiUrl);
      console.log('Request data:', { content });
      
      const response = await fetch(`${apiUrl}/process_job`, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });
      
      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);
      
      resultDiv.textContent = data.message;
      
      if (response.ok) {
        resultDiv.style.color = 'green';
      } else {
        resultDiv.style.color = 'red';
      }
    } catch (error) {
      console.error('Error:', error);
      resultDiv.textContent = `エラーが発生しました: ${error.message}`;
      resultDiv.style.color = 'red';
    }
  });
}); 
