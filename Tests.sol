// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../contracts/ToksStakingV2.sol";
import "../contracts/interfaces/IEpochController.sol";

interface IToksStakingV2 {
    function initializeV2(address epochControllerAddr) external;
    function initializeStakers(address[] calldata stakerAddresses, uint256[] calldata stakerAmounts) external;
    function incrementEpoch() external;
    function recordExternalRewardDistribution(address token, uint256 amount, uint256 timestamp) external;
    function claimExternalRewards(address user, uint256 epoch) external;
    function userPendingExternalRewards(address user, uint256 epoch) external view returns (address[] memory, uint256[] memory);
    function deposit(uint256 amount) external;
    function withdraw(uint256 amount) external;
    function pause() external;
    function unpause() external;
    function version() external view returns (uint256);
    function epochControllerAddr() external view returns (address);
    function balanceOf(address user) external view returns (uint256);
    function userHasClaimedExternalRewards(address user, uint256 epoch) external view returns (bool);
    function epochHasEnded(uint256 epoch) external view returns (bool);
    function paused() external view returns (bool);
}

contract MockEpochController is IEpochController {
    uint256 private epochNumber;

    function setCurrentEpochNumber(uint256 _epochNumber) external {
        epochNumber = _epochNumber;
    }

    function currentEpochNumber() external view override returns (uint256) {
        return epochNumber;
    }

    function getEndTime(uint256 epoch) external view override returns (uint256) {
        return epoch == 0 ? block.timestamp - 1 : 0;
    }

    function getStartTime(uint256 _epochNumber) external view override returns (uint256) {
        return block.timestamp - _epochNumber * 1 weeks;
    }

    function incrementEpoch() external override {
        epochNumber += 1;
    }
}

contract ToksStakingV2Testable is ToksStakingV2 {
    function getEpochNumber(uint256 epoch) external view returns (uint256) {
        return _epochs.length;
    }

    function getEpochStakedTotal(uint256 epoch) external view returns (uint256) {
        return _epochs[epoch].stakedTotalEligible;
    }

    function getEpochExternalRewardTokenTotals(uint256 epoch, address token) external view returns (uint256) {
        return _epochs[epoch].externalRewardTokenTotals[token];
    }

    function getEpochExternalRewardTokenExists(uint256 epoch, address token) external view returns (bool) {
        return _epochs[epoch].externalRewardTokenExists[token];
    }

    function getStakedTotal() external view returns (uint256) {
        return stakedTotal;
    }

    function getStakedTotalIneligible() external view returns (uint256) {
        return stakedTotalIneligible;
    }

    function setEpochController(address controller) external {
        epochControllerAddr = controller;
    }
}

contract ToksStakingV2Test is Test {
    ToksStakingV2Testable public toksStaking;
    MockEpochController epochController;
    address user = address(0x789);
    address token = address(0x456);
    address owner = address(this);
    address[] stakerAddresses;
    uint256[] stakerAmounts;
    bool private initialized;

    function setUp() public {
        vm.prank(owner);
        epochController = new MockEpochController();
        vm.prank(owner);
        toksStaking = new ToksStakingV2Testable();
        vm.prank(owner);
        toksStaking.setEpochController(address(epochController));
        vm.prank(owner);
        toksStaking.initializeV2(address(epochController));
    }

    function testInitializeV2_Success() public {
        assertEq(toksStaking.version(), 2);
        assertEq(toksStaking.epochControllerAddr(), address(epochController));
        assertTrue(toksStaking.paused());
    }

    function testInitializeV2_ZeroAddress() public {
        ToksStakingV2Testable toksStakingNew = new ToksStakingV2Testable();
        vm.prank(owner);
        vm.expectRevert("ToksStaking: cannot use zero address for EpochController");
        toksStakingNew.initializeV2(address(0));
    }

    function testInitializeV2_DoubleInitialization() public {
        vm.prank(owner);
        vm.expectRevert("Initializable: contract is already initialized");
        toksStaking.initializeV2(address(epochController));
    }

    function testInitializeStakers_Success() public {
        stakerAddresses = [address(0x123), address(0x456)];
        stakerAmounts = [100, 200];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        assertEq(toksStaking.balanceOf(stakerAddresses[0]), stakerAmounts[0]);
        assertEq(toksStaking.balanceOf(stakerAddresses[1]), stakerAmounts[1]);
    }

    function testInitializeStakers_OnlyOwner() public {
        stakerAddresses = [address(0x123), address(0x456)];
        stakerAmounts = [100, 200];
        vm.prank(address(0x456));
        vm.expectRevert("Ownable: caller is not the owner");
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
    }

    function testIncrementEpoch_CallerIsEpochController() public {
        epochController.setCurrentEpochNumber(1);
        vm.prank(address(epochController));
        toksStaking.incrementEpoch();
        assertEq(toksStaking.getEpochStakedTotal(0), toksStaking.getStakedTotal() - toksStaking.getStakedTotalIneligible());
        assertEq(toksStaking.getEpochStakedTotal(1), 0);
    }

    function testIncrementEpoch_CallerIsNotEpochController() public {
        epochController.setCurrentEpochNumber(1);
        vm.prank(address(0x123));
        vm.expectRevert("ToksStaking: must be called by EpochController");
        toksStaking.incrementEpoch();
    }

    function testIncrementEpoch_NextEpochIsZero() public {
        epochController.setCurrentEpochNumber(0);
        vm.prank(address(epochController));
        toksStaking.incrementEpoch();
        assertEq(toksStaking.getEpochNumber(0), 1);
    }

    function testIncrementEpoch_NextEpochGreaterThanEpochsLength() public {
        epochController.setCurrentEpochNumber(3);
        vm.prank(owner);
        toksStaking.deposit(1000);
        vm.prank(owner);
        toksStaking.incrementEpoch();
        assertEq(toksStaking.getEpochNumber(3), 3);
    }

    function testIncrementEpoch_NextEpochLessThanEpochsLength() public {
        epochController.setCurrentEpochNumber(2);
        vm.prank(owner);
        toksStaking.deposit(1500);
        vm.prank(owner);
        toksStaking.incrementEpoch();
        assertEq(toksStaking.getEpochNumber(2), 2);
    }

    function testIncrementEpoch_NextEpochEqualsEpochsLength() public {
        epochController.setCurrentEpochNumber(1);
        vm.prank(owner);
        toksStaking.deposit(2000);
        vm.prank(owner);
        toksStaking.incrementEpoch();
        assertEq(toksStaking.getEpochNumber(1), 1);
    }

    function testIncrementEpoch_NextEpochLessThan2() public {
        epochController.setCurrentEpochNumber(1);
        vm.prank(owner);
        toksStaking.deposit(2500);
        vm.prank(owner);
        toksStaking.incrementEpoch();
        assertEq(toksStaking.getEpochNumber(1), 1);
    }

    function testIncrementEpoch_StakedTotalUpdates() public {
        vm.prank(owner);
        toksStaking.deposit(1000);
        vm.prank(owner);
        toksStaking.incrementEpoch();
        assertEq(toksStaking.getStakedTotal(), 1000);
    }

    function testIncrementEpoch_PreventOverwrite() public {
        epochController.setCurrentEpochNumber(2);
        vm.prank(owner);
        toksStaking.deposit(3000);
        vm.prank(owner);
        toksStaking.incrementEpoch();
        vm.prank(owner);
        toksStaking.incrementEpoch();
        assertEq(toksStaking.getEpochNumber(2), 2);
    }

    function testRecordExternalRewardDistribution_CallerIsToken() public {
        vm.prank(token);
        toksStaking.recordExternalRewardDistribution(token, 100, block.timestamp);
    }

    function testRecordExternalRewardDistribution_AmountGreaterThanZero() public {
        vm.prank(token);
        vm.expectRevert("ToksStaking: External reward distribution must be > 0");
        toksStaking.recordExternalRewardDistribution(token, 0, block.timestamp);
    }

    function testRecordExternalRewardDistribution_TokenAddressExists() public {
        vm.prank(token);
        toksStaking.recordExternalRewardDistribution(token, 100, block.timestamp);
        assertTrue(toksStaking.getEpochExternalRewardTokenExists(0, token));
    }

    function testRecordExternalRewardDistribution_TokenAddressDoesNotExist() public {
        address newToken = address(0x789);
        vm.prank(token);
        toksStaking.recordExternalRewardDistribution(newToken, 100, block.timestamp);
        assertTrue(toksStaking.getEpochExternalRewardTokenExists(0, newToken));
    }

    function testRecordExternalRewardDistribution_Success() public {
        vm.prank(token);
        toksStaking.recordExternalRewardDistribution(token, 100, block.timestamp);
        assertEq(toksStaking.getEpochExternalRewardTokenTotals(0, token), 100);
    }

    function testClaimExternalRewards_UserHasStaked() public {
        stakerAddresses = [user];
        stakerAmounts = [100];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        vm.prank(user);
        vm.expectRevert("ToksStaking: user has not staked");
        toksStaking.claimExternalRewards(vm.addr(1), 0);
    }

    function testClaimExternalRewards_EpochHasEnded() public {
        stakerAddresses = [user];
        stakerAmounts = [100];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        vm.prank(user);
        vm.expectRevert("ToksStaking: epoch has not ended");
        toksStaking.claimExternalRewards(user, 1);
    }

    function testClaimExternalRewards_UserHasAlreadyClaimed() public {
        stakerAddresses = [user];
        stakerAmounts = [100];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        vm.prank(user);
        toksStaking.claimExternalRewards(user, 0);
        vm.prank(user);
        vm.expectRevert("ToksStaking: User has already claimed for this epoch");
        toksStaking.claimExternalRewards(user, 0);
    }

    function testClaimExternalRewards_Success() public {
        stakerAddresses = [user];
        stakerAmounts = [100];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        vm.prank(user);
        toksStaking.claimExternalRewards(user, 0);
        assertTrue(toksStaking.userHasClaimedExternalRewards(user, 0));
    }

    function testEpochHasEnded_True() public {
        assertTrue(toksStaking.epochHasEnded(0));
    }

    function testEpochHasEnded_False() public {
        assertFalse(toksStaking.epochHasEnded(1));
    }

    function testUserHasClaimedExternalRewards_True() public {
        stakerAddresses = [user];
        stakerAmounts = [100];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        vm.prank(user);
        toksStaking.claimExternalRewards(user, 0);
        assertTrue(toksStaking.userHasClaimedExternalRewards(user, 0));
    }

    function testUserHasClaimedExternalRewards_False() public {
        stakerAddresses = [user];
        stakerAmounts = [100];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        assertFalse(toksStaking.userHasClaimedExternalRewards(user, 0));
    }

    function testUserPendingExternalRewards_UserHasNotClaimed() public {
        stakerAddresses = [user];
        stakerAmounts = [100];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        vm.prank(user);
        toksStaking.claimExternalRewards(user, 0);
        vm.expectRevert("ToksStaking: User has already claimed for this epoch");
        toksStaking.userPendingExternalRewards(user, 0);
    }

    function testUserPendingExternalRewards_UserHasStaked() public {
        stakerAddresses = [user];
        stakerAmounts = [100];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        vm.prank(address(0x123));
        vm.expectRevert("ToksStaking: user has not staked");
        toksStaking.userPendingExternalRewards(address(0x123), 0);
    }

    function testUserPendingExternalRewards_CalculateRewards() public {
        stakerAddresses = [user];
        stakerAmounts = [100];
        vm.prank(owner);
        toksStaking.initializeStakers(stakerAddresses, stakerAmounts);
        (address[] memory tokens, uint256[] memory rewards) = toksStaking.userPendingExternalRewards(user, 0);
        assertEq(tokens.length, 0);
        assertEq(rewards.length, 0);
    }

    function testDeposit_AmountGreaterThanZero() public {
        vm.prank(user);
        vm.expectRevert("ToksStaking: Invalid amount");
        toksStaking.deposit(0);
    }

    function testDeposit_Success() public {
        vm.prank(user);
        toksStaking.deposit(100);
        assertEq(toksStaking.balanceOf(user), 100);
    }

    function testDeposit_UserHasStaked() public {
        vm.prank(user);
        toksStaking.deposit(100);
        vm.prank(user);
        toksStaking.deposit(50);
        assertEq(toksStaking.balanceOf(user), 150);
    }

    function testDeposit_UserHasNotStaked() public {
        vm.prank(user);
        toksStaking.deposit(100);
        assertEq(toksStaking.balanceOf(user), 100);
    }

    function testWithdraw_BalanceSufficient() public {
        vm.prank(user);
        toksStaking.deposit(100);
        vm.prank(user);
        vm.expectRevert("ToksStaking: Invalid amount");
        toksStaking.withdraw(150);
    }

    function testWithdraw_Success() public {
        vm.prank(user);
        toksStaking.deposit(100);
        vm.prank(user);
        toksStaking.withdraw(50);
        assertEq(toksStaking.balanceOf(user), 50);
    }

    function testWithdraw_UserHasStaked() public {
        vm.prank(user);
        toksStaking.deposit(100);
        vm.prank(user);
        toksStaking.withdraw(50);
        assertEq(toksStaking.balanceOf(user), 50);
    }

    function testWithdraw_UserHasNotStaked() public {
        vm.prank(user);
        vm.expectRevert("ToksStaking: Invalid amount");
        toksStaking.withdraw(100);
    }

    function testWithdraw_SyncUserBalance() public {
        vm.prank(user);
        toksStaking.deposit(100);
        address user2 = address(0x456);
        vm.prank(user2);
        toksStaking.deposit(101);
        vm.prank(user2);
        toksStaking.transfer(user, 100);
        vm.prank(user);
        toksStaking.withdraw(50);
        assertEq(toksStaking.balanceOf(user), 150);
        assertEq(toksStaking.balanceOf(user2), 1);
    }

    function testWithdraw_PreventOverwriteFirstUser() public {
        vm.prank(user);
        toksStaking.deposit(100);
        address user2 = address(0x456);
        vm.prank(user2);
        vm.expectRevert("ToksStaking: Invalid amount");
        toksStaking.withdraw(100);
        assertEq(toksStaking.balanceOf(user), 100);
    }

    function testPause_OnlyOwner() public {
        vm.prank(address(0x123));
        vm.expectRevert("Ownable: caller is not the owner");
        toksStaking.pause();
    }

    function testPause_Success() public {
        vm.prank(owner);
        toksStaking.pause();
        assertTrue(toksStaking.paused());
    }

    function testUnpause_OnlyOwner() public {
        vm.prank(owner);
        toksStaking.pause();
        vm.prank(address(0x123));
        vm.expectRevert("Ownable: caller is not the owner");
        toksStaking.unpause();
    }

    function testUnpause_Success() public {
        vm.prank(owner);
        toksStaking.pause();
        vm.prank(owner);
        toksStaking.unpause();
        assertFalse(toksStaking.paused());
    }
}
