// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TicketRegistry {
    mapping(bytes32 => uint256) public storedAt;
    address public owner;

    event TicketStored(bytes32 indexed ticketHash, address indexed sender, uint256 timestamp);

    constructor() {
        owner = msg.sender;
    }

    function storeTicket(bytes32 ticketHash) external {
        if (storedAt[ticketHash] == 0) {
            storedAt[ticketHash] = block.timestamp;
            emit TicketStored(ticketHash, msg.sender, block.timestamp);
        }
    }

    function isStored(bytes32 ticketHash) external view returns (bool, uint256) {
        uint256 t = storedAt[ticketHash];
        return (t != 0, t);
    }
}
