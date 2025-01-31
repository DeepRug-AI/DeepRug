// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SocialInteraction {
    // State variables
    address public owner;
    uint256 public tradingCompetitionId;
    uint256 public minimumStakeAmount;
    
    struct TradingCompetition {
        uint256 startTime;
        uint256 endTime;
        uint256 prizePool;
        mapping(address => uint256) participantScores;
        address[] participants;
        bool isActive;
    }
    
    struct CommunityPost {
        address author;
        string content;
        uint256 timestamp;
        uint256 likes;
        mapping(address => bool) hasLiked;
    }
    
    mapping(uint256 => TradingCompetition) public competitions;
    mapping(uint256 => CommunityPost) public posts;
    uint256 public postCount;
    mapping(address => uint256) public userStakes;
    
    // Events
    event CompetitionStarted(uint256 indexed competitionId, uint256 startTime, uint256 endTime);
    event CompetitionEnded(uint256 indexed competitionId, address[] winners);
    event PostCreated(uint256 indexed postId, address indexed author, string content);
    event PostLiked(uint256 indexed postId, address indexed liker);
    event UserStaked(address indexed user, uint256 amount);
    
    constructor(uint256 _minimumStakeAmount) {
        owner = msg.sender;
        minimumStakeAmount = _minimumStakeAmount;
        tradingCompetitionId = 0;
        postCount = 0;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier hasStaked() {
        require(userStakes[msg.sender] >= minimumStakeAmount, "Must stake minimum amount");
        _;
    }
    
    // Trading Competition Functions
    function startCompetition(uint256 _duration) external onlyOwner {
        tradingCompetitionId++;
        uint256 startTime = block.timestamp;
        uint256 endTime = startTime + _duration;
        
        TradingCompetition storage competition = competitions[tradingCompetitionId];
        competition.startTime = startTime;
        competition.endTime = endTime;
        competition.isActive = true;
        
        emit CompetitionStarted(tradingCompetitionId, startTime, endTime);
    }
    
    function joinCompetition() external hasStaked {
        TradingCompetition storage competition = competitions[tradingCompetitionId];
        require(competition.isActive, "No active competition");
        require(block.timestamp < competition.endTime, "Competition ended");
        
        competition.participants.push(msg.sender);
        competition.participantScores[msg.sender] = 0;
    }
    
    function updateScore(address participant, uint256 score) external onlyOwner {
        TradingCompetition storage competition = competitions[tradingCompetitionId];
        require(competition.isActive, "No active competition");
        competition.participantScores[participant] = score;
    }
    
    function endCompetition() external onlyOwner {
        TradingCompetition storage competition = competitions[tradingCompetitionId];
        require(competition.isActive, "No active competition");
        require(block.timestamp >= competition.endTime, "Competition still ongoing");
        
        competition.isActive = false;
        
        // Calculate winners (top 3)
        address[] memory winners = new address[](3);
        uint256[] memory topScores = new uint256[](3);
        
        for (uint256 i = 0; i < competition.participants.length; i++) {
            address participant = competition.participants[i];
            uint256 score = competition.participantScores[participant];
            
            for (uint256 j = 0; j < 3; j++) {
                if (score > topScores[j]) {
                    // Shift lower scores down
                    for (uint256 k = 2; k > j; k--) {
                        topScores[k] = topScores[k-1];
                        winners[k] = winners[k-1];
                    }
                    topScores[j] = score;
                    winners[j] = participant;
                    break;
                }
            }
        }
        
        emit CompetitionEnded(tradingCompetitionId, winners);
    }
    
    // Community Interaction Functions
    function createPost(string memory content) external hasStaked {
        postCount++;
        CommunityPost storage post = posts[postCount];
        post.author = msg.sender;
        post.content = content;
        post.timestamp = block.timestamp;
        post.likes = 0;
        
        emit PostCreated(postCount, msg.sender, content);
    }
    
    function likePost(uint256 postId) external hasStaked {
        CommunityPost storage post = posts[postId];
        require(!post.hasLiked[msg.sender], "Already liked this post");
        
        post.likes++;
        post.hasLiked[msg.sender] = true;
        
        emit PostLiked(postId, msg.sender);
    }
    
    // Staking Functions
    function stake() external payable {
        require(msg.value > 0, "Must stake some amount");
        userStakes[msg.sender] += msg.value;
        emit UserStaked(msg.sender, msg.value);
    }
    
    function withdraw(uint256 amount) external {
        require(userStakes[msg.sender] >= amount, "Insufficient stake");
        userStakes[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
    }
}