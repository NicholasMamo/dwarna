pragma solidity ^0.5.0;

/// @title      Study - a contract that contains consent details for a study.
/// @author     Nicholas Mamo
/// @dev        Version 0.2.5 - last updated 2018-12-05
///             Added functions to help construct a consent trail for a participant.
contract Study {

    /// @notice A consent change container.
    ///         This struct contains information related to when the participant changed their consent.
    ///         Accompanying each consent change is the associated timestamp.
    struct Consent {
        uint timestamp;
        bool consent;
    }

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

    /// @author Nicholas Mamo
    /// @notice Create the study with its most basic details.
    ///         No consent information is collected initially.
    constructor() public { }

    /// @author Nicholas Mamo
    /// @notice The centerpiece of dynamic consent.
    ///         The sender gives consent to the use of their sample in the study.
    /// @dev    The function sets the mapping value that corresponds to the participant to true, whatever the initial value.
    ///         If the participant has not consented yet, or withdrew said consent, add them to the list of participants first.
    ///         This avoids 'double-spending' consent, or giving consent twice in quick succession.
    function give_consent() public {
        if (!has_consented())
            participants.push(msg.sender);

        participant_consent[msg.sender].push(Consent(block.timestamp, true));
    }

    /// @author Nicholas Mamo
    /// @notice The centerpiece of dynamic consent.
    ///         The sender withdraws consent to the use of their sample in the study.
    /// @dev    The function sets the mapping value that corresponds to the participant to false, whatever the initial value.
    ///         If the participant had given consent and is now withdrawing it, remove the participant from the list of consenting participants.
    ///         The deletion uses the swap technique.
    function withdraw_consent() public {
        if (has_consented()) {
            for (uint i = 0; i < participants.length; i++) {
                if (participants[i] == msg.sender) {
                    participants[i] = participants[participants.length - 1]; // replace the current element with the last one
                    participants.length--; // remove the last element, which is now a duplicate, and thus refers to an unwanted address
                    i--; // go back one step just in case the swapped element should be deleted as well
                }
            }
        }

        participant_consent[msg.sender].push(Consent(block.timestamp, false));
    }

    /// @author Nicholas Mamo
    /// @notice Check whether the participant has consented to the use of their sample in this study.
    /// @param  participant The address of the participant that will be queried.
    /// @return A boolean representing whether the participant has an active consent for the use of his data in the study.
    function has_consented(address participant) public view returns(bool) {
        uint history_length = participant_consent[participant].length; // get the length of the participant's consent trail
        if (history_length == 0) {
            return false; // if the participant has never interacted with the study in the first place, return false immediately
        } else {
            return participant_consent[participant][history_length - 1].consent; // otherwise, retrieve the last consent status
        }
    }

    /// @author Nicholas Mamo
    /// @notice Check whether the participant has consented to the use of their sample in this study.
    /// @dev    By default, the mapping value is 0, or false.
    /// @return A boolean representing whether the participant has an active consent for the use of his data in the study.
    function has_consented() public view returns(bool) {
        return has_consented(msg.sender);
    }

    /// @author Nicholas Mamo
    /// @notice Get a list of timestamps when a participant's consent was changed.
    /// @dev    At the time of writing (2018-12-05), Solidity does not allow returning dynamic arrays or structs.
    ///         The solution is to return a list of timestamps for a participant.
    ///         These timestamps can be used to construct a timeline by querying each timestamp.
    /// @param  participant The address of the participant that will be queried.
    /// @return A list of timestamps when the participant updated their consent status.
    function get_consent_timestamps(address participant) public view returns(uint [] memory) {
        Consent [] memory consent_trail = participant_consent[participant];
        uint [] memory timestamps = new uint[](consent_trail.length);

        for (uint i = 0; i < consent_trail.length; i++) {
            timestamps[i] = consent_trail[i].timestamp;
        }

        return timestamps;
    }

    /// @author Nicholas Mamo
    /// @notice Get the participant's consent at a particular timestamp.
    ///         If the participant did not change their consent at this timestamp, false is returned.
    /// @param  participant The address of the participant that will be queried.
    /// @param  timestamp The timestamp whose consent status needs to be known.
    /// @return The participant's consent status set at the given timestamp, or false if the participant did not update it at that moment.
    function get_consent_at(address participant, uint timestamp) public view returns(bool) {
        Consent [] memory consent_trail = participant_consent[participant];

        for (uint i = 0; i < consent_trail.length; i++) {
            if (consent_trail[i].timestamp == timestamp) {
                return consent_trail[i].consent;
            }
        }

        return false;
    }

    /// @author Nicholas Mamo
    /// @notice Get the list of participants that are participating in the study.
    /// @dev    The function double-checks the list of participants, ensuring that they are indeed consenting participants.
    /// @return A list of participants that have consented to the use of their data in the study.
    function get_consenting_participants() public view returns(address[] memory) {
        for (uint i = 0; i < participants.length; i++) {
            assert(has_consented(participants[i]));
        }

        return participants;
    }

}
