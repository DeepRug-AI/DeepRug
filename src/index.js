const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);
const dotenv = require('dotenv');
const TradingService = require('./services/trading_service');

dotenv.config();

// Initialize trading service
const tradingService = new TradingService(
    process.env.SOLANA_ENDPOINT || 'https://api.devnet.solana.com',
    process.env.PROGRAM_ID
);

// Middleware configuration
app.use(express.json());

// Start trading stream
tradingService.startTradingStream();

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('User connected');

  socket.on('disconnect', () => {
    console.log('User disconnected');
  });
});

// API routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Start server
const PORT = process.env.PORT || 3000;
http.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});