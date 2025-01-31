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

# DeepRug 开发者文档

[Chinese documentation content...]