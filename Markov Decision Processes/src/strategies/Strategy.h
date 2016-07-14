#ifndef STRATEGY_H_
#define STRATEGY_H_

#define SIMULATOR_TO_VSS 1.0
#define TURN_ROBOT 1.0

#include "Header.h"
#include "ModelStrategy.h"
#include "ArtificialIntelligence.h"

class Strategy : public ModelStrategy{
private:
	bool reachingPoint;

	float areaTarget;
    float sizeRobot;
    float distProjBallWall;
    float maxDiffRobotPos;
    int timeToFullHistory;

    bool runningRL;
    bool reachDeepState;

    ArtificialIntelligence* artInt;

    btVector3 ballTarget;

	float timeStep;

    void updateStrategiesHistory();

	void controlLocalStrategy(RobotStrategy* robotStrategy);

	void updateActionMotion(RobotStrategy* robotStrategy);

	float handleLocalMaxVelocity(RobotStrategy* robotStrategy);

	void printMDPState();
	void calculateNextTarget(RobotStrategy* robotStrategy);
public:
	Strategy();
	~Strategy();

	void reinitStrategy();

	void runStrategy(vector<RobotStrategy*> robotStrategiesTeam,vector<RobotStrategy*> robotStrategiesAdv,btVector3 ballPos, Map map);
};

#endif
