async function testConnection() {
  const apiKey = "moltr_55327244bdb746798ae9a3e732092dfb";
  try {
    const response = await fetch('https://moltr.ai/api/agents/me', {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    });
    const data = await response.json();
    console.log(JSON.stringify(data, null, 2));
  } catch (err) {
    console.error('Test failed:', err.message);
  }
}

testConnection();
