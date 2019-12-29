import os
import errno

print(os.path.dirname('output'))
dir_path = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()
print(dir_path)
print(cwd)
print(__file__)
# if not os.path.exists(os.path.dirname('output')):
#     try:
#         print(os.path.dirname('output'))
#         # print(os.path.dirname('output'))
#         os.makedirs(os.path.dirname('output'))
#     except OSError as exc:  # Guard against race condition
#         if exc.errno != errno.EEXIST:
#             raise

dir_path = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(os.path.join(dir_path, 'output1')):
    try:
        os.makedirs(os.path.join(dir_path, 'output1'))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
