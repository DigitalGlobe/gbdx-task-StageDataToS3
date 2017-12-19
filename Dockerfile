FROM tdgp/stagetos3:v1.0
COPY docker_utilities/algorithms/common.py /
COPY docker_utilities/algorithms/stagetos3.py /
CMD ["python", "/stagetos3.py"]
