#ifndef ARTIFICIAL_INTELIGENCE_H_
#define ARTIFICIAL_INTELIGENCE_H_

#define EPSILON 0.009

#include "Header.h"

class ArtificialIntelligence{
private: 
    int gameDepth;
    int gameWidth;

    int countQ;

    Map map;
    int generationsRL;

    Map prevMDP;
    Map mdp;
    vector< vector<string> > policy;
    float accuracy;
    float noise;
    float discount;
    float actReward;

    float impartialState;
    float maxReward;
    float minReward;

    
    float calculateActualState(float top, float bottom, float left, float right, int i, int j);
    float calculateQValue(float front, float left, float right);

    void searchAgentSetPositions();

    bool reachDeepState();

    void showBestResult();

public:
	ArtificialIntelligence();

    Map getMdp() {return mdp;}
    vector< vector<string> > getPolicy() { return policy; }
    void setMap(Map map);

    bool calculateMDPStates();

    float getMaxReward() { return maxReward; }
    float getImpartialState() { return impartialState; }
    float getMinReward() { return minReward; }
};

#endif