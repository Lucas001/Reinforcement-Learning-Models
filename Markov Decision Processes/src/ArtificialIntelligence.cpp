#include "ArtificialIntelligence.h"

ArtificialIntelligence::ArtificialIntelligence(){
	accuracy = 0.8;
	noise = 0.1;
	discount = 1.0;
	actReward = -0.5;
	generationsRL = 0;

	impartialState = -15;
	maxReward = 20;
	minReward = -5;
}

void ArtificialIntelligence::searchAgentSetPositions(){
	for(int i = 0; i < gameDepth;i++){
		vector<float> row;
		vector<string> rowAction;
		for(int j = 0; j < gameWidth;j++){
			rowAction.push_back(".");
			if(i == 0 || j == 0 || i == gameDepth - 1 || j == gameWidth - 1)
				row.push_back(-10);
			else
				row.push_back(-1);

			if(i > 0 && j > 0 && i < gameDepth - 1 && j < gameWidth - 1){
				if(map.at(i-1).at(j-1) == 2)
					row.at(j) = maxReward;
				if(map.at(i-1).at(j-1) == 5)
					row.at(j) = impartialState;
			}
		}
		policy.push_back(rowAction);
		mdp.push_back(row);
	}

	map.clear();
	for(int i = 0; i < gameDepth;i++){
		vector<float> row;
		for(int j = 0; j < gameWidth;j++){
			row.push_back(mdp.at(i).at(j));
		}
		map.push_back(row);
	}

	showBestResult();

	cout << "-------------" << endl << endl;
}

void ArtificialIntelligence::setMap(Map map){
	gameDepth = map.size()+2;
	gameWidth = map.at(0).size()+2;
	this->map = map;

	searchAgentSetPositions();

	calculateMDPStates();
}

bool ArtificialIntelligence::calculateMDPStates(){
	mdp.clear();
	float left, right, top, bottom;
	cout << "Generation " << generationsRL << endl;
	for(int i = 0; i < gameDepth;i++){
		vector<float> rowStates;
		for(int j = 0; j < gameWidth;j++){
			if(i != 0 && i != gameDepth -1 && j != 0 && j != gameWidth -1){
				if(i+1 < gameDepth && map.at(i+1).at(j) != impartialState) right = map.at(i+1).at(j);
				else right = map.at(i).at(j);

				if(i-1 >= 0 && map.at(i-1).at(j) != impartialState) left =  map.at(i-1).at(j);
				else left = map.at(i).at(j);

				if(j+1 < gameWidth && map.at(i).at(j+1) != impartialState) top = map.at(i).at(j+1);
				else top = map.at(i).at(j);

				if(j-1 >= 0 && map.at(i).at(j-1) != impartialState) bottom =  map.at(i).at(j-1);
				else bottom = map.at(i).at(j);
				
				rowStates.push_back(calculateActualState(top,bottom,right,left,i,j));	
			}else{
				rowStates.push_back(minReward);
			}

			if(map.at(i).at(j) == impartialState) rowStates.at(j) = impartialState;
			if(map.at(i).at(j) == maxReward) rowStates.at(j) = maxReward;
		}
		
		mdp.push_back(rowStates);
	}

	bool reachOptimalState = reachDeepState();

	map.clear();
	
	for(int i = 0; i < gameDepth;i++){
		vector<float> row;
		for(int j = 0; j < gameWidth;j++){
				row.push_back(mdp.at(i).at(j));
		}
		map.push_back(row);
	}

	showBestResult();

	generationsRL++;
	return reachOptimalState;
}

bool ArtificialIntelligence::reachDeepState(){
	for(int i = 0; i < gameDepth;i++){
		for(int j = 0; j < gameWidth;j++){
			float diff = mdp.at(i).at(j) - map.at(i).at(j);
			if(diff > EPSILON) return false;
		}
	}

	return true;
}

float ArtificialIntelligence::calculateActualState(float top,float bottom, float right, float left, int i, int j){
	float north, east, west;
	vector<float> listQValues;
	for(int i = 0; i < 4; i++){
		switch(i){
			case 0:{
				//action Up
				west = left;
				east = right;
				north = top;
			}break;
			case 1:{
				//action Down
				west = right;
				east = left;
				north = bottom;
			}break;
			case 2:{
				//action Right
				west = top;
				east = bottom;
				north = right;
			}break;
			case 3:{
				//action Left
				west = bottom;
				east = top;
				north = left;
			}break;
		}
		listQValues.push_back(calculateQValue(north,west,east));
	}

	float maxValue= -10000;
	string action;
	if(map.at(i).at(j) != impartialState){
		for(int i = 0; i < 4; i++){
			if(maxValue < listQValues.at(i)){
				maxValue = listQValues.at(i);
				if(i == 0) action = ">";
				if(i == 1) action = "<";
				if(i == 2) action = "v";
				if(i == 3) action = "^";
			}
		}
	
		policy.at(i).at(j) = action;
	}else{
		maxValue = impartialState;
	}
	return maxValue;
}

float ArtificialIntelligence::calculateQValue(float front, float left, float right){
	float qValue = (accuracy*(discount*front+actReward) + noise*(discount*left+actReward) + noise*(discount*right + actReward));
	return qValue;
}

void ArtificialIntelligence::showBestResult(){
	//for(int j = gameDepth-1; j >= 0;j--){
	for(int j = 0; j < gameDepth;j++){
		for(int i = 0; i < gameWidth ;i++){
			printf("%.2f\t",mdp.at(j).at(i));
		}
		cout << endl;
	}

	cout << endl << "Policy:" << endl;
	//for(int j = gameDepth-1; j >= 0;j--){
	for(int j = 0; j < gameDepth;j++){
		for(int i = 0; i < gameWidth ;i++){
			cout << policy.at(j).at(i) << "\t";
		}
		cout << endl;
	}
}