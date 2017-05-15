#ifndef ModelStrategy_H_
#define ModelStrategy_H_

#include "Header.h"
#include "RobotStrategy.h"

#define TURN_ROBOT 2
#define SIMULATOR_TO_VSS 1

struct DrawComponents{
		vector<btVector3> drawPoints;
		Color color;

		DrawComponents(vector<btVector3> drawPts, Color clr):drawPoints(drawPts),color(clr){}
};

class ModelStrategy{
	
protected:
	vector<DrawComponents> drawComponents;

    clock_t begin_time;
    float deltaTime;
    int numFramesPerSec;

    int attackDir;

	btVector3 targetPos;
	btVector3 targetVel;
	btVector3 targetAce;
	btVector3 posGoalpost;
	float timeStep;

    vector<RobotStrategy*> robotStrategiesTeam;
	vector<RobotStrategy*> robotStrategiesAdv;
	vector<ModelStrategy*> strategyHistory;

	virtual void updateStrategiesHistory();

    virtual void updateTargetPosition(RobotStrategy* robotStrategy);

    virtual void updateDynamics();
    virtual void updateLocalDynamics(RobotStrategy* cur, RobotStrategy* old);

public:
    ModelStrategy();
    void runStrategy();
	virtual void runStrategy(vector<RobotStrategy*> robotStrategiesTeam, vector<RobotStrategy*> robotStrategiesAdv, btVector3 targetPos,Map map) = 0;
	virtual void reinitStrategy() {}
	
	virtual void setAttackDir(int goalpostDir);
	int getAttackDir(){ return attackDir; }
    virtual void setFramesSec(int frames);

	virtual vector<ModelStrategy*> getStrategyHistory(){ return strategyHistory; }

	virtual vector<RobotStrategy*> getRobotStrategiesTeam(){ return robotStrategiesTeam; }
	virtual vector<RobotStrategy*> getRobotStrategiesAdv(){ return robotStrategiesAdv; }

	btVector3 getTargetPosition(){ return targetPos; }
	btVector3 getTargetVelocity(){ return targetVel; }
	btVector3 getTargetAcceleration(){ return targetAce; }

	float getAttackGoal(){ return attackDir; }

	vector<DrawComponents> getDrawComponents() { return drawComponents; }
};

#endif
