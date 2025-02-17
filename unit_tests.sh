#!/bin/bash

echo "Running Python unit tests for csle-agents"
cd simulation-system/libs/csle-agents; pytest; cd ../../../
echo "Running Python unit tests for csle-attacker"
cd simulation-system/libs/csle-attacker; pytest; cd ../../../
echo "Running Python unit tests for csle-collector"
cd simulation-system/libs/csle-collector; pytest; cd ../../../
echo "Running Python unit tests for csle-common"
cd simulation-system/libs/csle-common; pytest; cd ../../../
echo "Running Python unit tests for csle-defender"
cd simulation-system/libs/csle-defender; pytest; cd ../../../
echo "Running Python unit tests for csle-rest-api"
cd simulation-system/libs/csle-rest-api; pytest; cd ../../../
echo "Running Python unit tests for csle-ryu"
cd simulation-system/libs/csle-ryu; pytest; cd ../../../
echo "Running Python unit tests for csle-system-identification"
cd simulation-system/libs/csle-system-identification; pytest; cd ../../../
echo "Running Python unit tests for gym-csle-stopping-game"
cd simulation-system/libs/gym-csle-stopping-game; pytest; cd ../../../
echo "Running Python unit tests for csle-cluster"
cd simulation-system/libs/csle-cluster; pytest; cd ../../../
echo "Running Python unit tests for gym-csle-intrusion-response-game"
cd simulation-system/libs/gym-csle-intrusion-response-game; pytest; cd ../../../
echo "Running Python unit tests for csle-tolerance"
cd simulation-system/libs/csle-tolerance; pytest; cd ../../../
echo "Running Python unit tests for gym-csle-apt-game"
cd simulation-system/libs/gym-csle-apt-game; pytest; cd ../../../
echo "Running Python unit tests for gym-csle-cyborg"
cd simulation-system/libs/gym-csle-cyborg; pytest; cd ../../../
echo "Running JavaScript unit tests for csle-mgmt-webapp"
cd management-system/csle-mgmt-webapp; npm test -- --watchAll=false; cd ../../
