# import os
# import sys
# # Find the decision path of the current file, __file__ means the current file, which is test.py
# file_path = os.path.abspath(__file__)
# print(file_path)
# # Get the directory where the current file is located
# cur_path = os.path.dirname(file_path)
# print(cur_path)
# # Get the path of the project
# project_path = os.path.dirname(cur_path)
# print(project_path)
# # Add the project path to the python search path
# sys.path.append(project_path)

from subFiles.model import db

db.create_all()
