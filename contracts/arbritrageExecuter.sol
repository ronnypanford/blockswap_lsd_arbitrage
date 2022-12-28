pragma solidity 0.8.17;

// Import the ISavETHManager and DETH contract interfaces
import "./ISavETHManager.sol";
import "./DETH.sol";
import "./ReentrancyGuard.sol";
import "./Ownable.sol";

// SPDX-License-Identifier: BUSL-1.1

contract ArbitrageExecutor is ReentrancyGuard, Ownable {
    // Address of the savETH manager contract
    ISavETHManager public savETHManager;

    // Address of the DETH contract
    DETH public deth;

    // Constructor function
    constructor(address _savETHManagerAddress, address _dETHAddress) {
        // Set the addresses of the savETH manager and DETH contracts
        savETHManager = ISavETHManager(_savETHManagerAddress);
        deth = DETH(_dETHAddress);
    }

    // Public function to execute arbitrage for a given validator
    function executeArbitrage(
        bytes[] calldata _blsPublicKeysOpenIndex,
        bytes[] calldata _blsPublicKeysUserIndex,
        address[] calldata _openIndexStakeHouses,
        address[] calldata _userIndexStakeHouses,
        uint256 _userIndexId,
        uint256 _dETHRequiredForIsolation,
        address _userAddress
    ) external nonReentrant {
        require(msg.sender == _userAddress,
            "Only the user can execute arbitrage"
        );

        // Check that the dETH required for isolation is greater than 0
        require(
            _dETHRequiredForIsolation > 0,
            "dETH required for isolation must be greater than 0"
        );
        
        // Check that the user has sufficient dETH to cover the amount required for isolation
        require(
            deth.balanceOf(msg.sender) >= _dETHRequiredForIsolation,
            "Insufficient dETH balance"
        );

        require(
            _blsPublicKeysOpenIndex.length == _openIndexStakeHouses.length,
            "Open index public keys and stake houses must be the same length"
        );

        require(
            _blsPublicKeysUserIndex.length == _userIndexStakeHouses.length,
            "User index public keys and stake houses must be the same length"
        );

        require(
            _blsPublicKeysOpenIndex.length == _blsPublicKeysUserIndex.length,
            "Open index public keys and user index public keys must be the same length"
        );


        for (uint i = 0; i < _blsPublicKeysOpenIndex.length; i++) {
            // Isolate the validator's KNOT from the open index
            savETHManager.isolateKnotFromOpenIndex(_openIndexStakeHouses[i], _blsPublicKeysOpenIndex[i], _userIndexId);

            // Add the user's KNOT to the open index to complete the arbitrage
            savETHManager.addKnotToOpenIndex(_userIndexStakeHouses[i], _blsPublicKeysUserIndex[i], _userAddress);
        }

    }


    // Function to allow the owner to change the savETH manager contract address
    function changeSavETHManagerAddress(
        address _newSavETHManagerAddress
    ) external onlyOwner {
        // Set the new savETH manager contract address
        savETHManager = ISavETHManager(_newSavETHManagerAddress);
    }

    // Function to allow the owner to change the DETH contract address
    function changeDETHAddress(address _newDETHAddress) external onlyOwner {
        // Set the new DETH contract address
        deth = DETH(_newDETHAddress);
    }
}
