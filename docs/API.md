# DeepRug API Documentation

## Smart Contract Interfaces

### FollowTrade Contract

#### State Variables

- `owner` (address): Contract owner's address
- `followFee` (uint256): Fee required for following trades
- `burnRate` (uint256): Token burn rate (0-50%)
- `totalBurned` (uint256): Total amount of tokens burned
- `balances` (mapping): User balance mapping
- `activeFollows` (mapping): User active follow status
- `traderRewards` (mapping): Trader reward balances

#### Events

```solidity
event FollowTradeStarted(address follower, string symbol, uint256 fee)
event ProfitDistributed(address trader, address follower, uint256 amount)
event TokensBurned(uint256 amount)
event RewardsWithdrawn(address user, uint256 amount)
```

#### Functions

##### startFollow
```solidity
function startFollow(string memory symbol) external payable
```
Start following a trade.
- Parameters:
  - `symbol`: Trading pair symbol
- Requirements:
  - Paid fee must be greater than or equal to followFee
  - User cannot follow the same trading pair multiple times

##### distributeProfits
```solidity
function distributeProfits(address[] calldata followers, uint256[] calldata amounts) external onlyOwner
```
Distribute profits.
- Parameters:
  - `followers`: Array of follower addresses
  - `amounts`: Array of corresponding profit amounts
- Distribution rules:
  - Trader receives 70% of profits
  - Follower receives 30% of profits

##### withdrawRewards
```solidity
function withdrawRewards() external
```
Withdraw trading rewards.

##### withdraw
```solidity
function withdraw() external
```
Withdraw account balance.

##### updateFollowFee
```solidity
function updateFollowFee(uint256 _newFee) external onlyOwner
```
Update follow fee.

##### updateBurnRate
```solidity
function updateBurnRate(uint256 _newRate) external onlyOwner
```
Update token burn rate.

## Trading Service API

### WebSocket Interface

#### Connection
```javascript
ws://localhost:8081
```

#### Message Types

##### Follow Request
```javascript
{
  "type": "follow_request",
  "trader": "<trader_address>",
  "symbol": "<trading_pair>",
  "publicKey": "<follower_public_key>"
}
```

##### Unfollow Request
```javascript
{
  "type": "unfollow_request",
  "trader": "<trader_address>",
  "symbol": "<trading_pair>"
}
```

---

[点击查看中文文档]

# DeepRug API 文档

## 智能合约接口

### 跟随交易合约

#### 状态变量

- `owner` (address): 合约所有者地址
- `followFee` (uint256): 跟随交易所需的费用
- `burnRate` (uint256): 代币销毁比率（0-50%）
- `totalBurned` (uint256): 已销毁代币总量
- `balances` (mapping): 用户余额映射
- `activeFollows` (mapping): 用户活跃跟随状态
- `traderRewards` (mapping): 交易者奖励余额

#### 事件

```solidity
event FollowTradeStarted(address follower, string symbol, uint256 fee)
event ProfitDistributed(address trader, address follower, uint256 amount)
event TokensBurned(uint256 amount)
event RewardsWithdrawn(address user, uint256 amount)
```

事件说明：
- FollowTradeStarted：开始跟随交易时触发
- ProfitDistributed：分配利润时触发
- TokensBurned：代币销毁时触发
- RewardsWithdrawn：提取奖励时触发

#### 函数

##### 开始跟随
```solidity
function startFollow(string memory symbol) external payable
```
开始跟随一个交易。
- 参数:
  - `symbol`: 交易对符号
- 要求:
  - 支付的费用必须大于或等于跟随费用
  - 用户不能多次跟随同一个交易对

##### 分配利润
```solidity
function distributeProfits(address[] calldata followers, uint256[] calldata amounts) external onlyOwner
```
分配利润。
- 参数:
  - `followers`: 跟随者地址数组
  - `amounts`: 对应的利润金额数组
- 分配规则:
  - 交易者获得70%的利润
  - 跟随者获得30%的利润

##### 提取奖励
```solidity
function withdrawRewards() external
```
提取交易奖励。

##### 提取余额
```solidity
function withdraw() external
```
提取账户余额。

##### 更新跟随费用
```solidity
function updateFollowFee(uint256 _newFee) external onlyOwner
```
更新跟随费用。

##### 更新销毁比率
```solidity
function updateBurnRate(uint256 _newRate) external onlyOwner
```
更新代币销毁比率。

## 交易服务API

### WebSocket接口

#### 连接
```javascript
ws://localhost:8081
```

#### 消息类型

##### 跟随请求
```javascript
{
  "type": "follow_request",
  "trader": "<trader_address>",
  "symbol": "<trading_pair>",
  "publicKey": "<follower_public_key>"
}
```

##### 取消跟随请求
```javascript
{
  "type": "unfollow_request",
  "trader": "<trader_address>",
  "symbol": "<trading_pair>"
}
```