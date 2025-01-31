const { WebSocketServer } = require('ws');
const { TradingEngine } = require('../ai_engine/trading_engine');
const { ethers } = require('ethers');
const followTradeABI = require('../contracts/FollowTrade.json');

class RealTimeService {
    constructor(config) {
        this.tradingEngine = new TradingEngine(config.apiKey, config.apiSecret);
        this.provider = new ethers.providers.JsonRpcProvider(config.rpcUrl);
        this.wallet = new ethers.Wallet(config.privateKey, this.provider);
        this.followTradeContract = new ethers.Contract(
            config.contractAddress,
            followTradeABI,
            this.wallet
        );
        
        this.wss = new WebSocketServer({ port: config.wsPort });
        this.activeSymbols = new Set();
        this.subscribers = new Map();
        this.initialize();
    }
    
    initialize() {
        // 设置WebSocket连接处理
        this.wss.on('connection', (ws) => {
            ws.on('message', async (message) => {
                try {
                    const data = JSON.parse(message);
                    switch(data.type) {
                        case 'subscribe':
                            await this.handleSubscribe(ws, data);
                            break;
                        case 'unsubscribe':
                            await this.handleUnsubscribe(ws, data);
                            break;
                    }
                } catch (error) {
                    console.error('Error processing message:', error);
                    ws.send(JSON.stringify({ type: 'error', message: error.message }));
                }
            });
        });
        
        // 启动信号生成循环
        this.startSignalGeneration();
    }
    
    async handleSubscribe(ws, data) {
        const { symbol, address } = data;
        
        // 验证用户是否有效跟随者
        const isActiveFollower = await this.followTradeContract.getFollowerStatus(address, symbol);
        if (!isActiveFollower) {
            ws.send(JSON.stringify({
                type: 'error',
                message: 'Not an active follower for this symbol'
            }));
            return;
        }
        
        // 添加到订阅列表
        if (!this.subscribers.has(symbol)) {
            this.subscribers.set(symbol, new Set());
        }
        this.subscribers.get(symbol).add(ws);
        this.activeSymbols.add(symbol);
        
        ws.send(JSON.stringify({
            type: 'subscribed',
            symbol: symbol
        }));
    }
    
    async handleUnsubscribe(ws, data) {
        const { symbol } = data;
        if (this.subscribers.has(symbol)) {
            this.subscribers.get(symbol).delete(ws);
            if (this.subscribers.get(symbol).size === 0) {
                this.subscribers.delete(symbol);
                this.activeSymbols.delete(symbol);
            }
        }
    }
    
    async startSignalGeneration() {
        const INTERVAL = 1000; // 1秒更新间隔
        const MAX_RETRIES = 3;
        let performanceMetrics = new Map();

        setInterval(async () => {
            for (const symbol of this.activeSymbols) {
                try {
                    const startTime = Date.now();
                    let retries = 0;
                    let marketData;

                    // 带重试的市场数据获取
                    while (retries < MAX_RETRIES && !marketData) {
                        marketData = await this.tradingEngine.fetch_market_data(symbol);
                        if (!marketData) {
                            retries++;
                            await new Promise(resolve => setTimeout(resolve, 1000 * retries));
                        }
                    }

                    if (!marketData) {
                        throw new Error(`Failed to fetch market data for ${symbol} after ${MAX_RETRIES} retries`);
                    }

                    // 获取投资组合价值
                    const portfolioValue = await this.getPortfolioValue(symbol);

                    // 生成交易信号
                    const signal = await this.tradingEngine.generate_trading_signal(
                        marketData,
                        portfolioValue
                    );

                    // 评估交易风险
                    const riskAssessment = await this.assessTradeRisk(signal, marketData);

                    // 记录性能指标
                    const processingTime = Date.now() - startTime;
                    this.updatePerformanceMetrics(symbol, processingTime);

                    // 广播信号
                    if (signal && signal.signal !== 0 && signal.confidence > 0.7 && riskAssessment.riskScore < 0.8) {
                        signal.position_size = riskAssessment.recommendedSize;
                        await this.broadcastSignal(symbol, signal);
                    }

                } catch (error) {
                    console.error(`Error processing ${symbol}:`, error);
                    this.notifyError(symbol, error);
                }
            }
        }, INTERVAL);
    }

    async getPortfolioValue(symbol) {
        try {
            // 从智能合约获取跟随者的投资组合价值
            const followers = await this.followTradeContract.getFollowers(symbol);
            let totalValue = 0;
            
            for (const follower of followers) {
                const balance = await this.followTradeContract.balances(follower);
                totalValue += balance.toNumber();
            }
            
            return totalValue;
        } catch (error) {
            console.error('Error getting portfolio value:', error);
            return 1000000; // 默认值
        }
    }

    async assessTradeRisk(signal, marketData) {
        try {
            const volatility = marketData.indicators.volatility;
            const volume = marketData.ohlcv.volume.mean();
            const price = marketData.ohlcv.close.last();
            
            // 计算风险分数
            let riskScore = 0.5; // 基础风险分数
            
            // 波动率调整
            if (volatility > 0.02) riskScore += 0.2;
            if (volatility > 0.05) riskScore += 0.3;
            
            // 成交量调整
            const avgVolume = volume * price;
            if (avgVolume < 1000000) riskScore += 0.2; // 流动性风险
            
            // 市场冲击成本
            const impact = marketData.orderbook ? 
                this.tradingEngine.market_data.calculate_market_impact(marketData.orderbook, signal.position_size) :
                { buy_impact: 0, sell_impact: 0 };
            
            if (impact.buy_impact > 0.01 || impact.sell_impact > 0.01) {
                riskScore += 0.1;
            }
            
            return {
                riskScore: Math.min(riskScore, 1),
                factors: {
                    volatility,
                    volume: avgVolume,
                    impact
                },
                recommendedSize: signal.position_size * (1 - riskScore)
            };
        } catch (error) {
            console.error('Error assessing trade risk:', error);
            return {
                riskScore: 1,
                factors: {},
                recommendedSize: 0
            };
        }
    }

    updatePerformanceMetrics(symbol, latency) {
        if (!this.performanceMetrics) {
            this.performanceMetrics = new Map();
        }
        
        const metrics = this.performanceMetrics.get(symbol) || {
            latencies: [],
            errors: 0,
            signalCount: 0
        };
        
        metrics.latencies.push(latency);
        metrics.signalCount++;
        
        if (metrics.latencies.length > 100) {
            metrics.latencies.shift();
        }
        
        this.performanceMetrics.set(symbol, metrics);
    }

    notifyError(symbol, error) {
        const subscribers = this.subscribers.get(symbol);
        if (!subscribers) return;

        const errorMessage = JSON.stringify({
            type: 'error',
            symbol,
            message: error.message,
            timestamp: Date.now()
        });

        subscribers.forEach(ws => {
            if (ws.readyState === ws.OPEN) {
                ws.send(errorMessage);
            }
        });

        this.updateErrorMetrics(symbol, error);
    }

    updateErrorMetrics(symbol, error) {
        if (!this.errorMetrics) {
            this.errorMetrics = new Map();
        }
        
        const metrics = this.errorMetrics.get(symbol) || {
            count: 0,
            lastError: null,
            timestamp: null
        };
        
        metrics.count++;
        metrics.lastError = error.message;
        metrics.timestamp = Date.now();
        
        this.errorMetrics.set(symbol, metrics);
    }

    async getPortfolioValue(symbol) {
        try {
            // 从智能合约获取跟随者的投资组合价值
            const followers = await this.followTradeContract.getFollowers(symbol);
            let totalValue = 0;
            
            for (const follower of followers) {
                const balance = await this.followTradeContract.balances(follower);
                totalValue += balance.toNumber();
            }
            
            return totalValue;
        } catch (error) {
            console.error('Error getting portfolio value:', error);
            return 1000000; // 默认值
        }
    }

    async assessTradeRisk(signal, marketData) {
        try {
            const volatility = marketData.indicators.volatility;
            const volume = marketData.ohlcv.volume.mean();
            const price = marketData.ohlcv.close.last();
            
            // 计算风险分数
            let riskScore = 0.5; // 基础风险分数
            
            // 波动率调整
            if (volatility > 0.02) riskScore += 0.2;
            if (volatility > 0.05) riskScore += 0.3;
            
            // 成交量调整
            const avgVolume = volume * price;
            if (avgVolume < 1000000) riskScore += 0.2; // 流动性风险
            
            // 市场冲击成本
            const impact = marketData.orderbook ? 
                this.tradingEngine.market_data.calculate_market_impact(marketData.orderbook, signal.position_size) :
                { buy_impact: 0, sell_impact: 0 };
            
            if (impact.buy_impact > 0.01 || impact.sell_impact > 0.01) {
                riskScore += 0.1;
            }
            
            return {
                riskScore: Math.min(riskScore, 1),
                factors: {
                    volatility,
                    volume: avgVolume,
                    impact
                },
                recommendedSize: signal.position_size * (1 - riskScore)
            };
        } catch (error) {
            console.error('Error assessing trade risk:', error);
            return {
                riskScore: 1,
                factors: {},
                recommendedSize: 0
            };
        }
    }

    updatePerformanceMetrics(symbol, latency) {
        if (!this.performanceMetrics) {
            this.performanceMetrics = new Map();
        }
        
        const metrics = this.performanceMetrics.get(symbol) || {
            latencies: [],
            errors: 0,
            signalCount: 0
        };
        
        metrics.latencies.push(latency);
        metrics.signalCount++;
        
        if (metrics.latencies.length > 100) {
            metrics.latencies.shift();
        }
        
        this.performanceMetrics.set(symbol, metrics);
    }

    updateErrorMetrics(symbol, error) {
        if (!this.errorMetrics) {
            this.errorMetrics = new Map();
        }
        
        const metrics = this.errorMetrics.get(symbol) || {
            count: 0,
            lastError: null,
            timestamp: null
        };
        
        metrics.count++;
        metrics.lastError = error.message;
        metrics.timestamp = Date.now();
        
        this.errorMetrics.set(symbol, metrics);
    }
}

module.exports = { RealTimeService };