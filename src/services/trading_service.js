const { Connection, PublicKey, Transaction, SystemProgram } = require('@solana/web3.js');
const { Program } = require('@project-serum/anchor');
const { TradingEngine } = require('../ai_engine/trading_engine');
const WebSocket = require('ws');

class TradingService {
    constructor(endpoint, programId) {
        // Initialize Solana connection
        this.connection = new Connection(endpoint);
        this.programId = new PublicKey(programId);
        
        // Initialize trading engine
        this.tradingEngine = new TradingEngine();
        
        // Active trading signals
        this.activeSignals = new Map();
        
        // Initialize WebSocket server
        this.wss = new WebSocket.Server({ port: 8080 });
        this.clients = new Map();
        
        this.setupWebSocket();
    }
    
    setupWebSocket() {
        this.wss.on('connection', (ws) => {
            ws.on('message', async (message) => {
                try {
                    const data = JSON.parse(message);
                    
                    if (data.type === 'subscribe') {
                        this.clients.set(ws, {
                            publicKey: data.publicKey,
                            symbols: new Set(data.symbols)
                        });
                    }
                } catch (error) {
                    console.error('Error processing WebSocket message:', error);
                }
            });
            
            ws.on('close', () => {
                this.clients.delete(ws);
            });
        });
    }
    
    broadcastSignal(symbol, signal) {
        this.clients.forEach((client, ws) => {
            if (client.symbols.has(symbol) && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'signal',
                    symbol,
                    signal
                }));
            }
        });
    }
    
    notifyFollowSuccess(userPublicKey, symbol, signal) {
        this.clients.forEach((client, ws) => {
            if (client.publicKey === userPublicKey && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'follow_success',
                    symbol,
                    signal
                }));
            }
        });
    }
    
    async generateAndBroadcastSignal(symbol) {
        try {
            // Fetch market data and generate signal
            const marketData = await this.tradingEngine.fetch_market_data(symbol);
            const signal = await this.tradingEngine.generate_trading_signal(marketData);
            
            if (signal) {
                // Store active signal
                this.activeSignals.set(symbol, {
                    ...signal,
                    followers: new Set()
                });
                
                // Broadcast signal to connected clients
                this.broadcastSignal(symbol, signal);
            }
            
            return signal;
        } catch (error) {
            console.error('Error generating trading signal:', error);
            return null;
        }
    }
    
    async followTrade(userPublicKey, symbol) {
        try {
            // Check if signal exists
            const signal = this.activeSignals.get(symbol);
            if (!signal) {
                throw new Error('No active signal for this symbol');
            }
            
            // Check if user is already following
            if (signal.followers.has(userPublicKey)) {
                throw new Error('Already following this signal');
            }
            
            // Create follow trade instruction
            const instruction = await this.program.instruction.followTrade({
                accounts: {
                    user: userPublicKey,
                    systemProgram: SystemProgram.programId,
                },
                signers: [userPublicKey]
            });
            
            // Add user to followers
            signal.followers.add(userPublicKey);
            
            // Notify user of successful follow
            this.notifyFollowSuccess(userPublicKey, symbol, signal);
            
            return true;
        } catch (error) {
            console.error('Error following trade:', error);
            return false;
        }
    }
    
    async startTradingStream(symbols = ['BTC/USDT', 'ETH/USDT']) {
        // Start periodic signal generation
        setInterval(async () => {
            for (const symbol of symbols) {
                await this.generateAndBroadcastSignal(symbol);
            }
        }, 60000); // Generate signals every minute
    }
                throw new Error('No active signal for this symbol');
            }
            
            // Create transaction for follow trade fee
            const transaction = new Transaction();
            const instruction = await this.program.methods
                .payFollowTradeFee()
                .accounts({
                    user: userPublicKey,
                    // Add other required accounts based on your program structure
                })
                .instruction();
            
            transaction.add(instruction);
            
            // Send and confirm transaction
            const signature = await this.connection.sendTransaction(transaction, []);
            const confirmation = await this.connection.confirmTransaction(signature);
            
            if (confirmation.value.err === null) {
                // Add user to signal followers
                signal.followers.add(userPublicKey.toString());
                
                // Notify user of successful follow
                this.notifyFollowSuccess(userPublicKey.toString(), symbol, signal);
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Error following trade:', error);
            return false;
        }
    }
    
    broadcastSignal(symbol, signal) {
        // This method should be implemented to work with your WebSocket system
        // to broadcast signals to connected clients
        console.log(`Broadcasting signal for ${symbol}:`, signal);
    }
    
    notifyFollowSuccess(userPublicKey, symbol, signal) {
        // This method should be implemented to notify users of successful follows
        console.log(`User ${userPublicKey} successfully followed ${symbol} signal`);
    }
}

module.exports = TradingService;