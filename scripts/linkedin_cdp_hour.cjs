// LinkedIn Feed Collector - CDP WebSocket (Node.js)
// 连接 Edge 浏览器 (port 18800) 持续采集 60 分钟

const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');

// ==================== 配置 ====================

const CDP_PORT = 18800;
const CDP_HTTP = `http://127.0.0.1:${CDP_PORT}`;
const OUTPUT_DIR = path.join('C:', 'Users', 'Haide', 'Desktop', 'real business post');
const DURATION_MINUTES = 60;
const SCROLL_PAUSE = 5000; // ms
const SCROLL_PIXELS = 800;

// PN 正则
const PN_REGEX = [
  /\b[0-9]{6,}-[0-9]{2,}\b/gi,
  /\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b/gi,
  /\bHG[0-9]{4}[A-Z]{2}\b/gi,
];

// 业务关键词
const KEYWORDS = [
  'CFM56', 'V2500', 'A320', 'B737', 'LEAP', 'engine', 'landing', 'APU',
  'stock', 'price', 'available', 'PN', 'P/N', '件号', '现货', '出售',
  'starter', 'generator', 'pump', 'valve', 'actuator', 'sensor',
  'ADIRU', 'MCP', 'TCAS', 'surplus', 'rotable', 'aircraft', 'ferry',
  'delivery', 'lease', 'sold', 'purchase', 'blade', 'module',
];

// ==================== 工具 ====================

function log(msg) {
  const time = new Date().toLocaleTimeString('zh-CN', { hour12: false });
  console.log(`[${time}] ${msg}`);
}

function extractPN(text) {
  const pns = [];
  for (const regex of PN_REGEX) {
    const matches = text.match(regex) || [];
    pns.push(...matches);
  }
  return [...new Set(pns)];
}

function hasBusinessIntent(text) {
  const lower = text.toLowerCase();
  return KEYWORDS.some(kw => lower.includes(kw.toLowerCase()));
}

function getTabs() {
  return new Promise((resolve, reject) => {
    http.get(`${CDP_HTTP}/json/list`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

function savePosts(posts, file) {
  if (!posts.length) return 0;
  
  const header = '采集时间,内容摘要,零件号,业务意图\n';
  let content = fs.existsSync(file) ? '' : header;
  
  for (const post of posts) {
    const text = post.text.slice(0, 500).replace(/[,\n\r]/g, ' ');
    const time = new Date().toISOString().slice(0, 19).replace('T', ' ');
    const pns = post.pn.join(',');
    const biz = post.business ? '是' : '否';
    content += `${time},${text},${pns},${biz}\n`;
  }
  
  fs.appendFileSync(file, content, 'utf8');
  return posts.length;
}

// ==================== 主逻辑 ====================

async function main() {
  log('='.repeat(50));
  log('LinkedIn Feed Collector - CDP WebSocket');
  log(`Duration: ${DURATION_MINUTES} minutes`);
  log('='.repeat(50));
  
  // 获取标签页
  const tabs = await getTabs();
  const linkedinTab = tabs.find(t => 
    t.url?.includes('linkedin.com') || t.title?.includes('LinkedIn')
  );
  
  if (!linkedinTab) {
    log('ERROR: No LinkedIn tab found!');
    return;
  }
  
  log(`Found tab: ${linkedinTab.title}`);
  const wsUrl = linkedinTab.webSocketDebuggerUrl;
  
  // 连接 WebSocket
  const ws = new WebSocket(wsUrl, {
    headers: { Origin: CDP_HTTP }
  });
  
  let msgId = 0;
  const allPosts = [];
  let scrollCount = 0;
  const startTime = Date.now();
  const endTime = startTime + DURATION_MINUTES * 60 * 1000;
  
  const sendCmd = (method, params = {}) => {
    msgId++;
    ws.send(JSON.stringify({ id: msgId, method, params }));
    return new Promise((resolve) => {
      const handler = (data) => {
        const resp = JSON.parse(data);
        if (resp.id === msgId) {
          ws.removeListener('message', handler);
          resolve(resp);
        }
      };
      ws.on('message', handler);
    });
  };
  
  ws.on('open', async () => {
    log('WebSocket connected');
    
    // Enable runtime
    await sendCmd('Runtime.enable');
    
    const outputFile = path.join(OUTPUT_DIR, 
      `LinkedIn_CDP_${new Date().toISOString().slice(0, 16).replace(/[:-]/g, '')}.csv`
    );
    
    // 采集循环
    while (Date.now() < endTime) {
      scrollCount++;
      const remaining = Math.floor((endTime - Date.now()) / 60000);
      
      // 滚动
      await sendCmd('Runtime.evaluate', {
        expression: `window.scrollBy(0, ${SCROLL_PIXELS})`
      });
      
      // 等待
      await new Promise(r => setTimeout(r, SCROLL_PAUSE));
      
      // 提取帖子
      const result = await sendCmd('Runtime.evaluate', {
        expression: `(() => {
          let posts = []; let seen = new Set();
          document.querySelectorAll('div, article, section, span, p').forEach(el => {
            let text = (el.innerText || '').trim();
            let key = text.slice(0, 100);
            if (seen.has(key) || text.length < 50 || text.length > 3000) return;
            seen.add(key);
            let keywords = ['CFM56', 'V2500', 'A320', 'B737', 'LEAP', 'engine', 'landing', 'APU',
                          'stock', 'price', 'available', 'PN', 'P/N', '件号', '现货', '出售',
                          'starter', 'generator', 'pump', 'valve', 'actuator', 'sensor',
                          'ADIRU', 'MCP', 'TCAS', 'surplus', 'rotable', 'aircraft', 'ferry',
                          'delivery', 'lease', 'sold', 'purchase', 'blade', 'module'];
            for (let kw of keywords) {
              if (text.toLowerCase().includes(kw.toLowerCase())) {
                posts.push(text);
                break;
              }
            }
          });
          return posts.slice(0, 10);
        })()`,
        returnByValue: true
      });
      
      const texts = result.result?.result?.value || [];
      let found = 0;
      
      for (const text of texts) {
        if (typeof text === 'string' && text.length > 50) {
          const pn = extractPN(text);
          const business = hasBusinessIntent(text);
          
          if (business || pn.length) {
            allPosts.push({ text, pn, business });
            found++;
          }
        }
      }
      
      log(`Scroll #${scrollCount} | ${remaining}min left | Found ${found} | Total ${allPosts.length}`);
      
      // 每 15 次保存
      if (scrollCount % 15 === 0) {
        const saved = savePosts(allPosts, outputFile);
        if (saved) log(`  Saved ${saved} posts`);
      }
      
      // 随机等待
      const wait = SCROLL_PAUSE + (scrollCount % 3) * 1000;
      await new Promise(r => setTimeout(r, wait));
    }
    
    // 最终保存
    savePosts(allPosts, outputFile);
    
    log('='.repeat(50));
    log('Collection complete!');
    log(`Total scrolls: ${scrollCount}`);
    log(`Total posts: ${allPosts.length}`);
    log(`Output: ${outputFile}`);
    log('='.repeat(50));
    
    ws.close();
  });
  
  ws.on('error', (err) => {
    log(`WebSocket error: ${err.message}`);
  });
}

main().catch(err => log(`Error: ${err}`));