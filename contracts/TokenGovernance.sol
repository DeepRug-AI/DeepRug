// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TokenGovernance {
    // State variables
    address public owner;
    uint256 public proposalCount;
    uint256 public minimumStakeForProposal;
    uint256 public votingPeriod;
    
    struct Proposal {
        address proposer;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 forVotes;
        uint256 againstVotes;
        bool executed;
        mapping(address => bool) hasVoted;
        mapping(address => uint256) stakedAmount;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(address => uint256) public userStakes;
    mapping(address => uint256) public votingPower;
    
    // Events
    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string description);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId);
    event TokensStaked(address indexed user, uint256 amount);
    event TokensUnstaked(address indexed user, uint256 amount);
    
    constructor(uint256 _minimumStakeForProposal, uint256 _votingPeriod) {
        owner = msg.sender;
        minimumStakeForProposal = _minimumStakeForProposal;
        votingPeriod = _votingPeriod;
        proposalCount = 0;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    // Staking Functions
    function stake() external payable {
        require(msg.value > 0, "Must stake some amount");
        userStakes[msg.sender] += msg.value;
        votingPower[msg.sender] = calculateVotingPower(msg.sender);
        emit TokensStaked(msg.sender, msg.value);
    }
    
    function unstake(uint256 amount) external {
        require(userStakes[msg.sender] >= amount, "Insufficient stake");
        require(canUnstake(msg.sender, amount), "Tokens locked in active proposals");
        
        userStakes[msg.sender] -= amount;
        votingPower[msg.sender] = calculateVotingPower(msg.sender);
        payable(msg.sender).transfer(amount);
        
        emit TokensUnstaked(msg.sender, amount);
    }
    
    // Governance Functions
    function createProposal(string memory description) external {
        require(userStakes[msg.sender] >= minimumStakeForProposal, "Insufficient stake to create proposal");
        
        proposalCount++;
        Proposal storage proposal = proposals[proposalCount];
        proposal.proposer = msg.sender;
        proposal.description = description;
        proposal.startTime = block.timestamp;
        proposal.endTime = block.timestamp + votingPeriod;
        
        emit ProposalCreated(proposalCount, msg.sender, description);
    }
    
    function castVote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp <= proposal.endTime, "Voting period ended");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        require(votingPower[msg.sender] > 0, "No voting power");
        
        uint256 weight = votingPower[msg.sender];
        if (support) {
            proposal.forVotes += weight;
        } else {
            proposal.againstVotes += weight;
        }
        
        proposal.hasVoted[msg.sender] = true;
        proposal.stakedAmount[msg.sender] = userStakes[msg.sender];
        
        emit VoteCast(proposalId, msg.sender, support, weight);
    }
    
    function executeProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp > proposal.endTime, "Voting period not ended");
        require(!proposal.executed, "Proposal already executed");
        
        proposal.executed = true;
        
        emit ProposalExecuted(proposalId);
    }
    
    // Helper Functions
    function calculateVotingPower(address user) public view returns (uint256) {
        return userStakes[user];
    }
    
    function canUnstake(address user, uint256 amount) internal view returns (bool) {
        uint256 lockedAmount = 0;
        for (uint256 i = 1; i <= proposalCount; i++) {
            Proposal storage proposal = proposals[i];
            if (!proposal.executed && proposal.hasVoted[user]) {
                lockedAmount += proposal.stakedAmount[user];
            }
        }
        return userStakes[user] - lockedAmount >= amount;
    }
    
    // Admin Functions
    function updateMinimumStakeForProposal(uint256 _newAmount) external onlyOwner {
        minimumStakeForProposal = _newAmount;
    }
    
    function updateVotingPeriod(uint256 _newPeriod) external onlyOwner {
        votingPeriod = _newPeriod;
    }
}