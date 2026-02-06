const { MCPClient } = require('./MaiMaiBot/src/mcpClient');

const token = 'o5iMdVTmxUW8cuzrm5vaduVB6Ge9p3s0';
const baseUrl = 'https://mcp.mcd.cn/mcp-servers/mcd-mcp';

async function claim() {
  console.log('Starting McDonald\'s coupon claim...');
  const client = new MCPClient({
    baseUrl,
    token,
    requestTimeoutMs: 60000
  });

  try {
    console.log('Calling auto-bind-coupons...');
    const result = await client.callTool('auto-bind-coupons', {});
    console.log('Claim result:', JSON.stringify(result, null, 2));
    
    // Check for success in the response text
    const text = result.content?.[0]?.text || '';
    if (text.includes('成功') || text.includes('success')) {
      console.log('Successfully claimed all coupons!');
    } else {
      console.log('Claim finished with response:', text);
    }
  } catch (error) {
    console.error('Error claiming coupons:', error.message);
  }
}

claim();
