# DeepRug API 文档

## 智能合约接口

### FollowTrade 合约

#### 状态变量

- `owner` (address): 合约拥有者地址
- `followFee` (uint256): 跟随交易所需费用
- `burnRate` (uint256): 代币销毁比率（0-50%）
- `totalBurned` (uint256): 总销毁代币数量
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

#### 函数

##### startFollow
```solidity
function startFollow(string memory symbol) external payable
```
开始跟随交易。
- 参数：
  - `symbol`: 交易对符号
- 要求：
  - 支付的费用必须大于等于 followFee
  - 用户不能重复跟随同一交易对

##### distributeProfits
```solidity
function distributeProfits(address[] calldata followers, uint256[] calldata amounts) external onlyOwner
```
分配利润。
- 参数：
  - `followers`: 跟随者地址数组
  - `amounts`: 对应的利润金额数组
- 分配规则：
  - 交易者获得 70% 利润
  - 跟随者获得 30% 利润

##### withdrawRewards
```solidity
function withdrawRewards() external
```
提取交易奖励。

##### withdraw
```solidity
function withdraw() external
```
提取账户余额。

##### updateFollowFee
```solidity
function updateFollowFee(uint256 _newFee) external onlyOwner
```
更新跟随费用。

##### updateBurnRate
```solidity
function updateBurnRate(uint256 _newRate) external onlyOwner
```
更新代币销毁比率。

## 交易服务 API

### WebSocket 接口

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

##### 交易信号
```javascript
{
  "type": "trade_signal",
  "trader": "<trader_address>",
  "symbol": "<trading_pair>",
  "signal": {
    // 交易信号详情
  }
}
```

##### 利润分配通知
```javascript
{
  "type": "profit_distribution",
  "trader": "<trader_address>",
  "symbol": "<trading_pair>",
  "amount": "<profit_amount>"
}
```

## 错误处理

### 智能合约错误

- `Only owner can call this function`: 仅合约拥有者可调用
- `Insufficient follow fee`: 跟随费用不足
- `Already following this symbol`: 已在跟随该交易对
- `Not an active follower`: 非活跃跟随者
- `No rewards to withdraw`: 无可提取奖励
- `No balance to withdraw`: 账户余额为零
- `Burn rate cannot exceed 50%`: 销毁比率不能超过 50%

### WebSocket 错误

错误消息格式：
```javascript
{
  "type": "error",
  "message": "<error_message>"
}
```

## 安全性考虑

1. 所有金额计算都使用 SafeMath 库防止溢出
2. 关键操作需要权限验证
3. 资金转移操作有余额检查
4. WebSocket 连接需要签名验证

## 性能优化

1. 批量处理利润分配以节省 gas
2. 使用事件通知减少区块链查询
3. WebSocket 保持长连接提高实时性