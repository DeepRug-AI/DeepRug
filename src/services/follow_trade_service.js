const { Connection, PublicKey, Transaction, SystemProgram } = require('@solana/web3.js');
const BN = require('bn.js');
const { Program } = require('@project-serum/anchor');
const WebSocket = require('ws');

class FollowTradeService {
    constructor(endpoint, programId) {
        this.connection = new Connection(endpoint);
        this.programId = new PublicKey(programId);
        
        // Initialize WebSocket server for real-time updates
        this.wss = new WebSocket.Server({ port: 8081 });
        this.followers = new Map();
        
        this.setupWebSocket();
    }
    
    setupWebSocket() {
        this.wss.on('connection', (ws) => {
            ws.on('message', async (message) => {
                try {
                    const data = JSON.parse(message);
                    
                    switch (data.type) {
                        case 'follow_request':
                            await this.handleFollowRequest(ws, data);
                            break;
                        case 'unfollow_request':
                            await this.handleUnfollowRequest(ws, data);
                            break;
                    }
                } catch (error) {
                    console.error('Error processing WebSocket message:', error);
                    ws.send(JSON.stringify({
                        type: 'error',
                        message: error.message
                    }));
                }
            });
            
            ws.on('close', () => {
                this.removeFollower(ws);
            });
        });
    }
    
    async handleFollowRequest(ws, data) {
        const { trader, symbol, publicKey } = data;
        
        try {
            // Create follow instruction
            const instruction = await this.program.instruction.startFollow(
                symbol,
                {
                    accounts: {
                        follower: new PublicKey(publicKey),
                        trader: new PublicKey(trader),
                        systemProgram: SystemProgram.programId,
                    },
                }
            );
            
            // Add to followers list
            this.followers.set(ws, {
                publicKey,
                trader,
                symbol
            });
            
            // Send confirmation
            ws.send(JSON.stringify({
                type: 'follow_success',
                trader,
                symbol
            }));
        } catch (error) {
            ws.send(JSON.stringify({
                type: 'error',
                message: 'Failed to start following: ' + error.message
            }));
        }
    }
    
    async handleUnfollowRequest(ws, data) {
        const follower = this.followers.get(ws);
        if (!follower) {
            return;
        }
        
        try {
            // Remove from followers list
            this.followers.delete(ws);
            
            // Send confirmation
            ws.send(JSON.stringify({
                type: 'unfollow_success',
                trader: follower.trader,
                symbol: follower.symbol
            }));
        } catch (error) {
            ws.send(JSON.stringify({
                type: 'error',
                message: 'Failed to unfollow: ' + error.message
            }));
        }
    }
    
    removeFollower(ws) {
        this.followers.delete(ws);
    }
    
    broadcastTradeSignal(trader, symbol, signal) {
        this.followers.forEach((follower, ws) => {
            if (follower.trader === trader && 
                follower.symbol === symbol && 
                ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'trade_signal',
                    trader,
                    symbol,
                    signal
                }));
            }
        });
    }
    
    async distributeProfits(trader, symbol, profits) {
        const followers = Array.from(this.followers.values())
            .filter(f => f.trader === trader && f.symbol === symbol);
        
        if (followers.length === 0) {
            return;
        }
        
        try {
            // Calculate profit shares
            const traderShare = (profits * 70) / 100; // 70% to trader
            const followerShare = (profits * 30) / followers.length; // 30% split among followers
            
            // Create profit distribution instruction
            const instruction = await this.program.instruction.distributeProfit(
                new BN(profits),
                {
                    accounts: {
                        trader: new PublicKey(trader),
                        // Add other required accounts
                    },
                }
            );
            
            // Broadcast profit distribution
            followers.forEach(({ publicKey }, ws) => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'profit_distribution',
                        trader,
                        symbol,
                        amount: followerShare
                    }));
                }
            });
        } catch (error) {
            console.error('Error distributing profits:', error);
        }
    }
}

module.exports = FollowTradeService;