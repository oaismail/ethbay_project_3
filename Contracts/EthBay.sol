pragma solidity ^0.5.0;


import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/math/SafeMath.sol";

contract EthBay {

    using SafeMath for uint;
    address public owner;
    uint public balance;
    uint public commission = 5;

    // Seller
    uint public totalSellers = 0;
    uint public nextSellerId = 1; // First Seller created will have id = 1
    struct Seller {
        uint seller_id;
        bool enabled;
        uint balance;
        uint[] stores;
    }

    mapping (address => Seller) public sellers; //map seller to seller address

    //Stores
    uint public nextStoreId = 1; // First Store created will have id = 1
    struct Store {
        uint store_id;
        string name;
        string description;
        address seller;
        bool storeOnline;
        uint[] products;
    }

    
    mapping (uint => Store) public stores; //map store to storeId

    // Products
    uint public nextProductId = 1; // First product created will have id = 1
    struct Product {
        uint storeId;
        uint product_id;
        address seller;
        string name;
        string description;
        uint inventory;
        uint256 price;
        string image;
    }
    mapping (uint => Product) public products; //map product to productId


    //modifier to restrict operations specific to owner
    modifier isOwner() {
        require(msg.sender == owner, "Only owner can execute this");
        _;
    }

    //Constructor 
    constructor() public {
        owner = msg.sender; // Set deployer to owner
    }

    // Start of Owner Related Functions
    event OwnerWithdrewFunds(address admin, uint amount, uint balance);
    function withdrawEthBayFunds() public isOwner {
        uint amount = balance;
        msg.sender.transfer(balance);
        balance = 0;
        emit OwnerWithdrewFunds(msg.sender, amount, balance);
    }

    event SellerAdded(address seller);
    function addSeller(address seller) public isOwner  {
        Seller storage newSeller = sellers[seller];
        newSeller.seller_id = nextSellerId;
        newSeller.balance = 0;
        newSeller.enabled = true;
        totalSellers = totalSellers + 1;
        nextSellerId = nextSellerId + 1;
        emit SellerAdded(seller);
    }

    event OwnerChangedCommission(uint newCommission, uint oldCommission);
    function changeCommission(uint newCommission ) public isOwner {
        uint oldCommission = commission;
        commission = newCommission;
        emit OwnerChangedCommission( newCommission, oldCommission);
    }

    function isSeller(address seller) public view returns (bool) {
        Seller memory seller_ = sellers[seller];
        return seller_.enabled;
    }

    //Start of Seller Related Functions
    event SellerWithdraw(address seller);
    function sellerWithdraw() public {
        require(isSeller(msg.sender) == true, "Only store owner can call function");
        Seller storage seller_ = sellers[msg.sender];
        msg.sender.transfer(seller_.balance);
        seller_.balance = 0;
        emit SellerWithdraw(msg.sender);
    }


    event NewStoreAdded(uint id);
    function addStore(string memory name, string memory description) public  {
        require(isSeller(msg.sender), "Only a store owner can create store fronts");
        Store storage store_ = stores[nextStoreId - 1];
        store_.store_id = nextStoreId;
        store_.name = name;
        store_.description = description;
        store_.seller = msg.sender;
        Seller storage seller_ = sellers[msg.sender];
        seller_.stores.push(nextStoreId);
        nextStoreId ++;
        emit NewStoreAdded(nextStoreId);
    }


    function getStoreForSeller(address seller) public view  returns (uint[] memory) {
        require(isSeller(seller), "Only a store owner can access storefronts");
        Seller storage seller_ = sellers[seller];
        return seller_.stores;
    }

    function getProductsForStore(uint storeId) public view returns (uint[] memory) {
        Store storage store_ = stores[storeId - 1];
        return store_.products;
    }


    event ProductAdded(uint id);
    function addProduct(
        uint storeId, string memory name, string memory description, uint inventory, uint256 price, string memory image
        ) public  {
        Product storage product_ = products[nextProductId - 1];
        Store storage store_ = stores[storeId-1];
        require(store_.seller == msg.sender, "Only the Seller can add products");
        product_.storeId = storeId;
        product_.product_id = nextProductId;
        product_.seller = msg.sender;
        product_.name = name;
        product_.description = description;
        product_.inventory = inventory;
        product_.price = price;
        product_.image = image;       
        store_.products.push(nextProductId);
        emit ProductAdded(nextProductId);
        nextProductId ++;
    }


    event ProductEdited(uint id);
    function editProduct(uint productId, uint inventory, uint256 price) public  {
        Product storage product_ = products[productId - 1];
        require(product_.seller == msg.sender, "Only the Seller can edit products");
        product_.inventory = inventory;
        product_.price = price;
        emit ProductEdited(productId);
    }

    // Start of Buyer Related Functions

    event ProductBought(uint id, address seller, uint owner_profit);
    function buyProduct(uint productId, uint quantity) public  payable {
        Product storage product_ = products[productId - 1];
        Seller storage seller_ = sellers[product_.seller];
        uint commissionValue = (msg.value.mul(commission)).div(100); //Calculate Contract Commission
        balance += commissionValue; // transfer commission to the contract
        seller_.balance = seller_.balance + (msg.value - commissionValue); // transfer rest of the sale to the seller
        product_.inventory = product_.inventory.sub(quantity);
        emit ProductBought(productId, product_.seller, msg.value - commissionValue);
    }
       

}