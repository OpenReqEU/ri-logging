"""
created at: 2019-11-26
author:     Volodymyr Biryuk

<module comment>
"""
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET
from microservice import util

if __name__ == '__main__':
    # Execute tests
    os.system('python -m pytest --cov=microservice --cov-report=xml --cov-config=.coveragerc tests/test_all.py')
    # Modify source path in xml to relative path
    filepath = os.path.join(os.path.dirname(__file__), 'coverage-reports', 'coverage.xml')
    tree = ET.parse(filepath)
    root = tree.getroot()
    wrong_path = root[0][0].text
    split = wrong_path.split('/')
    correct_path = split[-1]
    root[0][0].text = correct_path
    tree.write(filepath)

