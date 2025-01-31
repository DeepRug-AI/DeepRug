# DeepRug 开发者文档

## 项目架构

### 系统组件

1. 智能合约
   - FollowTrade.sol: 跟随交易核心合约
   - 实现用户跟随、利润分配、代币销毁等功能

2. 交易引擎
   - 位于 src/ai_engine 目录
   - market_data.py: 市场数据采集和处理
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

1. 安装 Node.js 依赖
```bash
npm install
```

2. 安装 Python 依赖
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

### 4. 启动 AI 引擎
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
创建 .env 文件：
```
PRIVATE_KEY=your_private_key
INFURA_API_KEY=your_infura_key
FOLLOW_FEE=1000000000000000000
BURN_RATE=10
```

### 2. 编译合约
```bash
npx hardhat compile
```

### 3. 部署到测试网
```bash
npx hardhat run scripts/deploy.js --network goerli
```

### 4. 验证合约
```bash
npx hardhat verify --network goerli DEPLOYED_CONTRACT_ADDRESS
```

## 代码规范

### Solidity
- 使用 Solidity 风格指南
- 使用 SafeMath 进行算术运算
- 事件记录关键操作

### JavaScript
- 使用 ESLint 进行代码检查
- 遵循 Airbnb JavaScript 风格指南
- 使用 async/await 处理异步操作

### Python
- 遵循 PEP 8 规范
- 使用类型注解
- 编写单元测试

## 调试指南

### 智能合约调试
1. 使用 Hardhat Console.log
2. 使用 Remix IDE 在线调试
3. 检查交易收据和事件日志

### 服务调试
1. 使用 WebSocket 客户端工具测试连接
2. 检查服务日志
3. 使用 Postman 测试 API

### AI引擎调试
1. 启用详细日志输出
2. 使用 Python debugger (pdb)
3. 监控模型性能指标

## 常见问题

### 1. 合约部署失败
- 检查网络连接
- 确认账户余额充足
- 验证 gas 设置

### 2. 跟随交易失败
- 检查 followFee 设置
- 确认用户余额充足
- 验证交易对是否支持

### 3. AI模型性能问题
- 检查数据质量
- 调整模型参数
- 优化特征工程

## 贡献指南

1. Fork 项目仓库
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

## 安全建议

1. 定期更新依赖包
2. 使用环境变量存储敏感信息
3. 实施访问控制
4. 进行安全审计
5. 监控异常活动