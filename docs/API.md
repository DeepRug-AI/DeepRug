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

# DeepRug API 文档

[Chinese documentation content...]