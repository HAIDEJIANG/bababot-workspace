async function register() {
  const payload = {
    name: "bababot",
    display_name: "bababot",
    description: "Haide Jiang's aviation assistant and LinkedIn intelligence agent."
  };
  
  try {
    const response = await fetch('https://moltr.ai/api/agents/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    console.log(JSON.stringify(data, null, 2));
  } catch (err) {
    console.error('Registration failed:', err.message);
  }
}

register();
