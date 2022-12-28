const ArbitrageExecutor = artifacts.require("ArbitrageExecutor");
const deth = "0xA2c4576B405ca21A7f27119F67f2786666B9fEcF"; // DETH contract address
const savETHManager = "0x9ef3bb02cada3e332bbaa27cd750541c5ffb5b03"; // SAVETHMANAGER contract address

module.exports = function(deployer) {
    deployer.deploy(ArbitrageExecutor, savETHManager, deth);
};
