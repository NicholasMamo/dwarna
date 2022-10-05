// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

/// @title      Study - a contract that contains consent details for a study.
/// @author     Jacques Vella Critien
/// @dev        Version 0.3 - last updated 2022-05-19
///             Upgraded to include multiple studies in 1 contract
contract DwarnaData {

    /// @notice A consent change container.
    ///         This struct contains information related to when the participant changed their consent.
    ///         Accompanying each consent change is the associated timestamp.
    struct Consent {
        uint timestamp;
        bool consent;
    }

    /// @notice A study container.
    ///         This struct contains information related to the study and its participants
    struct Study {

        uint created;
        /// @notice The users' consent status.
        ///         This is stored in the form of a mapping.
        ///         Each address is associated with a historical list of consent changes.
        ///         This creates an audit trail.
        /// @dev    The consent changes are stored as an array, which is naturally ordered.
        mapping (address => Consent[]) participant_consent;

        /// @notice The list of consenting participants.
        /// @dev    Mappings are not like some other associative arrays - the keys cannot be iterated.
        ///         The participants list is used to keep track of addresses that are currently in use.
        address[] participants;

        /// @notice The list of all participants that ever participated.
        /// @dev    Mappings are not like some other associative arrays - the keys cannot be iterated.
        ///         The participants list is used to keep track of addresses that are currently in use.
        address[] all_participants;
    }

    /// @notice Holds studies
    mapping(string => Study) public studies;

    /// @notice Holds the creator's address
    address public owner;

    /// @notice Holds the logic contract's address
    address public logicAddress;

    /// @author Jacques Vella Critien
    /// @notice Set the address of the creator to restrict changes
    constructor() { 
        owner = msg.sender;
    }

    /// @notice Ensures the request is coming from the logic contract
    modifier isLogic(){
        require(msg.sender == logicAddress, "Only the logic address can do this");
        _;
    }
    
    /// @notice Ensures the request is coming from the data contract's address
    modifier isOwner(){
        require(msg.sender == owner, "Only the owner can do this");
        _;
    }

    /// @notice Ensures the study does not exist
    /// @param  id The id of the study to check
    modifier studyFree(string memory id){
        require(studies[id].created == 0, "Study already exists");
        _;
    }

    /// @notice Ensures the study exists
    /// @param  id The id of the study to check
    modifier studyExists(string memory id){
        require(studies[id].created != 0, "Study does not exist");
        _;
    }

    /// @notice Ensures the participant is not already consented
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    modifier notConsented(string memory study, address participant){
        require(!hasConsented(study, participant), "Participant already consented the study");
        _;
    }

    /// @notice Ensures the participant is consented
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    modifier alreadyConsented(string memory study, address participant){
        require(hasConsented(study, participant), "Participant has to be consented");
        _;
    }
    
    /// @notice Ensures the name of the study is not empty
    /// @param  id The id of the study to check
    modifier studyNameCheck(string memory id){
        require(keccak256(abi.encodePacked(id)) != keccak256(abi.encodePacked("")), "Study id cannot be empty");
        _;
    }

    /// @notice Changes the logic contract address
    ///         This allows another address to query the data
    /// @param  logic The address of the new logic contract address
    function changeLogic(address logic) public isOwner {
        logicAddress = logic;
    }

    /// @notice Changes the owner of this contract
    /// @param  new_owner The address of the new owner
    function changeOwner(address new_owner) public isOwner {
        owner = new_owner;
    }

    /// @notice Create new study
    /// @param  id The id of the study
    function addStudy(string memory id) public isLogic studyFree(id) studyNameCheck(id) {
        Study storage study = studies[id];
        study.created = block.timestamp;
    }

    /// @notice Check whether the participant has consented to the use of their sample in this study.
    /// @param  participant The address of the participant that will be queried.
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    /// @return A boolean representing whether the participant has an active consent for the use of his data in the study.
    function hasConsented(string memory study, address participant) public view studyExists(study) isLogic returns(bool) {
        uint256 history_length = studies[study].participant_consent[participant].length; // get the length of the participant's consent trail
        if (history_length == 0) {
            return false; // if the participant has never interacted with the study in the first place, return false immediately
        } else {
            return studies[study].participant_consent[participant][history_length - 1].consent; // otherwise, retrieve the last consent status
        }
    }

    /// @notice Check whether the participant has ever consented to the use of their sample in this study.
    /// @param  participant The address of the participant that will be queried.
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    /// @return A boolean representing whether the participant has an active consent for the use of his data in the study.
    function hasEverConsented(string memory study, address participant) public view studyExists(study) isLogic returns(bool) {
        return studies[study].participant_consent[participant].length > 0;
    }

    /// @notice The centerpiece of dynamic consent.
    ///         The sender gives consent to the use of their sample in the study.
    /// @dev    The function sets the mapping value that corresponds to the participant to true, whatever the initial value.
    ///         If the participant has not consented yet, or withdrew said consent, add them to the list of participants first.
    ///         This avoids 'double-spending' consent, or giving consent twice in quick succession.
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    function addConsentToStudy(string memory study, address participant) public notConsented(study, participant) studyExists(study) isLogic {
        //check if consented and if not, add participant
        if (!hasConsented(study, participant)){
            studies[study].participants.push(participant);
        }

        //check if first time consenting, if so add to all time participants
        if (!hasEverConsented(study, participant)){
            studies[study].all_participants.push(participant);
        }


        studies[study].participant_consent[participant].push(Consent(block.timestamp, true));
    }

    /// @notice The centerpiece of dynamic consent.
    ///         The sender withdraws consent to the use of their sample in the study.
    /// @dev    The function sets the mapping value that corresponds to the participant to false, whatever the initial value.
    ///         If the participant had given consent and is now withdrawing it, remove the participant from the list of consenting participants.
    ///         The deletion uses the swap technique.
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    function withdrawConsentFromStudy(string memory study, address participant) public isLogic alreadyConsented(study, participant) {
        if (hasConsented(study, participant)) {
            for (uint256 i = 0; i < studies[study].participants.length; i++) {
                if (studies[study].participants[i] == participant) {
                    studies[study].participants[i] = studies[study].participants[studies[study].participants.length - 1]; // replace the current element with the last one
                    studies[study].participants.pop(); // remove the last element, which is now a duplicate, and thus refers to an unwanted address
                    if (i > 0){
                        i--; // go back one step just in case the swapped element should be deleted as well
                    }
                }
            }
        }

        studies[study].participant_consent[participant].push(Consent(block.timestamp, false));
    }

    /// @notice Obtains the consenting participants of the study
    /// @param  study The id of the study to check
    /// @return An array of addresses of participants
    function getStudyParticipants(string memory study) public view studyExists(study) isLogic returns(address[] memory) {
        return studies[study].participants;
    }

    /// @notice Obtains all the participants of the study
    /// @param  study The id of the study to check
    /// @return An array of addresses of participants
    function getAllStudyParticipants(string memory study) public view studyExists(study) isLogic returns(address[] memory) {
        return studies[study].all_participants;
    }

    /// @notice Obtains the consent trail of a participant of a particular study
    /// @param  study The id of the study to check
    /// @param  participant The address of the participant
    /// @return An array of consents representing the consent trail of a participant
    function getStudyConsentTrailOfParticipant(string memory study, address participant) public view studyExists(study) isLogic returns(Consent[] memory) {
        return studies[study].participant_consent[participant];
    }
}