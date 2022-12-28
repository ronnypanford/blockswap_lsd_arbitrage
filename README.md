Stakehouse Protocol Arbitrage
=============================

This project aims to write scripts that fetch information about LSD arbitrage opportunities on the Goerli testnet and a smart contract that executes the arbitrage. Executing arbitrage in this context means taking validators that are associated with the open index (the default index for earning yield) and transferring them to the user's own index, where the yield is boosted by managing the dETH and validators.

To find arbitrage opportunities, the script compares the yields of validators in the open index to the yields of validators in the user's index, and only considers validators that have a higher yield in the open index and require less dETH to isolate (transfer to the user's index) than their counterparts in the user's index. The script then calculates the total dETH required to isolate all identified validators and the total dETH gained by returning all of the user's validators to the open index. If the total dETH gained is greater than the total dETH required, an arbitrage opportunity is deemed to exist and the validators are eligible for transfer.

To fetch information about the validators and their yields, the script queries the LSD and Stakehouse subgraphs using GraphQL. It also interacts with the `ISavETHManager` and `ArbitrageExecutor` contracts to execute the arbitrage by isolating the validators and returning the user's validators to the open index.

[SavETHManager Smart Contract](SMART_CONTRACT_README.md)

[Test Arbitrage for user 0xc3419f3ac973574f1e0c47cc9e6f4804acf8c740](test_arbitrage_for_user_0xc3419f3ac973574f1e0c47cc9e6f4804acf8c740.jpg)

Dependencies
------------

The following dependencies are required to run the script:

-   aiohttp
-   aiographql
-   asyncio
-   dotenv
-   json
-   os
-   web3

Environment Variables
---------------------

The following environment variables must be set:

-   `INFURA_URL`: The URL of the Ethereum node to be used for contract interactions.
-   `PRIVATE_key`: The private key used to generate the Ethereum account that will execute the arbitrage.

Constants
---------

The following constants are used in the script:

-   `LSD_SUBGRAPH_URL`: The URL of the LSD subgraph.
-   `SH_SUBGRAPH_URL`: The URL of the Stakehouse subgraph.
-   `SAV_ETH_MANAGER_COMPILED_JSON`: The compiled JSON file for the `ISavETHManager` contract.
-   `ARBITRAGE_EXECUTOR_COMPILED_JSON`: The compiled JSON file for the `ArbitrageExecutor` contract.
-   `ARBITRAGE_EXECUTOR_CONTRACT_ADDRESS`: The contract address of the 
    `ArbitrageExecutor` contract.
    `DETH_CONTRACT_ADDRESS`: The contract address of the dETH contract.
-   `GAS_LIMIT`: The maximum amount of gas that can be used for a contract transaction.
-   `SAV_ETH_MANAGER_CONTRACT_ADDRESS`: The contract address of the `ISavETHManager` contract.
-   `DETH_COMPILED_JSON`: The compiled JSON file for the dETH contract.

Classes
-------

### LsdValidators

This class is used to get the LSD validators from the LSD subgraph.

#### `__init__(self, subgraph_url)`

This is the constructor of the `LsdValidators` class. It takes in a `subgraph_url` and creates a `GraphQLClient` object.

#### `async get_lsd_validators(self, currentIndex, status=None)`

This method queries the GraphQL API for all the LSD validators that have a `status` of "MINTED_DERIVATIVES" and a `currentIndex` of the `currentIndex` variable. If no `status` is provided, it returns all validators with the specified `currentIndex`. It returns a generator object.

##### Parameters

-   `currentIndex`: The `currentIndex` of the validator.
-   `status`: The `status` of the validator.

##### Returns

-   A generator object.

### Stakehouses

This class is used to get the StakehouseAccounts from the Stakehouse subgraph.

#### `__init__(self, subgraph_url)`

This is the constructor of the `Stakehouses` class. It takes in a `subgraph_url` and creates a `GraphQLClient` object.

#### `async get_stakehouse_accounts(self, validator_ids)`

This method queries the GraphQL API for all the StakehouseAccounts that have a `stakeHouse` of the `validator_ids`. It returns a generator object.

##### Parameters

-   `validator_ids`: The `validator_ids`.

##### Returns

-   A generator object.

#### `async get_user_lsd_validators(self, user_address)`

This method queries the GraphQL API for all the LSD validators that have a `stakeHouse` of the `user_address`. It returns a generator object.

##### Parameters

-   `user_address`: The `user_address`.

##### Returns

-   A generator object.

#### `async get_knot_details(self, validators, order_by=None, order_direction=None)`

This method queries the GraphQL API for all the details of the validators. It returns a list of dictionaries containing the details of the validators.

##### Parameters

-   `validators`: The list of validators.
-   `order_by`: The field to order the results by.
-   `order_direction`: The direction to order the results in.

##### Returns

-   A list of dictionaries containing the details of the validators.

### ISavETHManager

This class is used to interact with the `ISavETHManager` contract.

#### `__init__(self, web3_url)`

This is the constructor of the `ISavETHManager` class. It takes in a `web3_url` and creates a `Web3` object. It also sets the contract address and ABI for the `ISavETHManager` contract.

##### Parameters

-   `web3_url`: The `web3_url` to connect to.

#### `calc_deth_required(self, validator_id)`

This method calculates the amount of dETH required for isolation for a validator with the given `validator_id`. It returns an integer representing the amount of dETH required.

##### Parameters

-   `validator_id`: The `validator_id` of the validator.

##### Returns

-   An integer representing the amount of dETH required.

#### `approve_deth(self, validator_id)`

This method approves the amount of dETH required for isolation for a validator for the saveETHManager to spend. It returns the transaction hash.

##### Parameters

-   `deth_amount`: The `deth_amount` required for isolation of the validatos.

##### Returns

-   The transaction hash of the approval.

#### `get_user_index(self, user_validator_id)`

This method gets the index of the user using one of the validator IDs of the user. It returns an integer representing the index of the user.

##### Parameters

-   `user_validator_id`: The `user_validator_id` of the user.

##### Returns

-   An integer representing the index of the user.

.

### Arbitrage


This class is used to interact with the `ArbitrageExecutor` contract.

#### `__init__(self, web3_url)`

This is the constructor of the `Arbitrage` class. It takes in a `web3_url` and creates a `Web3` object. It also sets the contract address and ABI for the `ArbitrageExecutor` contract.

##### Parameters

-   `web3_url`: The `web3_url` to connect to.

#### `async execute_arbitrage(self, open_index_validator_ids, user_validator_ids, open_index_stakehouse_ids, user_stakehouse_ids, deth_required_to_isolate, deth_gained_for_returning)`

This method executes the arbitrage by calling the `executeArbitrage` function on the `ArbitrageExecutor` contract. It takes in the `open_index_validator_ids`, `user_validator_ids`, `open_index_stakehouse_ids`, `user_stakehouse_ids`, `deth_required_to_isolate`, and `deth_gained_for_returning` and sends a transaction to the contract to execute the arbitrage.

##### Parameters

-   `open_index_validator_ids`: The `open_index_validator_ids` of the validators in the open index.
-   `user_validator_ids`: The `user_validator_ids` of the validators in the user's index.

-   `user_stakehouse_ids`: The `user_stakehouse_ids` of the validators in the user's index.
-   `deth_required_to_isolate`: The `deth_required_to_isolate` required to isolate the validators from the open index.
-   `deth_gained_for_returning`: The `deth_gained_for_returning` gained for returning the validators to the open index.

##### Returns

-   The transaction hash of the executed arbitrage.

### main

This is the main function of the script. It loads the environment variables and sets some initial variables such as the `web3_url`, `open_index_id`, `user_index`, and `user_address`. It then creates instances of the `LsdValidators`, `ISavETHManager`, `Stakehouses`, and `Arbitrage` classes.

It then queries the GraphQL API for all the LSD validators in the open index and the user's index. It also gets the metadata for the validators in the open index and the user's index.

The `main` function continues by looping through the validators in the open index and the user's index, and calculating the dETH required for isolation for both. If the dETH required for isolation for the open index validator is less than the dETH required for isolation for the user's validator and the reported yield for the open index validator is greater than the reported yield for the user's validator, it adds them to the list of validators to be arbitraged.

This is done to find the arbitrage opportunities, as the validators with a higher reported yield and a lower dETH required for isolation are more likely to provide a higher return on investment.

Finally, the `main` function calls the `execute_arbitrage` method of the `Arbitrage` class to execute the arbitrage. It passes in the validator IDs and stakehouse IDs of the validators in the open index and the user's index, as well as the `deth_required_to_isolate` and `deth_gained_for_returning` calculated earlier.

The `execute_arbitrage` method returns the transaction hash of the executed arbitrage, which is then printed to the console.

### Conclusion

This script fetches information about LSD arbitrage opportunities on the Goerli testnet and writes a smart contract that executes the arbitrage. It does so by querying the GraphQL API for validators in the open index and the user's index, calculating the dETH required for isolation for each validator, and finding arbitrage opportunities by comparing the dETH required for isolation and the reported yield for each validator. It then executes the arbitrage by calling the appropriate smart contract functions.