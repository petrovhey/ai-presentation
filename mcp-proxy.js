#!/usr/bin/env node
/**
 * MCP Proxy для Yandex Direct (HTTP Streamable)
 */

const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StreamableHTTPClientTransport } = require('@modelcontextprotocol/sdk/client/streamableHttp.js');

const SERVER_URL = 'https://direct-mcp.aatex.ru/mcp';
const AUTH_TOKEN = 'dfefcc0807df597e68077eb2a012d69a2034ce8188814c0fa4007e12a1b66797';

async function main() {
  const url = new URL(SERVER_URL);
  
  const transport = new StreamableHTTPClientTransport(url, {
    requestInit: {
      headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Accept': 'application/json, text/event-stream'
      }
    }
  });

  const client = new Client(
    { name: 'yandex-direct-proxy', version: '1.0.0' },
    { capabilities: {} }
  );

  await client.connect(transport);
  console.error('[Proxy] Connected to Yandex Direct MCP');

  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
  });

  rl.on('line', async (line) => {
    try {
      const message = JSON.parse(line);
      
      // Обрабатываем запросы
      if (message.method === 'initialize') {
        const result = await client.request(message, null);
        console.log(JSON.stringify({ jsonrpc: '2.0', id: message.id, result }));
        return;
      }
      
      if (message.method === 'tools/list') {
        const tools = await client.listTools();
        console.log(JSON.stringify({ jsonrpc: '2.0', id: message.id, result: { tools } }));
        return;
      }
      
      if (message.method === 'tools/call') {
        const result = await client.callTool(message.params);
        console.log(JSON.stringify({ jsonrpc: '2.0', id: message.id, result }));
        return;
      }
      
      if (message.method === 'resources/list') {
        const resources = await client.listResources();
        console.log(JSON.stringify({ jsonrpc: '2.0', id: message.id, result: { resources } }));
        return;
      }
      
      if (message.method === 'prompts/list') {
        const prompts = await client.listPrompts();
        console.log(JSON.stringify({ jsonrpc: '2.0', id: message.id, result: { prompts } }));
        return;
      }
      
      console.log(JSON.stringify({
        jsonrpc: '2.0',
        id: message.id,
        error: { code: -32601, message: 'Method not found' }
      }));
      
    } catch (err) {
      console.error(`[Proxy Error] ${err.message}`);
      console.log(JSON.stringify({
        jsonrpc: '2.0',
        id: null,
        error: { code: -32700, message: err.message }
      }));
    }
  });

  await new Promise(() => {});
}

main().catch((err) => {
  console.error('[Fatal]', err);
  process.exit(1);
});
