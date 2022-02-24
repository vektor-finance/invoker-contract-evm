// https://github.com/curvefi/curve-contract/blob/master/contracts/pool-templates/base/SwapTemplateBase.vy

pragma solidity ^0.8.0;

interface ISwapTemplateCurve {
    function A() external view returns (uint256);

    function A_precise() external view returns (uint256);

    function get_virtual_price() external view returns (uint256);

    function calc_token_amount(uint256[2] calldata _amounts, bool _isDeposit)
        external
        view
        returns (uint256);

    function calc_token_amount(uint256[3] calldata _amounts, bool _isDeposit)
        external
        view
        returns (uint256);

    function calc_token_amount(uint256[4] calldata _amounts, bool _isDeposit)
        external
        view
        returns (uint256);

    function calc_token_amount(uint256[5] calldata _amounts, bool _isDeposit)
        external
        view
        returns (uint256);

    function calc_token_amount(uint256[6] calldata _amounts, bool _isDeposit)
        external
        view
        returns (uint256);

    function add_liquidity(uint256[2] calldata _amounts, uint256 _minMintAmount)
        external
        returns (uint256);

    function add_liquidity(uint256[3] calldata _amounts, uint256 _minMintAmount)
        external
        returns (uint256);

    function add_liquidity(uint256[4] calldata _amounts, uint256 _minMintAmount)
        external
        returns (uint256);

    function add_liquidity(uint256[5] calldata _amounts, uint256 _minMintAmount)
        external
        returns (uint256);

    function add_liquidity(uint256[6] calldata _amounts, uint256 _minMintAmount)
        external
        returns (uint256);

    function get_dy(
        int128 _i,
        int128 _j,
        uint256 _dx
    ) external view returns (uint256);

    function exchange(
        int128 _i,
        int128 _j,
        uint256 _dx,
        uint256 _minDy
    ) external;

    function remove_liquidity(uint256 _amount, uint256[2] calldata _minAmounts)
        external
        returns (uint256[2] memory);

    function remove_liquidity(uint256 _amount, uint256[3] calldata _minAmounts)
        external
        returns (uint256[3] memory);

    function remove_liquidity(uint256 _amount, uint256[4] calldata _minAmounts)
        external
        returns (uint256[4] memory);

    function remove_liquidity(uint256 _amount, uint256[5] calldata _minAmounts)
        external
        returns (uint256[5] memory);

    function remove_liquidity(uint256 _amount, uint256[6] calldata _minAmounts)
        external
        returns (uint256[6] memory);

    function remove_liquidity_imbalance(uint256[2] calldata _amounts, uint256 _maxBurnAmount)
        external
        returns (uint256);

    function remove_liquidity_imbalance(uint256[3] calldata _amounts, uint256 _maxBurnAmount)
        external
        returns (uint256);

    function remove_liquidity_imbalance(uint256[4] calldata _amounts, uint256 _maxBurnAmount)
        external
        returns (uint256);

    function remove_liquidity_imbalance(uint256[5] calldata _amounts, uint256 _maxBurnAmount)
        external
        returns (uint256);

    function remove_liquidity_imbalance(uint256[6] calldata _amounts, uint256 _maxBurnAmount)
        external
        returns (uint256);

    function calc_withdraw_one_coin(uint256 _tokenAmount, int128 _i)
        external
        view
        returns (uint256);

    function remove_liquidity_one_coin(
        uint256 _tokenAmount,
        int128 _i,
        uint256 _minAmount
    ) external returns (uint256);
}
