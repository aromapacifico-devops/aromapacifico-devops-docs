# LoRa farms use a cumulative application acknowledgement and a versioned batch frame

## Context

A farm out of coverage sends its readings over LoRa to a shared gateway. The node keeps readings for 24 hours at most and deletes a reading only after it knows the platform has it. A LoRa node has no Device Shadow, its frames are short, and the data rate, the payload limit and the transmission rules depend on a regional plan and on regulation that are not settled. A radio acknowledgement shows that a frame reached a gateway or the network server. It does not show that the platform stored the reading.

## Options

For the acknowledgement, a confirmed uplink for each frame, a cumulative application acknowledgement sent as a downlink, or repeated frames with no acknowledgement. For the time, a capture time from the node clock, or a time estimated by the platform from the moment it received the frame. For the configuration, a downlink with the applied version reported, or a request in every uplink. For the frame, one reading in each frame, or a versioned frame with several readings.

## Decision

The node sends unconfirmed uplinks. The platform emits one cumulative acknowledgement after it has stored the readings. It carries a declared floor and a persisted limit, so that sequences the node declared expired are kept apart from sequences the platform stored, and the node deletes pending records only up to the persisted limit. A pending record leaves the node without a confirmation only when it expires at the limit of 24 hours, which is a counted loss and never a delivery. The capture time stays a requirement of the node clock, and the platform keeps the capture time, the transmission time, the reception time and the quality of the clock apart, with the age of a record as a complementary field. The platform keeps the desired configuration and sends it as a downlink, and the node reports the version it applied, with reception, validation and application kept apart. The node sends a versioned binary frame with several readings when the size and the transmission rules allow it, and the size limit comes from the regional plan and the data rate in use. Configuration and firmware update are separate. The solution is not declared ready for deployment while the regulation, the regional plan and the compatibility of the hardware stay unverified.

## Consequences

No pending reading is deleted before the limit of 24 hours, and a loss becomes visible and counted. The design guarantees no delivery. A frame can be lost for range, collision or outage, and a record that reaches 24 hours is deleted as expired, which does not mean it was delivered. Repeats of records that the platform already has are expected and ignored. The acknowledgement arrives one cycle after the uplink at the earliest, so a lost frame is repeated two cycles after the first send. The header of the frame takes bytes that matter under a 400 ms dwell limit, and a shorter header for continuation frames is a possible later version. A change of the regional plan, of the dwell setting or of the network server behavior can reopen the size budget and the acknowledgement.
