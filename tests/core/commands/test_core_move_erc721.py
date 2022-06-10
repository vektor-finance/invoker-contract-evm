import brownie


def test_cannot_duplicate_nft(alice, mock_erc721):
    mock_erc721.mint(alice, 0, {"from": alice})
    with brownie.reverts("ERC721: token already minted"):
        mock_erc721.mint(alice, 0, {"from": alice})


def test_move_erc721_in(alice, mock_erc721, invoker, cmove):
    mock_erc721.mint(alice, 0, {"from": alice})

    calldata_move_in = cmove.moveERC721In.encode_input(mock_erc721, 0)
    mock_erc721.approve(invoker, 0, {"from": alice})

    invoker.invoke([cmove], [calldata_move_in], {"from": alice})

    assert mock_erc721.ownerOf(0) == invoker


def test_erc721_move_requires_approval(alice, mock_erc721, invoker, cmove):
    mock_erc721.mint(alice, 0, {"from": alice})

    calldata_move_in = cmove.moveERC721In.encode_input(mock_erc721, 0)

    with brownie.reverts("ERC721: transfer caller is not owner nor approved"):
        invoker.invoke([cmove], [calldata_move_in], {"from": alice})


def test_erc721_move_requires_balance(alice, bob, mock_erc721, invoker, cmove):
    mock_erc721.mint(bob, 0, {"from": alice})
    calldata_move_in = cmove.moveERC721In.encode_input(mock_erc721, 0)

    with brownie.reverts("ERC721: transfer caller is not owner nor approved"):
        invoker.invoke([cmove], [calldata_move_in], {"from": alice})


def test_erc721_move_requires_token_existence(alice, mock_erc721, invoker, cmove):
    calldata_move_in = cmove.moveERC721In.encode_input(mock_erc721, 0)

    with brownie.reverts("ERC721: operator query for nonexistent token"):
        invoker.invoke([cmove], [calldata_move_in], {"from": alice})


def test_move_erc721_out(alice, mock_erc721, invoker, cmove):
    mock_erc721.mint(invoker, 0, {"from": alice})

    calldata_move_out = cmove.moveERC721Out.encode_input(mock_erc721, 0, alice)

    invoker.invoke([cmove], [calldata_move_out], {"from": alice})

    assert mock_erc721.ownerOf(0) == alice
