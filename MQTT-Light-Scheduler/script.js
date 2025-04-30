document.addEventListener('DOMContentLoaded', () => {
    const onTimeInput = document.getElementById('on-time');
    const offTimeInput = document.getElementById('off-time');
    const onTimeDisplay = document.getElementById('on-time-display');
    const offTimeDisplay = document.getElementById('off-time-display');
    const form = document.getElementById('light-form');
  
    onTimeInput.addEventListener('input', () => {
      onTimeDisplay.textContent = onTimeInput.value || '--:--';
    });
  
    offTimeInput.addEventListener('input', () => {
      offTimeDisplay.textContent = offTimeInput.value || '--:--';
    });
  
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      alert(`Light will turn ON at ${onTimeInput.value} and OFF at ${offTimeInput.value}`);
    });
  });

  let socket = new WebSocket("ws://localhost:8765");
  const statusIndicator = document.getElementById('statusIndicator');
  const statusText = document.getElementById('statusText');
  const notification = document.getElementById('notification');
  
  socket.onopen = () => {
      console.log("✅ WebSocket Connected!");
      statusIndicator.classList.add('connected');
      statusText.textContent = "Connected";
  };
  
  socket.onclose = () => {
      statusIndicator.classList.remove('connected');
      statusText.textContent = "Disconnected";
  };
  
  socket.onerror = () => {
      statusIndicator.classList.remove('connected');
      statusText.textContent = "Connection Error";
  };
  
  function submitSchedule() {
      const onTime = document.getElementById('onTime').value;
      const offTime = document.getElementById('offTime').value;
      
      if (onTime) {
          socket.send(`${onTime} ON`);
      }
      if (offTime) {
          socket.send(`${offTime} OFF`);
      }
      
      // Show notification
      notification.classList.add('show');
      setTimeout(() => {
          notification.classList.remove('show');
      }, 3000);
  }
  