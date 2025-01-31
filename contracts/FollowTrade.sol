// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FollowTrade {
    // State variables
    address public owner;
    uint256 public followFee;
    uint256 public burnRate;
    uint256 public totalBurned;
    mapping(address => uint256) public balances;
    mapping(address => mapping(string => bool)) public activeFollows;
    mapping(address => uint256) public traderRewards;
    
    // Events
    event FollowTradeStarted(address follower, string symbol, uint256 fee);
    event ProfitDistributed(address trader, address follower, uint256 amount);
    event TokensBurned(uint256 amount);
    event RewardsWithdrawn(address user, uint256 amount);
    
    constructor(uint256 _followFee, uint256 _burnRate) {
        require(_burnRate <= 50, "Burn rate cannot exceed 50%");
        owner = msg.sender;
        followFee = _followFee;
        burnRate = _burnRate;
    }
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;    
    }
    
    modifier onlyActiveFollower(string memory symbol) {
        require(activeFollows[msg.sender][symbol], "Not an active follower");
        _;
    }
    
    // Follow trade function
    function startFollow(string memory symbol) external payable {
        require(msg.value >= followFee, "Insufficient follow fee");
        require(!activeFollows[msg.sender][symbol], "Already following this symbol");
        
        // Calculate burn amount
        uint256 burnAmount = (followFee * burnRate) / 100;
        uint256 systemAmount = followFee - burnAmount;
        
        // Update state
        activeFollows[msg.sender][symbol] = true;
        balances[owner] += systemAmount;
        totalBurned += burnAmount;
        
        // Burn tokens
        address deadAddress = address(0);
        payable(deadAddress).transfer(burnAmount);
        
        // Refund excess payment
        if (msg.value > followFee) {
            payable(msg.sender).transfer(msg.value - followFee);
        }
        
        emit FollowTradeStarted(msg.sender, symbol, followFee);
        emit TokensBurned(burnAmount);
    }
    
    // Distribute profits
    function distributeProfits(address[] calldata followers, uint256[] calldata amounts) external onlyOwner {
        require(followers.length == amounts.length, "Arrays length mismatch");
        
        for (uint256 i = 0; i < followers.length; i++) {
            address follower = followers[i];
            uint256 amount = amounts[i];
            
            require(balances[owner] >= amount, "Insufficient balance");
            
            // Calculate profit shares
            uint256 traderShare = (amount * 70) / 100;  // 70% to trader
            uint256 followerShare = amount - traderShare;  // 30% to follower
            
            // Update balances
            balances[owner] -= amount;
            balances[follower] += followerShare;
            traderRewards[msg.sender] += traderShare;
            
            emit ProfitDistributed(msg.sender, follower, amount);
        }
    }
    
    // Withdraw rewards
    function withdrawRewards() external {
        uint256 amount = traderRewards[msg.sender];
        require(amount > 0, "No rewards to withdraw");
        
        traderRewards[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
        
        emit RewardsWithdrawn(msg.sender, amount);
    }
    
    // Withdraw balance
    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        balances[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
    
    // Update parameters
    function updateFollowFee(uint256 _newFee) external onlyOwner {
        followFee = _newFee;
    }
    
    function updateBurnRate(uint256 _newRate) external onlyOwner {
        require(_newRate <= 50, "Burn rate cannot exceed 50%");
        burnRate = _newRate;
    }
    
    // View functions
    function getFollowerStatus(address follower, string memory symbol) external view returns (bool) {
        return activeFollows[follower][symbol];
    }
    
    function getTraderRewards(address trader) external view returns (uint256) {
        return traderRewards[trader];
    }
}