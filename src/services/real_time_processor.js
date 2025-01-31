const WebSocket = require('ws');
const { MarketDataCollector } = require('../ai_engine/market_data');
const { SignalGenerator } = require('../ai_engine/signal_generator');
const { RiskManager } = require('../ai_engine/risk_manager');
const { ethers } = require('ethers');
const followTradeABI = require('../contracts/abi');

class RealTimeProcessor {
    constructor(config) {
        this.marketData = new MarketDataCollector(config.exchange);
        this.signalGenerator = new SignalGenerator();
        this.riskManager = new RiskManager();
        this.subscribers = new Map();
        this.activeSymbols = new Set();
        
        // Initialize smart contract connection
        this.provider = new ethers.providers.JsonRpcProvider(config.rpcUrl);
        this.wallet = new ethers.Wallet(config.privateKey, this.provider);
        this.followTradeContract = new ethers.Contract(
            config.contractAddress,
            followTradeABI,
            this.wallet
        );
    }

    async start() {
        this.wss = new WebSocket.Server({ port: 8082 });
        this.setupWebSocket();
        this.startDataProcessing();
        this.setupContractListeners();
    }

    setupWebSocket() {
        this.wss.on('connection', (ws) => {
            ws.on('message', async (message) => {
                try {
                    const data = JSON.parse(message);
                    await this.handleMessage(ws, data);
                } catch (error) {
                    console.error('Error processing message:', error);
                    ws.send(JSON.stringify({ type: 'error', message: error.message }));
                }
            });

            ws.on('close', () => {
                this.removeSubscriber(ws);
            });
        });
    }

    setupContractListeners() {
        // Listen for follow trade events
        this.followTradeContract.on('FollowTradeStarted', async (follower, symbol, fee) => {
            console.log(`New follow trade: ${follower} following ${symbol}`);
            await this.handleNewFollower(follower, symbol);
        });

        // Listen for profit distribution events
        this.followTradeContract.on('ProfitDistributed', (trader, follower, amount) => {
            console.log(`Profit distributed: ${amount} to ${follower} from ${trader}`);
        });
    }

    async handleNewFollower(follower, symbol) {
        try {
            // Add to active symbols if not already tracking
            if (!this.activeSymbols.has(symbol)) {
                this.activeSymbols.add(symbol);
                await this.startSymbolProcessing(symbol);
            }

            // Initialize risk parameters for the follower
            const riskMetrics = this.riskManager.get_risk_metrics();
            const initialRiskScore = 0.5; // Default risk score

            // Store follower information
            if (!this.subscribers.has(symbol)) {
                this.subscribers.set(symbol, new Map());
            }
            this.subscribers.get(symbol).set(follower, {
                riskScore: initialRiskScore,
                metrics: riskMetrics
            });
        } catch (error) {
            console.error(`Error handling new follower: ${error.message}`);
        }
    }

    async startSymbolProcessing(symbol) {
        try {
            while (this.activeSymbols.has(symbol)) {
                const marketData = await this.marketData.fetch_historical_data(symbol, '1m', 100);
                if (!marketData) continue;

                const technicalIndicators = this.signalGenerator.calculate_technical_indicators(marketData);
                const prediction = await this.signalGenerator.generate_signal(technicalIndicators);

                if (prediction) {
                    await this.processTradeSignal(symbol, prediction, technicalIndicators);
                }

                await new Promise(resolve => setTimeout(resolve, 60000)); // 1-minute interval
            }
        } catch (error) {
            console.error(`Error processing symbol ${symbol}: ${error.message}`);
        }
    }

    async processTradeSignal(symbol, prediction, indicators) {
        const subscribers = this.subscribers.get(symbol);
        if (!subscribers) return;

        for (const [follower, data] of subscribers) {
            try {
                // Calculate position size based on risk profile
                const positionSize = this.riskManager.calculate_position_size(
                    1000, // Default portfolio value, should be fetched from contract
                    indicators.volatility,
                    data.riskScore
                );

                // Generate trade parameters
                const tradeParams = {
                    symbol,
                    direction: prediction.signal > 0 ? 'long' : 'short',
                    size: positionSize,
                    stopLoss: this.riskManager.calculate_stop_loss(
                        indicators.close,
                        prediction.signal > 0 ? 'long' : 'short',
                        indicators.volatility
                    )
                };

                // Broadcast trade signal to follower
                this.broadcastTradeSignal(follower, tradeParams);
            } catch (error) {
                console.error(`Error processing trade signal for ${follower}: ${error.message}`);
            }
        }
    }

    broadcastTradeSignal(follower, tradeParams) {
        const message = {
            type: 'trade_signal',
            data: tradeParams,
            timestamp: Date.now()
        };

        // Send signal to specific follower's WebSocket connection
        const ws = Array.from(this.wss.clients).find(client => 
            client.follower === follower && client.readyState === WebSocket.OPEN
        );

        if (ws) {
            ws.send(JSON.stringify(message));
        }
    }
}

module.exports = RealTimeProcessor;