FROM luboobratil/rtt-pyscript-base:latest

LABEL maintainer.name="Lubo Obratil"
LABEL maintainer.email="lubomir.obratil@gmail.com"
LABEL image.source="https://github.com/LuboO/rtt-cache-cleaner-docker"
LABEL project="https://github.com/crocs-muni/randomness-testing-toolkit"

COPY cache_cleaner.py /

VOLUME ["/rtt_experiment_files"]

CMD ["python3", "/cache_cleaner.py"] 

