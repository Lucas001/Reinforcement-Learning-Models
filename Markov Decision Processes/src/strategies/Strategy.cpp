#include "Strategy.h"

Strategy::Strategy(){
    areaTarget = 10.f*SIMULATOR_TO_VSS;
    distProjBallWall = 5.f*SIMULATOR_TO_VSS;
    maxDiffRobotPos = 3.5f*SIMULATOR_TO_VSS;    

    sizeRobot = 8*SIMULATOR_TO_VSS;
    attackDir = 1;
    deltaTime = 0.001f;
    timeToFullHistory = 0.f;
    numFramesPerSec = 30;
    ballTarget = btVector3(0,0,0);

    runningRL = false;
    reachDeepState = false;
    reachingPoint = false;

    artInt = new ArtificialIntelligence();

    begin_time  = clock();
}

Strategy::~Strategy(){
    strategyHistory.clear();
}

void Strategy::runStrategy(vector<RobotStrategy*> robotStrategiesTeam,vector<RobotStrategy*> robotStrategiesAdv,btVector3 target, Map map){
    deltaTime = float( clock () - begin_time ) /  CLOCKS_PER_SEC;
    begin_time = clock();
    ballTarget = target;

    if(runningRL){
        if(!reachDeepState)
            reachDeepState = artInt->calculateMDPStates();
    }else{
        artInt->setMap(map);
        runningRL = true;
    }

    printMDPState();

    this->robotStrategiesTeam = robotStrategiesTeam;
    this->robotStrategiesAdv = robotStrategiesAdv;
    this->targetPos = target;

    if(strategyHistory.size() == numFramesPerSec){
        updateDynamics();
    }

    for(int i = 0; i < robotStrategiesTeam.size(); i++){
        controlLocalStrategy(robotStrategiesTeam[i]);
    }

    updateStrategiesHistory();
}

void Strategy::reinitStrategy(){
    runningRL = false;
    reachDeepState = false;
    reachingPoint = false;
    artInt = new ArtificialIntelligence();
    drawComponents.clear();
}

void Strategy::updateStrategiesHistory(){
    strategyHistory.clear();
    strategyHistory.push_back(this);
}

void Strategy::printMDPState(){
    Map map = artInt->getMdp();
    float maxReward = artInt->getMaxReward();
    float impartState = artInt->getImpartialState();
    float minReward = artInt->getMinReward();

    vector<DrawComponents> listDrawComponents;
    for(int i = 0;i < map.size();i++){
        for(int j = 0;j < map.at(0).size();j++){
            Color color;
            if(map.at(i).at(j) < 0){
                float percColor = map.at(i).at(j)/minReward;
                if(percColor > 1) percColor = 1;
                color = Color(percColor, 0,0);
            }else{
                float percColor = map.at(i).at(j)/maxReward;
                if(percColor > 1) percColor = 1;
                color = Color(0, percColor,0);
            }
                
            if(map.at(i).at(j) == impartState) color = Color(0,0,1);

            btVector3 centerPt(-10+i*SCALE_MAP+SCALE_MAP/2,2.5,-10+j*SCALE_MAP+SCALE_MAP/2);
            vector<btVector3> listVectors;
            listVectors.push_back(centerPt + btVector3(5,0,5));
            listVectors.push_back(centerPt + btVector3(5,0,-5));
            listVectors.push_back(centerPt + btVector3(-5,0,-5));
            listVectors.push_back(centerPt + btVector3(-5,0,5));

            DrawComponents drawComp(listVectors, color);

            listDrawComponents.push_back(drawComp);
        }
    }

    drawComponents = listDrawComponents;
}

void Strategy::controlLocalStrategy(RobotStrategy* robotStrategy){
    
    if(!reachDeepState) return; 

    calculateNextTarget(robotStrategy);
    updateActionMotion(robotStrategy);
}

void Strategy::calculateNextTarget(RobotStrategy* robotStrategy){
    int agentX = robotStrategy->getPosition().getX()/SCALE_MAP;
    int agentZ = robotStrategy->getPosition().getZ()/SCALE_MAP;
    if(!reachingPoint){

        vector< vector<string> > policy = artInt->getPolicy();
        char action = policy.at(agentX+1).at(agentZ+1).at(0);
        switch(action){
            case '^':{
                agentX--;
            }break;
            case '>':{
                agentZ++;
            }break;
            case 'v':{
                agentX++;
            }break;
            case '<':{
                agentZ--;
            }break;
        }
    }

    robotStrategy->setTargetPosition(btVector3((agentX+0.5)*SCALE_MAP, 0, (agentZ+0.5)*SCALE_MAP));
}

float Strategy::handleLocalMaxVelocity(RobotStrategy* robotStrategy){
	float perc;

	float distToBall = robotStrategy->getTargetDistance();
	float actDistBall = robotStrategy->getActDistToTarget();

	if(distToBall < actDistBall) perc = distToBall/actDistBall;
	else perc = 1;

    if(perc < 0.4) perc = 0.4;

	return perc;
}

void Strategy::updateActionMotion(RobotStrategy* robotStrategy){
	float maxAngToBall = robotStrategy->getMaxAngToTarget();
	float currAngToBall = robotStrategy->getPointAngle(robotStrategy->getTargetPosition());
	float maxVelocity = robotStrategy->getMaxCommand();

	float handMaxVel = maxVelocity*handleLocalMaxVelocity(robotStrategy);
	float percAng = 1 - fabs(currAngToBall)/maxAngToBall;
	float handLowVel = handMaxVel*percAng;

	if(fabs(currAngToBall) < maxAngToBall){
		if(currAngToBall < 0){
			robotStrategy->updateCommand(handLowVel,handMaxVel);
		}else{
			robotStrategy->updateCommand(handMaxVel,handLowVel);
		}
        robotStrategy->setStandardMotion(true);
	}else{
		if(currAngToBall < 0){
			robotStrategy->updateCommand(-maxVelocity/TURN_ROBOT,maxVelocity/TURN_ROBOT);
		}else{
			robotStrategy->updateCommand(maxVelocity/TURN_ROBOT,-maxVelocity/TURN_ROBOT);
		}
	}
}