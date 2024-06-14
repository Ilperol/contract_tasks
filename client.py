import cmd
from web3 import Web3
from eth_account import Account
from web3.middleware import construct_sign_and_send_raw_middleware
import time

# Etherscan API Key
etherscan_api_key = 'I2WT2TUKQG45RPD28WNXDHY1RZA7KUEGYD'
etherscan_base_url = 'https://api-sepolia.etherscan.io/api'
sepolia_chain_id = 11155111

# Hardcoded account address and private key
account_address = '0x34dab0B81832C4acF3CaEE5ABaE15878Da279f93'
private_key = '709d6b5985bb15fb7af796ce969bd7f55e18a1554c6b78d6fa1e4915bff83951'

# Hardcoded contract addresses
car_token_address = '0x256C0B67767E989bC5B1B77960B7C71dfE1Fec9b'
dividend_token_address = '0xeF05E0E8eA7404992878A3c612a565795ef9443A'
escrow_address = '0x07d93BcA85B253e13bc1330996CCD816eE043897'
rental_service_address = '0x0440361fBb9168e8aFB59F473e63827C99850573'

# CarToken ABI
car_token_abi = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "ERC721IncorrectOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ERC721InsufficientApproval",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "approver",
				"type": "address"
			}
		],
		"name": "ERC721InvalidApprover",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			}
		],
		"name": "ERC721InvalidOperator",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "ERC721InvalidOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "receiver",
				"type": "address"
			}
		],
		"name": "ERC721InvalidReceiver",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			}
		],
		"name": "ERC721InvalidSender",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ERC721NonexistentToken",
		"type": "error"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "approved",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "Approval",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "ApprovalForAll",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "Transfer",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "admin",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "approve",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "balanceOf",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "carDetails",
		"outputs": [
			{
				"internalType": "string",
				"name": "vin",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "licensePlate",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "bodyType",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "brand",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "model",
				"type": "string"
			},
			{
				"internalType": "bool",
				"name": "availableForRent",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "getApproved",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			}
		],
		"name": "isApprovedForAll",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "isCarAvailableForRent",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "vin",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "licensePlate",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "bodyType",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "brand",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "model",
				"type": "string"
			}
		],
		"name": "listCarForRent",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "vin",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "licensePlate",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "bodyType",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "brand",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "model",
				"type": "string"
			}
		],
		"name": "mint",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "name",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nextTokenId",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ownerOf",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "removeCarFromRental",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "safeTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "bytes",
				"name": "data",
				"type": "bytes"
			}
		],
		"name": "safeTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "setApprovalForAll",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes4",
				"name": "interfaceId",
				"type": "bytes4"
			}
		],
		"name": "supportsInterface",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "symbol",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "tokenURI",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "transferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
# RentalService ABI
rental_service_abi = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_carTokenAddress",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "_dividendTokenAddress",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "_escrowAddress",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "renter",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "startDate",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "endDate",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "dailyRate",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "deposit",
                "type": "uint256"
            }
        ],
        "name": "CarRented",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "renter",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "refundAmount",
                "type": "uint256"
            }
        ],
        "name": "CarReturned",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "carToken",
        "outputs": [
            {
                "internalType": "contract CarToken",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "dividendToken",
        "outputs": [
            {
                "internalType": "contract DividendToken",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "escrow",
        "outputs": [
            {
                "internalType": "contract Escrow",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "pendingWithdrawals",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "rentalDays",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "dailyRate",
                "type": "uint256"
            }
        ],
        "name": "rentCar",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "name": "rentals",
        "outputs": [
            {
                "internalType": "address",
                "name": "renter",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "startDate",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "endDate",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "dailyRate",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "deposit",
                "type": "uint256"
            },
            {
                "internalType": "bool",
                "name": "active",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            }
        ],
        "name": "returnCar",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Escrow ABI
escrow_abi = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "DepositReceived",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "refundAmount",
                "type": "uint256"
            }
        ],
        "name": "DepositRefunded",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "paymentAmount",
                "type": "uint256"
            }
        ],
        "name": "PaymentReleased",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "admin",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            }
        ],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "name": "deposits",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
            {
                "internalType": "address payable",
                "name": "renter",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "refundAmount",
                "type": "uint256"
            }
        ],
        "name": "refundDeposit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
            {
                "internalType": "address payable",
                "name": "owner",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "paymentAmount",
                "type": "uint256"
            }
        ],
        "name": "releasePayment",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# DividendToken ABI
dividend_token_abi = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "allowance",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "needed",
                "type": "uint256"
            }
        ],
        "name": "ERC20InsufficientAllowance",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "sender",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "balance",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "needed",
                "type": "uint256"
            }
        ],
        "name": "ERC20InsufficientBalance",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "approver",
                "type": "address"
            }
        ],
        "name": "ERC20InvalidApprover",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "receiver",
                "type": "address"
            }
        ],
        "name": "ERC20InvalidReceiver",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "sender",
                "type": "address"
            }
        ],
        "name": "ERC20InvalidSender",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            }
        ],
        "name": "ERC20InvalidSpender",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "internalType": "uint8",
                "name": "",
                "type": "uint8"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "lastWithdrawalTime",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "payDividends",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "serviceOwner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "withdrawDividends",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

class EthereumCLI(cmd.Cmd):
    prompt = '> '
    intro = "? for help"

    def __init__(self):
        super().__init__()
        self.account = account_address
        self.private_key = private_key
        self.web3 = Web3(Web3.HTTPProvider('https://rpc.sepolia.org'))
        self.web3.middleware_onion.add(construct_sign_and_send_raw_middleware(self.web3.eth.account.from_key(private_key)))

        # Hardcoded contract instances
        self.car_token_contract = self.web3.eth.contract(address=car_token_address, abi=car_token_abi)
        self.dividend_token_contract = self.web3.eth.contract(address=dividend_token_address, abi=dividend_token_abi)
        self.escrow_contract = self.web3.eth.contract(address=escrow_address, abi=escrow_abi)
        self.rental_service_contract = self.web3.eth.contract(address=rental_service_address, abi=rental_service_abi)

        if self.web3.is_connected():
            print("Connected to Sepolia network.")
        else:
            print("Failed to connect to Sepolia network.")

        admin_address = self.escrow_contract.functions.admin().call()
        print(f"Admin address from contract: {admin_address}")
        print(f"Account address in client: {self.account}")

    def send_transaction(self, function, value=0):
        """Helper function to send transaction via Web3"""
        try:
            tx_hash = function.transact({
                'from': self.account,
                'value': value,
                'gas': 900000,
                'gasPrice': self.web3.to_wei('100', 'gwei')
            })
            print(f"Transaction sent with hash {tx_hash.hex()}")
            self.check_transaction_status(tx_hash)
            return tx_hash
        except Exception as e:
            print(f"An error occurred {e}")
            return None

    def check_transaction_status(self, tx_hash):
        """Check the status of a transaction"""
        try:
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status == 1:
                print("Transaction successful")
            else:
                print("Transaction failed")
        except Exception as e:
            print(f"Error checking transaction status {e}")

    def do_mint_car_token(self, line):
        """Mint a new car token mint_car_token <to> <vin> <licensePlate> <bodyType> <brand> <model>"""
        args = line.split()
        if len(args) != 6:
            print("Usage mint_car_token <to> <vin> <licensePlate> <bodyType> <brand> <model>")
            return

        to, vin, license_plate, body_type, brand, model = args
        function = self.car_token_contract.functions.mint(to, vin, license_plate, body_type, brand, model)
        self.send_transaction(function)

    def do_list_car_for_rent(self, line):
        """List a car for rent list_car_for_rent <tokenId> <vin> <licensePlate> <bodyType> <brand> <model>"""
        args = line.split()
        if len(args) != 6:
            print("Usage list_car_for_rent <tokenId> <vin> <licensePlate> <bodyType> <brand> <model>")
            return

        token_id = int(args[0])
        vin, license_plate, body_type, brand, model = args[1:]
        function = self.car_token_contract.functions.listCarForRent(token_id, vin, license_plate, body_type, brand, model)
        self.send_transaction(function)

    def do_remove_car_from_rental(self, line):
        """Remove a car from rental remove_car_from_rental <tokenId>"""
        args = line.split()
        if len(args) != 1:
            print("Usage remove_car_from_rental <tokenId>")
            return

        token_id = int(args[0])
        function = self.car_token_contract.functions.removeCarFromRental(token_id)
        self.send_transaction(function)

    def do_is_car_available_for_rent(self, line):
        """Check if a car is available for rent is_car_available_for_rent <tokenId>"""
        args = line.split()
        if len(args) != 1:
            print("Usage is_car_available_for_rent <tokenId>")
            return

        token_id = int(args[0])
        available = self.car_token_contract.functions.isCarAvailableForRent(token_id).call()
        print(f"Car availability for rent (Token ID {token_id}): {available}")

    def do_rent_car(self, line):
        """Rent a car rent_car <tokenId> <rentalDays> <dailyRate>"""
        args = line.split()
        if len(args) != 3:
            print("Usage rent_car <tokenId> <rentalDays> <dailyRate>")
            return

        token_id, rental_days, daily_rate = map(int, args)
        deposit_amount = rental_days * daily_rate
        function = self.rental_service_contract.functions.rentCar(token_id, rental_days, daily_rate)
        self.send_transaction(function, value=deposit_amount)

    def do_return_car(self, line):
        """Return a rented car return_car <tokenId>"""
        args = line.split()
        if len(args) != 1:
            print("Usage return_car <tokenId>")
            return

        token_id = int(args[0])
        function = self.rental_service_contract.functions.returnCar(token_id)
        self.send_transaction(function)

    def do_withdraw_dividends(self, line):
        """Withdraw dividends withdraw_dividends <amount>"""
        args = line.split()
        if len(args) != 1:
            print("Usage withdraw_dividends <amount>")
            return

        amount = int(args[0])
        function = self.dividend_token_contract.functions.withdrawDividends(amount)
        self.send_transaction(function)

    def do_pay_dividends(self, line):
        """Pay dividends pay_dividends <owner> <amount>"""
        args = line.split()
        if len(args) != 2:
            print("Usage pay_dividends <owner> <amount>")
            return

        owner = args[0]
        amount = int(args[1])
        function = self.dividend_token_contract.functions.payDividends(owner, amount)
        self.send_transaction(function)

    def do_transfer_car(self, line):
        """Transfer a car transfer_car <from> <to> <tokenId>"""
        args = line.split()
        if len(args) != 3:
            print("Usage transfer_car <from> <to> <tokenId>")
            return

        from_address, to_address, token_id = args
        token_id = int(token_id)
        function = self.car_token_contract.functions.transferFrom(from_address, to_address, token_id)
        self.send_transaction(function)

    def do_deposit(self, line):
        """Deposit to escrow deposit <tokenId> <amount>"""
        args = line.split()
        if len(args) != 2:
            print("Usage deposit <tokenId> <amount>")
            return

        token_id = int(args[0])
        amount = int(args[1])
        function = self.escrow_contract.functions.deposit(token_id)
        self.send_transaction(function, value=amount)

    def do_refund_deposit(self, line):
        """Refund deposit from escrow refund_deposit <tokenId> <renter> <amount>"""
        args = line.split()
        if len(args) != 3:
            print("Usage refund_deposit <tokenId> <renter> <amount>")
            return

        token_id = int(args[0])
        renter = args[1]
        amount = int(args[2])
        function = self.escrow_contract.functions.refundDeposit(token_id, renter, amount)
        self.send_transaction(function)

    def do_release_payment(self, line):
        """Release payment from escrow release_payment <tokenId> <owner> <amount>"""
        args = line.split()
        if len(args) != 3:
            print("Usage release_payment <tokenId> <owner> <amount>")
            return

        token_id = int(args[0])
        owner = args[1]
        amount = int(args[2])
        function = self.escrow_contract.functions.releasePayment(token_id, owner, amount)
        self.send_transaction(function)

    def do_exit(self, line):
        """Exit the CLI"""
        return True

if __name__ == '__main__':
    EthereumCLI().cmdloop()
