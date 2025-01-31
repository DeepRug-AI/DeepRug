# DeepRug Developer Documentation

## Project Architecture

### System Components

1. Smart Contracts
   - FollowTrade.sol: Core contract for follow trading
   - Implements user following, profit distribution, token burning functionalities

2. Trading Engine
   - Located in src/ai_engine directory
   - market_data.py: Market data collection and processing
   - ml_models.py: Machine learning models
   - risk_manager.py: Risk management module
   - trading_engine.py: Trading strategy execution

3. Service Layer
   - follow_trade_service.js: Follow trading service
   - trading_service.js: Trade execution service

### Tech Stack

- Smart Contracts: Solidity ^0.8.0
- Backend Services: Node.js
- AI Engine: Python
- WebSocket: Real-time communication

## Environment Setup

### Prerequisites

- Node.js >= 14.0.0
- Python >= 3.8
- Solidity ^0.8.0
- Hardhat or Truffle (Smart contract development framework)

### Dependencies Installation

1. Install Node.js dependencies
```bash
npm install
```

2. Install Python dependencies
```bash
pip install -r requirements.txt
```

## Local Development

### 1. Start Local Blockchain
```bash
npx hardhat node
```

### 2. Deploy Smart Contracts
```bash
npx hardhat run scripts/deploy.js --network localhost
```

### 3. Start Trading Service
```bash
node src/index.js
```

### 4. Start AI Engine
```bash
python src/ai_engine/trading_engine.py
```

## Testing

### Smart Contract Tests
```bash
npx hardhat test
```

### AI Engine Tests
```bash
python -m pytest tests/ai_engine
```

## Deployment Process

### 1. Prepare Environment Variables
Create .env file:
```
PRIVATE_KEY=your_private_key
INFURA_API_KEY=your_infura_key
FOLLOW_FEE=1000000000000000000
BURN_RATE=10
```

### 2. Compile Contracts
```bash
npx hardhat compile
```

### 3. Deploy to Testnet
```bash
npx hardhat run scripts/deploy.js --network testnet
```

---

[点击查看中文文档]

# DeepRug 开发者文档

## 项目架构

### 系统组件

1. 智能合约
   - FollowTrade.sol: 跟随交易的核心合约
   - 实现用户跟随、利润分配、代币销毁等功能

2. 交易引擎
   - 位于src/ai_engine目录
   - market_data.py: 市场数据收集和处理
   - ml_models.py: 机器学习模型
   - risk_manager.py: 风险管理模块
   - trading_engine.py: 交易策略执行

3. 服务层
   - follow_trade_service.js: 跟随交易服务
   - trading_service.js: 交易执行服务

### 技术栈

- 智能合约: Solidity ^0.8.0
- 后端服务: Node.js
- AI引擎: Python
- WebSocket: 实时通信

## 环境配置

### 前置要求

- Node.js >= 14.0.0
- Python >= 3.8
- Solidity ^0.8.0
- Hardhat 或 Truffle (智能合约开发框架)

### 依赖安装

1. 安装Node.js依赖
```bash
npm install
```

2. 安装Python依赖
```bash
pip install -r requirements.txt
```

## 本地开发

### 1. 启动本地区块链
```bash
npx hardhat node
```

### 2. 部署智能合约
```bash
npx hardhat run scripts/deploy.js --network localhost
```

### 3. 启动交易服务
```bash
node src/index.js
```

### 4. 启动AI引擎
```bash
python src/ai_engine/trading_engine.py
```

## 测试

### 智能合约测试
```bash
npx hardhat test
```

### AI引擎测试
```bash
python -m pytest tests/ai_engine
```

## 部署流程

### 1. 准备环境变量
创建.env文件：
```
PRIVATE_KEY=你的私钥
INFURA_API_KEY=你的Infura密钥
FOLLOW_FEE=1000000000000000000
BURN_RATE=10
```

### 2. 编译合约
```bash
npx hardhat compile
```

### 3. 部署到测试网
```bash
npx hardhat run scripts/deploy.js --network testnet
```
