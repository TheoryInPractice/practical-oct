SRC_FILES = src/heuristics/heuristic_solver.cpp\
			src/heuristics/Debug.cpp\
			src/heuristics/Ensemble.cpp\
			src/heuristics/Graph.cpp\
			src/heuristics/Heuristics.cpp
AKIBA_IWATA_DIR = src/akiba-iwata-src
AKIBA_IWATA_VERSION = acfe2d7205e60778c96e0b5596037dd774ba1c3e
AKIBA_IWATA_PREPROCESSING_DIR = src/preprocessing/akiba-iwata
HUFFNER_DIR = src/huffner-src
HUFFNER_VERSION = 64a1cdf8a42d4a9808e117e7c35a335dcd0b6bc9
ENV_DIR = env
OUTPUT = src/heuristics/heuristic_solver
CPP_VERSION = -std=c++14
COMPILE_OPTIONS = -Wall -g -O3 -pthread

default:
	@echo "You're not in a paper dir"

real_default: clean virtualenv heuristics akiba-iwata akiba-iwata-preprocessing huffner data

clean:
	rm -f $(OUTPUT)
	rm -rf $(AKIBA_IWATA_DIR)
	rm -rf $(ENV_DIR)

data: virtualenv
	source $(ENV_DIR)/bin/activate && python -m src.data

huffner:
	test -e $(HUFFNER_DIR) || git clone https://github.com/tdgoodrich/occ_cpp.git $(HUFFNER_DIR)
	(cd $(HUFFNER_DIR) && git pull -f origin master && git checkout $(HUFFNER_VERSION))
	(cd $(HUFFNER_DIR) && make clean && make)

heuristics:
	clang++ $(CPP_VERSION) $(SRC_FILES) -o $(OUTPUT) $(COMPILE_OPTIONS)

akiba-iwata:
	test -e $(AKIBA_IWATA_DIR) || git clone https://github.com/wata-orz/vertex_cover.git $(AKIBA_IWATA_DIR)
	(cd $(AKIBA_IWATA_DIR) && git pull -f origin master && git checkout $(AKIBA_IWATA_VERSION))
	chmod +x $(AKIBA_IWATA_DIR)/build.sh
	rm -rf $(AKIBA_IWATA_DIR)/bin
	(cd $(AKIBA_IWATA_DIR) && exec ./build.sh)

akiba-iwata-preprocessing:
	rm -rf $(AKIBA_IWATA_PREPROCESSING_DIR)/bin
	(cd $(AKIBA_IWATA_PREPROCESSING_DIR) && exec ./build.sh)

virtualenv:
	/bin/test -d $(ENV_DIR) || (virtualenv $(ENV_DIR) --python=python3.5)
	./$(ENV_DIR)/bin/pip install -r requirements.txt
