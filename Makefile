platform=$(shell uname -s)
conda_path=$(shell which conda)

.PHONY: show check-env venv install_snap check venv_install_snap

ifeq ($(platform),Darwin)

ifneq ($(findstring conda,${conda_path}),conda)
	$(error Conda not present)
else
	@echo Conda present at ${conda_path}
endif

ifeq ($(BLOG_ANALYSIS_VENV),)
BLOG_ANALYSIS_VENV=blog_analysis_venv
endif
ifeq ($(CONDA_ENV_PATH),)
CONDA_ENV_PATH=//anaconda
endif

VENVDIR := ${CONDA_ENV_PATH}/envs/${BLOG_ANALYSIS_VENV}

SNAPDIR := ./snap-1.2.1-2.4-macosx10.7.5-x64-py2.7

$(SNAPDIR):
	curl "http://snap.stanford.edu/snappy/release/snap-1.2.1-2.4-macosx10.7.5-x64-py2.7.tar.gz" -o ./snap-1.2.1-2.4-macosx10.7.5-x64-py2.7.tar.gz
	tar zxvf ./snap-1.2.1-2.4-macosx10.7.5-x64-py2.7.tar.gz
	cp ./snap_setup.py ./snap-1.2.1-2.4-macosx10.7.5-x64-py2.7/setup.py

$(VENVDIR):
	conda create -y -n ${BLOG_ANALYSIS_VENV} numpy scipy scikit-learn networkx matplotlib pandas ipython notebook

deps: $(SNAPDIR) $(VENVDIR)
	source activate ${BLOG_ANALYSIS_VENV}; \
	cd $(SNAPDIR); \
	export BLOG_ANALYSIS_VENV=${BLOG_ANALYSIS_VENV};\
	python setup.py install

check: 
	source activate ${BLOG_ANALYSIS_VENV};\
	python ./test_analysis.py

notebook:
	source activate ${BLOG_ANALYSIS_VENV};\
	ipython notebook

else ifeq ($(platform),Linux)

SNAPDIR := ./snap-1.2.1-2.4-centos6.5-x64-py2.6/

$(SNAPDIR):
	curl "http://snap.stanford.edu/snappy/release/snap-1.2.1-2.4-centos6.5-x64-py2.6.tar.gz" -o ./snap-1.2.1-2.4-centos6.5-x64-py2.6.tar.gz
	tar zxvf ./snap-1.2.1-2.4-centos6.5-x64-py2.6.tar.gz

VENVDIR := ./venv

$(VENVDIR):
	virtualenv venv

deps: $(SNAPDIR) $(VENVDIR)
	sudo apt-get install -y gfortran libopenblas-dev liblapack-dev \
	build-dep python-matplotlib; \
	source ./venv/bin/activate; \
	pip install -U numpy scipy scikit-learn networkx matplotlib pandas notebook; \
	cd $(SNAPDIR); \
	python setup.py install

check: 
	source ./venv/bin/activate; \
	python ./test_analysis.py

notebook:
	source ./venv/bin/activate; \
	ipython notebook

else
	$(error, Unknown platform)

endif


