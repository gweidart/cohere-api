// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ComplexToken {
    // ========================
    // ERC20 Implementation
    // ========================
    string public name = "ComplexToken";
    string public symbol = "CTK";
    uint8 public decimals = 18;
    uint256 private _totalSupply;

    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    // ========================
    // Access Control
    // ========================
    mapping(bytes32 => mapping(address => bool)) private _roles;
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant SNAPSHOT_ROLE = keccak256("SNAPSHOT_ROLE");
    bytes32 public constant GOVERNOR_ROLE = keccak256("GOVERNOR_ROLE");

    // ========================
    // Pausable
    // ========================
    bool private _paused;

    // ========================
    // Snapshot
    // ========================
    uint256 private _currentSnapshotId;
    mapping(uint256 => mapping(address => uint256)) private _snapshots;

    // ========================
    // Governance
    // ========================
    struct Proposal {
        uint256 id;
        address proposer;
        string description;
        uint256 snapshotId;
        uint256 deadline;
        uint256 forVotes;
        uint256 againstVotes;
        bool executed;
        mapping(address => bool) voters;
    }

    uint256 private _proposalCount;
    mapping(uint256 => Proposal) private _proposals;

    // ========================
    // Events
    // ========================
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event RoleGranted(bytes32 indexed role, address indexed account, address indexed sender);
    event RoleRevoked(bytes32 indexed role, address indexed account, address indexed sender);
    event Paused(address account);
    event Unpaused(address account);
    event Snapshot(uint256 id);
    event ProposalCreated(uint256 id, address proposer, string description, uint256 snapshotId, uint256 deadline);
    event Voted(uint256 proposalId, address voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 id, bool passed);

    // ========================
    // Modifiers
    // ========================
    modifier onlyRole(bytes32 role) {
        require(hasRole(role, msg.sender), "AccessControl: sender does not have the required role");
        _;
    }

    modifier whenNotPaused() {
        require(!_paused, "Pausable: paused");
        _;
    }

    modifier whenPaused() {
        require(_paused, "Pausable: not paused");
        _;
    }

    // ========================
    // Constructor
    // ========================
    constructor(address admin) {
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(MINTER_ROLE, admin);
        _grantRole(BURNER_ROLE, admin);
        _grantRole(PAUSER_ROLE, admin);
        _grantRole(SNAPSHOT_ROLE, admin);
        _grantRole(GOVERNOR_ROLE, admin);
        _mint(admin, 1000000 * (10 ** uint256(decimals)));
    }

    // ========================
    // ERC20 Functions
    // ========================
    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }

    function transfer(address to, uint256 amount) public whenNotPaused returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function allowance(address owner, address spender) public view returns (uint256) {
        return _allowances[owner][spender];
    }

    function approve(address spender, uint256 amount) public whenNotPaused returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) public whenNotPaused returns (bool) {
        uint256 currentAllowance = _allowances[from][msg.sender];
        require(currentAllowance >= amount, "ERC20: transfer amount exceeds allowance");
        _transfer(from, to, amount);
        _approve(from, msg.sender, currentAllowance - amount);
        return true;
    }

    // ========================
    // Internal ERC20 Functions
    // ========================
    function _transfer(address from, address to, uint256 amount) internal {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");
        require(_balances[from] >= amount, "ERC20: transfer amount exceeds balance");

        _balances[from] -= amount;
        _balances[to] += amount;
        emit Transfer(from, to, amount);
    }

    function _mint(address account, uint256 amount) internal {
        require(account != address(0), "ERC20: mint to the zero address");

        _totalSupply += amount;
        _balances[account] += amount;
        emit Transfer(address(0), account, amount);
    }

    function _burn(address account, uint256 amount) internal {
        require(account != address(0), "ERC20: burn from the zero address");
        require(_balances[account] >= amount, "ERC20: burn amount exceeds balance");

        _balances[account] -= amount;
        _totalSupply -= amount;
        emit Transfer(account, address(0), amount);
    }

    function _approve(address owner_, address spender, uint256 amount) internal {
        require(owner_ != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner_][spender] = amount;
        emit Approval(owner_, spender, amount);
    }

    // ========================
    // Access Control Functions
    // ========================
    function hasRole(bytes32 role, address account) public view returns (bool) {
        return _roles[role][account];
    }

    function grantRole(bytes32 role, address account) public onlyRole(ADMIN_ROLE) {
        _grantRole(role, account);
    }

    function revokeRole(bytes32 role, address account) public onlyRole(ADMIN_ROLE) {
        _revokeRole(role, account);
    }

    function renounceRole(bytes32 role) public {
        require(_roles[role][msg.sender], "AccessControl: sender does not have the role");
        _revokeRole(role, msg.sender);
    }

    function _grantRole(bytes32 role, address account) internal {
        if (!_roles[role][account]) {
            _roles[role][account] = true;
            emit RoleGranted(role, account, msg.sender);
        }
    }

    function _revokeRole(bytes32 role, address account) internal {
        if (_roles[role][account]) {
            _roles[role][account] = false;
            emit RoleRevoked(role, account, msg.sender);
        }
    }

    // ========================
    // Pausable Functions
    // ========================
    function pause() public onlyRole(PAUSER_ROLE) whenNotPaused {
        _paused = true;
        emit Paused(msg.sender);
    }

    function unpause() public onlyRole(PAUSER_ROLE) whenPaused {
        _paused = false;
        emit Unpaused(msg.sender);
    }

    // ========================
    // Mint & Burn Functions
    // ========================
    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) whenNotPaused {
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) public onlyRole(BURNER_ROLE) whenNotPaused {
        _burn(from, amount);
    }

    // ========================
    // Snapshot Functions
    // ========================
    function snapshot() public onlyRole(SNAPSHOT_ROLE) returns (uint256) {
        _currentSnapshotId += 1;
        emit Snapshot(_currentSnapshotId);
        return _currentSnapshotId;
    }

    function balanceOfAt(address account, uint256 snapshotId) public view returns (uint256) {
        return _snapshots[snapshotId][account];
    }

    // Override transfer functions to take snapshots
    function _beforeTokenTransfer(address from, address to, uint256 amount) internal {
        // Implement snapshot logic here if needed
    }

    // ========================
    // Governance Functions
    // ========================
    function propose(string memory description) public onlyRole(GOVERNOR_ROLE) returns (uint256) {
        _proposalCount += 1;
        Proposal storage newProposal = _proposals[_proposalCount];
        newProposal.id = _proposalCount;
        newProposal.proposer = msg.sender;
        newProposal.description = description;
        newProposal.snapshotId = snapshot();
        newProposal.deadline = block.timestamp + 3 days;
        emit ProposalCreated(newProposal.id, msg.sender, description, newProposal.snapshotId, newProposal.deadline);
        return newProposal.id;
    }

    function vote(uint256 proposalId, bool support) public {
        Proposal storage proposal = _proposals[proposalId];
        require(block.timestamp < proposal.deadline, "Governance: voting period has ended");
        require(!proposal.voters[msg.sender], "Governance: already voted");

        uint256 weight = balanceOf(msg.sender);
        require(weight > 0, "Governance: no voting power");

        if (support) {
            proposal.forVotes += weight;
        } else {
            proposal.againstVotes += weight;
        }

        proposal.voters[msg.sender] = true;
        emit Voted(proposalId, msg.sender, support, weight);
    }

    function execute(uint256 proposalId) public {
        Proposal storage proposal = _proposals[proposalId];
        require(block.timestamp >= proposal.deadline, "Governance: voting period not yet ended");
        require(!proposal.executed, "Governance: proposal already executed");

        if (proposal.forVotes > proposal.againstVotes) {
            // Implement proposal execution logic here
            // For example, changing a parameter or executing a function
            // This is a placeholder as the actual implementation depends on governance use-case
        }

        proposal.executed = true;
        emit ProposalExecuted(proposal.id, proposal.forVotes > proposal.againstVotes);
    }

    // ========================
    // Utility Functions
    // ========================
    function getCurrentSnapshotId() public view returns (uint256) {
        return _currentSnapshotId;
    }

    function getProposal(uint256 proposalId) public view returns (
        uint256 id,
        address proposer,
        string memory description,
        uint256 snapshotId,
        uint256 deadline,
        uint256 forVotes,
        uint256 againstVotes,
        bool executed
    ) {
        Proposal storage proposal = _proposals[proposalId];
        return (
            proposal.id,
            proposal.proposer,
            proposal.description,
            proposal.snapshotId,
            proposal.deadline,
            proposal.forVotes,
            proposal.againstVotes,
            proposal.executed
        );
    }
}
