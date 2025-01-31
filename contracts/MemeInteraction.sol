// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MemeInteraction {
    // State variables
    address public owner;
    uint256 public memeCount;
    uint256 public minimumStakeAmount;
    
    struct Meme {
        address creator;
        string content;
        string imageHash;
        uint256 timestamp;
        uint256 likes;
        uint256 shares;
        mapping(address => bool) hasLiked;
        mapping(address => bool) hasShared;
    }
    
    mapping(uint256 => Meme) public memes;
    mapping(address => uint256[]) public userMemes;
    mapping(address => uint256) public userReputation;
    
    // Events
    event MemeCreated(uint256 indexed memeId, address indexed creator, string content, string imageHash);
    event MemeLiked(uint256 indexed memeId, address indexed liker);
    event MemeShared(uint256 indexed memeId, address indexed sharer);
    event ReputationUpdated(address indexed user, uint256 newReputation);
    
    constructor(uint256 _minimumStakeAmount) {
        owner = msg.sender;
        minimumStakeAmount = _minimumStakeAmount;
        memeCount = 0;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    // Meme Creation and Interaction Functions
    function createMeme(string memory content, string memory imageHash) external {
        memeCount++;
        Meme storage meme = memes[memeCount];
        meme.creator = msg.sender;
        meme.content = content;
        meme.imageHash = imageHash;
        meme.timestamp = block.timestamp;
        meme.likes = 0;
        meme.shares = 0;
        
        userMemes[msg.sender].push(memeCount);
        userReputation[msg.sender] += 1;
        
        emit MemeCreated(memeCount, msg.sender, content, imageHash);
        emit ReputationUpdated(msg.sender, userReputation[msg.sender]);
    }
    
    function likeMeme(uint256 memeId) external {
        Meme storage meme = memes[memeId];
        require(!meme.hasLiked[msg.sender], "Already liked this meme");
        
        meme.likes++;
        meme.hasLiked[msg.sender] = true;
        userReputation[meme.creator] += 1;
        
        emit MemeLiked(memeId, msg.sender);
        emit ReputationUpdated(meme.creator, userReputation[meme.creator]);
    }
    
    function shareMeme(uint256 memeId) external {
        Meme storage meme = memes[memeId];
        require(!meme.hasShared[msg.sender], "Already shared this meme");
        
        meme.shares++;
        meme.hasShared[msg.sender] = true;
        userReputation[meme.creator] += 2;
        userReputation[msg.sender] += 1;
        
        emit MemeShared(memeId, msg.sender);
        emit ReputationUpdated(meme.creator, userReputation[meme.creator]);
        emit ReputationUpdated(msg.sender, userReputation[msg.sender]);
    }
    
    // Reputation Management Functions
    function getReputation(address user) external view returns (uint256) {
        return userReputation[user];
    }
    
    function getUserMemes(address user) external view returns (uint256[] memory) {
        return userMemes[user];
    }
    
    // Admin Functions
    function updateMinimumStakeAmount(uint256 _newAmount) external onlyOwner {
        minimumStakeAmount = _newAmount;
    }
}