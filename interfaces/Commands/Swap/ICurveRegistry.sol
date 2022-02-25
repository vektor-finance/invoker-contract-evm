// https://etherscan.io/address/0x7d86446ddb609ed0f5f8684acf30380a356b2b4c#code

pragma solidity ^0.8.0;

interface ICurveRegistry {
    function get_coin_indices(
        address _pool,
        address _from,
        address _to
    )
        external
        view
        returns (
            int128,
            int128,
            bool
        );
}
