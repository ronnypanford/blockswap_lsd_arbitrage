import os
from dotenv import load_dotenv
import asyncio
import aiohttp
import json
import asyncio
from aiographql.client import GraphQLClient, GraphQLRequest
from web3 import Web3, HTTPProvider
from constants import (LSD_SUBGRAPH_URL, SH_SUBGRAPH_URL, SAV_ETH_MANAGER_COMPILED_JSON,
                       ARBITRAGE_EXECUTOR_COMPILED_JSON, ARBITRAGE_EXECUTOR_CONTRACT_ADDRESS,
                       DETH_CONTRACT_ADDRESS, GAS_LIMIT,
                       SAV_ETH_MANAGER_CONTRACT_ADDRESS,
                       DETH_COMPILED_JSON)


class LsdValidators:
    """
    This class is used to get the lsdvalidators from the LSD subgraph
    """

    def __init__(self, subgraph_url):
        """
        The above function is a constructor that takes in a subgraph url and creates a GraphQLClient
        object

        :param subgraph_url: The URL of the subgraph you want to query
        """
        self.client = GraphQLClient(subgraph_url)

    async def get_lsd_validators(self, currentIndex, status=None):
        """
        It queries the GraphQL API for all the LSD validators that have a status of "MINTED_DERIVATIVES"
        and a currentIndex of the currentIndex variable

        :param currentIndex: The current index of the validator
        :return: A generator object
        """
        if status is None:
            query = '''
                    query($currentIndex: BigInt!) {
                        lsdvalidators(where: {
                            currentIndex: $currentIndex
                        }) {
                            id
                        }
                    }
                '''
        else:
            query = '''
                    query($currentIndex: BigInt!, $status: String!) {
                        lsdvalidators(where: {
                            status: $status
                            currentIndex: $currentIndex
                        }) {
                            id
                        }
                    }
                '''

        query = GraphQLRequest(
            query=query,
            variables={'currentIndex': currentIndex, 'status': status}
        )

        try:
            result = await self.client.query(query)
            result = result.json["data"]["lsdvalidators"]

            lsdValidators_generator = (
                lsdValidator["id"] for lsdValidator in result)
        except Exception as e:
            raise e

        return lsdValidators_generator


class Stakehouses:
    """
    This class is used to get the StakehouseAccounts from the Stakehouse subgraph
    """

    def __init__(self, subgraph_url):
        """
        The above function is a constructor that takes in a subgraph url and creates a GraphQLClient
        object

        :param subgraph_url: The URL of the subgraph you want to query
        """
        self.client = GraphQLClient(subgraph_url)

    async def get_stakehouse_accounts(self, validator_ids):
        """
        It queries the GraphQL API for all the StakehouseAccounts that have a stakeHouse of the validator_ids

        :param validator_ids: The validator ids
        :return: A generator object
        """
        query = GraphQLRequest(
            query='''
                query($ids: [ID!]) {
                    stakehouseAccounts(where: {
                        id_in: $ids
                    }) {
                        stakeHouse
                    }
                }
            ''',
            variables={'ids': validator_ids}
        )

        try:
            result = await self.client.query(query)
            result = result.json["data"]["stakehouseAccounts"]

            StakehouseAccounts_generator = (
                stakehouseAccount["stakeHouse"] for stakehouseAccount in result)

        except Exception as e:
            raise e

        return StakehouseAccounts_generator

    async def get_user_lsd_validators(self, user_address):
        """
        It queries the GraphQL API for all the LSD validators that have a status of "MINTED_DERIVATIVES"
        and a currentIndex of the currentIndex variable

        :param currentIndex: The current index of the validator
        :return: A generator object
        """
        query = '''
                query($owner: String!) {
                    collateralizedKnotOwners(where:{
                        owner: $owner
                    }){
                        validatorID: blsPubKey
                        owner
                        stakehouseAddress
                    }
                }
            '''

        query = GraphQLRequest(
            query=query,
            variables={'owner': user_address}
        )

        try:
            result = await self.client.query(query)
            result = result.json["data"]["collateralizedKnotOwners"]

            user_lsdValidators_generator = (
                lsdValidator["validatorID"] for lsdValidator in result)
        except Exception as e:
            raise e

        return user_lsdValidators_generator

    async def get_knot_details(self, validator_ids, order_by=None, order_direction='asc'):

        if order_by is None:
            query = """
                    query($ids: [ID!]) {
                        knots(where:{
                            id_in: $ids
                        }){
                            id
                            active
                            isolatedDETH
                            rageQuit
                            kicked
                            coordinates
                            knotIndex
                            houseIndex
                            stakeHouse
                            depositor
                            isPartOfIndex
                            reportedYield
                        }
                        }
                    """
        else:
            query = """
                    query($ids: [ID!], $order_by: KNOT_orderBy, $order_direction: OrderDirection) {
                        knots(where:{
                            id_in: $ids
                        }
                        orderBy: $order_by
                        orderDirection: $order_direction){
                            id
                            active
                            isolatedDETH
                            rageQuit
                            kicked
                            coordinates
                            knotIndex
                            houseIndex
                            stakeHouse
                            depositor
                            isPartOfIndex
                            reportedYield
                        }
                        }
                    """
        query = GraphQLRequest(
            query=query,
            variables={'ids': validator_ids, 'order_by': order_by,
                       'order_direction': order_direction}
        )

        try:
            result = await self.client.query(query)
            result = result.json["data"]["knots"]

        except Exception as e:
            raise e

        return result


class ISavETHManager:

    def __init__(self, web3_provider='http://127.0.0.1:9545'):
        self.web3 = Web3(HTTPProvider(web3_provider))
        self.web3.eth.defaultAccount = self.web3.eth.account.privateKeyToAccount(
            os.environ.get('PRIVATE_KEY')).address

        with open(SAV_ETH_MANAGER_COMPILED_JSON) as file:
            self.isavethmanager_contract_json = json.load(
                file)  # load contract info as JSON
            # fetch contract's abi
            self.abi = self.isavethmanager_contract_json['abi']

        self.isavethmanager_contract = self.web3.eth.contract(
            abi=self.abi, address=Web3.toChecksumAddress(SAV_ETH_MANAGER_CONTRACT_ADDRESS))

        with open(DETH_COMPILED_JSON) as file:
            self.deth_contract_json = json.load(
                file)  # load contract info as JSON
            # fetch contract's abi
            self.deth_abi = self.deth_contract_json['abi']

        self.deth_contract = self.web3.eth.contract(
            abi=self.deth_abi, address=Web3.toChecksumAddress(DETH_CONTRACT_ADDRESS))

    def calc_deth_required(self, validator_id):
        rewards_minted = self.isavethmanager_contract.functions.dETHRewardsMintedForKnot(
            validator_id).call()
        deth_required = 24 + self.web3.fromWei(rewards_minted, 'ether')
        return deth_required

    def approve_deth(self, user_address, deth_amount):
        estimate = self.deth_contract.functions.approve(
            self.web3.toChecksumAddress(user_address),
            self.web3.toWei(deth_amount, 'ether')).estimateGas(
            {'from': self.web3.eth.defaultAccount,
             'nonce': self.web3.eth.getTransactionCount(self.web3.eth.defaultAccount),
             'gas': 1000000,
             'gasPrice': self.web3.toWei('1', 'gwei')}
        )

        deth_contract = self.deth_contract.functions.approve(
            self.web3.toChecksumAddress(user_address),
            self.web3.toWei(deth_amount, 'ether')).buildTransaction(
            {'from': self.web3.eth.defaultAccount,
                'nonce': self.web3.eth.getTransactionCount(self.web3.eth.defaultAccount),
                'gas': estimate,
                'gasPrice': self.web3.eth.gasPrice}
        )
        tx_receipt = self.web3.eth.sendRawTransaction(
            self.web3.eth.account.sign_transaction(
                deth_contract, private_key=os.environ.get('PRIVATE_KEY')).rawTransaction)

        return tx_receipt.hex()
    
    def get_user_index(self, user_validator_id):
        return self.isavethmanager_contract.functions.associatedIndexIdForKnot(
            user_validator_id
        ).call()


class Arbitrage:

    def __init__(self, web3_provider='http://127.0.0.1:9545'):
        self.web3 = Web3(HTTPProvider(web3_provider))
        self.web3.eth.defaultAccount = self.web3.eth.account.privateKeyToAccount(
            os.environ.get('PRIVATE_KEY')).address

        with open(ARBITRAGE_EXECUTOR_COMPILED_JSON) as file:
            self.arbitrage_contract_json = json.load(
                file)  # load contract info as JSON
            # fetch contract's abi
            self.arbitrage_contract_abi = self.arbitrage_contract_json['abi']

        self.arbitrage_contract = self.web3.eth.contract(
            abi=self.arbitrage_contract_abi,
            address=ARBITRAGE_EXECUTOR_CONTRACT_ADDRESS
        )

    def execute_arbitrage(self,
                          open_index_validator_ids,
                          user_validator_ids,
                          open_index_validator_stakehouse_ids,
                          user_validator_stakehouse_ids,
                          user_index,
                          deth_required,
                          user_address,
                          gas=GAS_LIMIT):
        message = self.arbitrage_contract.functions.executeArbitrage(
            open_index_validator_ids,
            user_validator_ids,
            open_index_validator_stakehouse_ids,
            user_validator_stakehouse_ids,
            user_index,
            self.web3.toWei(deth_required, 'ether'),
            user_address
        ).buildTransaction(
            {
                'gas': gas,
                'nonce': self.web3.eth.getTransactionCount(self.web3.eth.defaultAccount),
                'gasPrice': self.web3.eth.gasPrice,
            }
        )

        # Sign transaction
        signed_txn = self.web3.eth.account.sign_transaction(
            message, private_key=os.environ.get('PRIVATE_KEY'))

        # Send transaction
        tx_hash = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)

        # Wait for transaction to be mined
        self.web3.eth.waitForTransactionReceipt(tx_hash)

        return tx_hash

    def get_arbitrage_gas_estimate(self,
                                   open_index_validator_ids,
                                   user_validator_ids,
                                   open_index_validator_stakehouse_ids,
                                   user_validator_stakehouse_ids,
                                   user_index,
                                   deth_required,
                                   user_address,
                                   gas=GAS_LIMIT):
        transaction = self.arbitrage_contract.functions.executeArbitrage(
            open_index_validator_ids,
            user_validator_ids,
            open_index_validator_stakehouse_ids,
            user_validator_stakehouse_ids,
            user_index,
            self.web3.toWei(deth_required, 'ether'),
            user_address
        ).buildTransaction({
            'gas': gas,
            'nonce': self.web3.eth.getTransactionCount(self.web3.eth.defaultAccount),
            'gasPrice': self.web3.eth.gasPrice
        })

        estimate = self.web3.eth.estimateGas(transaction)

        return estimate


async def main():

    load_dotenv()

    consider_execution_cost = False
    web3_url = os.environ.get('INFURA_URL', 'http://127.0.0.1:9545')
    open_index_id = 0
    user_index_id = 1
    user_address = '0xc3419f3ac973574f1e0c47cc9e6f4804acf8c740'

    lsd_validators_instance = LsdValidators(LSD_SUBGRAPH_URL)
    i_save_eth_manager_instance = ISavETHManager(web3_url)
    stakehouses_instance = Stakehouses(SH_SUBGRAPH_URL)
    arbitrage_instance = Arbitrage(web3_url)

    openindex_validators = [lsd_validator for lsd_validator in await lsd_validators_instance.get_lsd_validators(open_index_id)]
    user_lsd_validators = [lsd_validator for lsd_validator in await stakehouses_instance.get_user_lsd_validators(user_address=user_address)]

    openindex_validators_details = await stakehouses_instance.get_knot_details(openindex_validators, order_by="reportedYield", order_direction="desc")
    user_lsd_validators_details = await stakehouses_instance.get_knot_details(user_lsd_validators, order_by="reportedYield", )

    l = min((len(openindex_validators_details),
             len(user_lsd_validators_details)))
    
    if user_lsd_validators_details:
        user_index_id = i_save_eth_manager_instance.get_user_index(user_lsd_validators_details[0]['id'])
    else:
        print("No user lsd validators")
        return


    openIndex_validators_ids = []
    openIndex_validators_stakehouse_ids = []
    user_lsd_validators_ids = []
    user_lsd_validators_stakehouse_ids = []

    deth_required_to_isolate = 0
    deth_gained_for_returning = 0

    for i in range(l):
        open_index_deth_needed = i_save_eth_manager_instance.calc_deth_required(
            openindex_validators_details[i]['id'])
        openindex_validators_details[i]['deth_needed'] = open_index_deth_needed

        user_deth_needed = i_save_eth_manager_instance.calc_deth_required(
            user_lsd_validators_details[i]['id'])
        user_lsd_validators_details[i]['deth_needed'] = user_deth_needed

        if open_index_deth_needed < user_deth_needed and openindex_validators_details[i]['reportedYield'] > user_lsd_validators_details[i]['reportedYield']:

            openIndex_validators_ids.append(
                openindex_validators_details[i]['id'])
            openIndex_validators_stakehouse_ids.append(
                Web3.toChecksumAddress(openindex_validators_details[i]['stakeHouse']))
            user_lsd_validators_ids.append(
                user_lsd_validators_details[i]['id'])
            user_lsd_validators_stakehouse_ids.append(
                Web3.toChecksumAddress(user_lsd_validators_details[i]['stakeHouse']))

            deth_required_to_isolate += open_index_deth_needed
            deth_gained_for_returning += user_deth_needed

            print("\nArbitrage opportunity found:")
            print("=====================================")
            print(f"\nOpenIndex Validator: {openindex_validators_details[i]}")
            print(f"\nUser LSD Validator: {user_lsd_validators_details[i]}\n")

    if consider_execution_cost:
        # Check cost of arbitrage
        executing_cost = arbitrage_instance.get_arbitrage_gas_estimate(
            openIndex_validators_ids,
            user_lsd_validators_ids,
            openIndex_validators_stakehouse_ids,
            user_lsd_validators_stakehouse_ids,
            user_index=user_index_id,
            deth_required=Web3.toWei(deth_required_to_isolate, 'ether'),
            user_address=Web3.toChecksumAddress(user_address)
        )

        print(f"\nExecuting cost: {executing_cost}")

        if (deth_required_to_isolate + executing_cost) > deth_gained_for_returning:
            print("\nArbitrage is not profitable")
            return

    # Approve deth
    response = i_save_eth_manager_instance.approve_deth(
        user_address=Web3.toChecksumAddress(user_address),
        deth_amount=Web3.toWei(deth_required_to_isolate, 'ether')
    )

    # If approve deth failed
    if not response:
        print("\nApprove deth failed.")
        return

    print(f"\nApprove deth success, transaction hash: {str(response)}")

    response = arbitrage_instance.execute_arbitrage(
        openIndex_validators_ids,
        user_lsd_validators_ids,
        openIndex_validators_stakehouse_ids,
        user_lsd_validators_stakehouse_ids,
        user_index=user_index_id,
        deth_required=Web3.toWei(deth_required_to_isolate, 'ether'),
        user_address=Web3.toChecksumAddress(user_address),
        gas=(executing_cost if consider_execution_cost else GAS_LIMIT),
    )

    print(f"\nArbitrage executed: {response}\n")

    print(f"\nDeth required to isolate: {deth_required_to_isolate}")
    print(f"\nDeth gained for returning: {deth_gained_for_returning}")

    if consider_execution_cost:
        print(
            f"\nDeth profit: {deth_gained_for_returning - deth_required_to_isolate - executing_cost}")
    else:
        print(
            f"\nDeth profit: {deth_gained_for_returning - deth_required_to_isolate}")

    print("\nPairs executed:")
    for i in range(len(openIndex_validators_ids)):
        print(f"\nOpenIndex Validator: {openIndex_validators_ids[i]}")
        print(
            f"\nOpenIndex cost to isolate: {openindex_validators_details[i]['deth_needed']}")

        print(f"\nUser LSD Validator: {user_lsd_validators_ids[i]}\n")
        print(f"\n")


if __name__ == "__main__":

    response = asyncio.run(main=main())
