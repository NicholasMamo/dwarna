// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./DwarnaData.sol";

/// @title      Study - a contract that contains consent details for a study.
/// @author     Jacques Vella Critien
/// @dev        Version 0.3 - last updated 2022-05-19
///             Upgraded to include multiple studies in 1 contract
contract Dwarna {

    /// @notice Holds the creator's address
    address public owner;

    /// @notice Holds the data contract
    DwarnaData dwarnaData;

    /// @author Jacques Vella Critien
    /// @notice Create the study with its most basic details.
    ///         No consent information is collected initially.
    /// @param  dataAddress The address of the data contract
    constructor(address dataAddress) { 
        owner = msg.sender;
        dwarnaData = DwarnaData(dataAddress);
    }

    /// @notice Ensures the request is coming from the data contract's address
    modifier isOwner(){
        require(msg.sender == owner, "Only the owner can do this");
        _;
    }

    /// @notice Changes the data contract address
    ///         This allows to change the data
    /// @param  data The address of the new data contract address
    function changeLogic(address data) public isOwner {
        dwarnaData = DwarnaData(data);
    }

    /// @notice Changes the owner of this contract
    /// @param  new_owner The address of the new owner
    function changeOwner(address new_owner) public isOwner {
        owner = new_owner;
    }

    /// @notice Create new study
    /// @param  id The id of the study
    function createStudy(string memory id) public isOwner {
        dwarnaData.addStudy(id);
    }

    /// @notice The centerpiece of dynamic consent.
    ///         The sender gives consent to the use of their sample in the study.
    /// @dev    The function sets the mapping value that corresponds to the participant to true, whatever the initial value.
    ///         If the participant has not consented yet, or withdrew said consent, add them to the list of participants first.
    ///         This avoids 'double-spending' consent, or giving consent twice in quick succession.
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    function addConsentToStudy(string memory study, address participant) public isOwner {
        dwarnaData.addConsentToStudy(study, participant);
    }

   /// @notice The centerpiece of dynamic consent.
    ///         The sender withdraws consent to the use of their sample in the study.
    /// @dev    The function sets the mapping value that corresponds to the participant to false, whatever the initial value.
    ///         If the participant had given consent and is now withdrawing it, remove the participant from the list of consenting participants.
    ///         The deletion uses the swap technique.
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    function withdrawConsentFromStudy(string memory study, address participant) public isOwner {
        dwarnaData.withdrawConsentFromStudy(study, participant);
    }

    /// @notice Check whether the participant has consented to the use of their sample in this study.
    /// @param  participant The address of the participant that will be queried.
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    /// @return A boolean representing whether the participant has an active consent for the use of his data in the study.
    function hasConsented(string memory study, address participant) public view returns(bool) {
        return dwarnaData.hasConsented(study, participant);
    }

    /// @notice Get a list of timestamps when a participant's consent was changed.
    /// @dev    At the time of writing (2018-12-05), Solidity does not allow returning dynamic arrays or structs.
    ///         The solution is to return a list of timestamps for a participant.
    ///         These timestamps can be used to construct a timeline by querying each timestamp.
    /// @param  study The study to be queried.
    /// @param  participant The address of the participant that will be queried.
    /// @return A list of timestamps when the participant updated their consent status.
    function getConsentTimestamps(string memory study, address participant) public view returns(uint [] memory) {
        DwarnaData.Consent [] memory consent_trail = dwarnaData.getStudyConsentTrailOfParticipant(study, participant);
        uint [] memory timestamps = new uint[](consent_trail.length);

        for (uint256 i = 0; i < consent_trail.length; i++) {
            timestamps[i] = consent_trail[i].timestamp;
        }

        return timestamps;
    }

    /// @notice Get consent trail
    /// @dev    At the time of writing (2018-12-05), Solidity does not allow returning dynamic arrays or structs.
    ///         The solution is to return a list of timestamps for a participant.
    ///         These timestamps can be used to construct a timeline by querying each timestamp.
    /// @param  study The study to be queried.
    /// @param  participant The address of the participant that will be queried.
    /// @return A list of timestamps when the participant updated their consent status.
    function getConsentTrail(string memory study, address participant) public view returns(uint[] memory, bool[] memory) {
        DwarnaData.Consent [] memory consent_trail = dwarnaData.getStudyConsentTrailOfParticipant(study, participant);
        uint[] memory timestamps = new uint[](consent_trail.length);
        bool[] memory statuses = new bool[](consent_trail.length);

        for (uint256 i = 0; i < consent_trail.length; i++) {
            timestamps[i] = consent_trail[i].timestamp;
            statuses[i] = consent_trail[i].consent;
        }

        return (timestamps, statuses);
    }

    /// @notice Get the participant's consent at a particular timestamp.
    ///         If the participant did not change their consent at this timestamp, false is returned.
    /// @param  study The study to be queried.
    /// @param  participant The address of the participant that will be queried.
    /// @param  timestamp The timestamp whose consent status needs to be known.
    /// @return The participant's consent status set at the given timestamp, or false if the participant did not update it at that moment.
    function GetConsentAt(string memory study, address participant, uint timestamp) public view returns(bool) {
        DwarnaData.Consent [] memory consent_trail = dwarnaData.getStudyConsentTrailOfParticipant(study, participant);

        for (uint256 i = 0; i < consent_trail.length; i++) {
            if (consent_trail[i].timestamp == timestamp) {
                return consent_trail[i].consent;
            }
        }

        return false;
    }

    /// @notice Get the list of participants that are participating in the study.
    /// @dev    The function double-checks the list of participants, ensuring that they are indeed consenting participants.
    /// @param  study The study to be queried.
    /// @return A list of participants that have consented to the use of their data in the study.
    function getConsentingParticipants(string memory study) public view returns(address[] memory) {
        address[] memory participants = dwarnaData.getStudyParticipants(study);

        return participants;
    }


    /// @notice Get the list of all participants that ever participated in the study.
    /// @dev    The function double-checks the list of participants, ensuring that they are indeed consenting participants.
    /// @param  study The study to be queried.
    /// @return A list of participants that have consented to the use of their data in the study.
    function getAllStudyParticipants(string memory study) public view returns(address[] memory) {
        address[] memory participants = dwarnaData.getAllStudyParticipants(study);

        return participants;
    }

}
