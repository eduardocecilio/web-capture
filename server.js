#!/usr/bin/env node

/**
 * Dev Server Script
 * Inicia um servidor HTTP simples para desenvolvimento
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 8080;
const PUBLIC_DIR = __dirname;

// MIME types
const mimeTypes = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.wav': 'audio/wav',
  '.mp4': 'video/mp4',
  '.woff': 'application/font-woff',
  '.ttf': 'application/font-ttf',
  '.eot': 'application/vnd.ms-fontobject',
  '.otf': 'application/font-otf',
  '.wasm': 'application/wasm'
};

const server = http.createServer((req, res) => {
  // Parse URL
  const parsedUrl = url.parse(req.url);
  
  // Extract URL path
  let pathname = `.${parsedUrl.pathname}`;
  
  // Default to index.html if root is requested
  if (pathname === './') {
    pathname = './index.html';
  }

  // Prevent directory traversal attacks
  const filePath = path.join(PUBLIC_DIR, pathname);
  
  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  // Try to access the file
  fs.readFile(filePath, (err, content) => {
    if (err) {
      // If file not found and it's not an API route, serve index.html (SPA)
      if (err.code === 'ENOENT') {
        if (!filePath.includes('.')) {
          // No file extension, probably a route - serve index.html
          fs.readFile(path.join(PUBLIC_DIR, 'index.html'), (err, content) => {
            if (err) {
              res.writeHead(404);
              res.end('Not Found');
            } else {
              res.writeHead(200, { 'Content-Type': 'text/html' });
              res.end(content);
            }
          });
        } else {
          res.writeHead(404);
          res.end('Not Found');
        }
      } else {
        res.writeHead(500);
        res.end('Internal Server Error');
      }
    } else {
      // Success - determine MIME type
      const ext = path.extname(filePath).toLowerCase();
      const contentType = mimeTypes[ext] || 'application/octet-stream';
      
      // Add CORS headers
      res.writeHead(200, {
        'Content-Type': contentType,
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'no-cache'
      });
      res.end(content);
    }
  });
});

server.listen(PORT, () => {
  console.log(`
  ╔═══════════════════════════════════════╗
  ║   Web-Capture Dev Server              ║
  ║   Server running at http://localhost:${PORT}   ║
  ║   Press Ctrl+C to stop                ║
  ╚═══════════════════════════════════════╝
  `);
});

// Handle server errors
server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use!`);
    process.exit(1);
  } else {
    throw err;
  }
});
