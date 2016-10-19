import rosbag
import numpy as np
import matplotlib.pyplot as plot
import tf.transformations


def bag_topic_list(bag):
    return bag.get_type_and_topic_info()[1].keys()


def topic_info(bag, topic):
    msgType, length, _, freq = bag.get_type_and_topic_info()[1][topic]
    return msgType, length, freq


if __name__ == "__main__":
    bagMocap = rosbag.Bag('unitDiamondMocap.bag')
    bagSim = rosbag.Bag('unitDiamondSim.bag')

    # extract motion capture data
    mocapPosition = np.array([[], [], []])
    mocapOrientation = np.array([[], [], []])
    timeMocap = np.array([])

    for msg in bagMocap.read_messages("/mavros/mocap/pose"):
        position = msg.message.pose.position
        orientation = msg.message.pose.orientation
        timeMocap = np.append(timeMocap, msg.timestamp.to_time())
        mocapPosition = np.column_stack((mocapPosition, (position.x, position.y, position.z)))
        # mocapOrientation = np.column_stack((mocapOrientation, (orientation.x, orientation.y, orientation.z)))

    timeMocap = timeMocap - bagMocap.get_start_time()

    # extract IMU data
    imuPosition = np.array([[], [], []])
    imuOrientation = np.array([[], [], []])
    timeIMU = np.array([])

    for msg in bagMocap.read_messages("/mavros/local_position/pose"):
        position = msg.message.pose.position
        orientation = msg.message.pose.orientation
        timeIMU = np.append(timeIMU, msg.timestamp.to_time())
        imuPosition = np.column_stack((imuPosition, (position.x, position.y, position.z)))
        # imuOrientation = np.column_stack((imuOrientation, (orientation.x, orientation.y, orientation.z)))

    timeIMU = timeIMU - bagMocap.get_start_time()

    # find matching time indices for IMU and Mocap data
    matchingMocapIdx = np.array([]).astype(int)
    matchingIMUIdx = np.array([]).astype(int)
    for tIMU in timeIMU:
        for tMocap in timeMocap:
            if abs(tIMU - tMocap) <= 0.005:
                matchingIMUIdx = np.append(matchingIMUIdx, np.where(timeIMU == tIMU)[0][0])
                matchingMocapIdx = np.append(matchingMocapIdx, np.where(timeMocap == tMocap)[0][0])

    commonIMUTime = timeMocap[matchingMocapIdx]
    downsampledMocapPos = mocapPosition[:, matchingMocapIdx]
    downsampledIMUPos = imuPosition[:, matchingIMUIdx]

    # find starting index for offboard mode
    for _, msg, t in bagMocap.read_messages("/mavros/state"):
        if msg.mode == "OFFBOARD":
            startOffboard = t.to_time() - bagMocap.get_start_time()
            break

    for t in timeMocap:
        if abs(t - startOffboard) <= 0.01:
            offboardIdx = np.where(timeMocap == t)[0][0]
            startOffboard = t
            break


    # extract simulation data
    simPosition = np.array([[], [], []])
    simOrientation = np.array([[], [], []])
    timeSim = np.array([])

    for msg in bagSim.read_messages("/mavros/local_position/pose"):
        position = msg.message.pose.position
        orientation = msg.message.pose.orientation
        timeSim = np.append(timeSim, msg.timestamp.to_time())
        simPosition = np.column_stack((simPosition, (position.x, position.y, position.z)))
        # simOrientation = np.column_stack((simOrientation, (orientation.x, orientation.y, orientation.z)))

    timeSim = timeSim - bagSim.get_start_time()

    # find starting index for arming
    for _, msg, t in bagSim.read_messages("/mavros/state"):
        if msg.armed:
            startSim = t.to_time() - bagSim.get_start_time()
            break

    for t in timeSim:
        if abs(t - startSim) <= 0.015:  # TODO set these thresholds by using the rate of the topic?
            armIdx = np.where(timeSim == t)[0][0]
            startSim = t
            break

    armIdx -= 25
    simPosition = simPosition[:, armIdx:]
    mocapPosition = mocapPosition[:, offboardIdx:]
    timeSim = timeSim[armIdx:] - timeSim[armIdx]
    timeMocap = timeMocap[offboardIdx:] - startOffboard

    # find matching time indices for Sim and Mocap data
    matchingMocapIdx = np.array([]).astype(int)
    matchingSimIdx = np.array([]).astype(int)
    for tSim in timeSim:
        for tMocap in timeMocap:
            if abs(tSim - tMocap) <= 0.005:
                matchingSimIdx = np.append(matchingSimIdx, np.where(timeSim == tSim)[0][0])
                matchingMocapIdx = np.append(matchingMocapIdx, np.where(timeMocap == tMocap)[0][0])

    commonSimTime = timeMocap[matchingMocapIdx]
    downsampledMocapPos2 = mocapPosition[:, matchingMocapIdx]
    downsampledSimPos = simPosition[:, matchingSimIdx]

    error = np.mean(np.sqrt(np.square(downsampledMocapPos2 - downsampledSimPos)))
    print "sim vs mocap error for mocap time length:", error

    plot.figure(1)
    plot.subplot(311)
    plot.title("Position comparison for PX4 Position Controller")
    plot.plot(timeSim, simPosition[0], label="sim")
    plot.plot(timeMocap, mocapPosition[0], label="mocap")
    plot.legend()
    plot.ylabel("X [m]")
    plot.subplot(312)
    plot.plot(timeSim, simPosition[1])
    plot.plot(timeMocap, mocapPosition[1])
    plot.ylabel("Y [m]")
    plot.subplot(313)
    plot.plot(timeSim, simPosition[2])
    plot.plot(timeMocap, mocapPosition[2])
    plot.xlabel("Time [s]")
    plot.ylabel("Y [m]")
    plot.show()
