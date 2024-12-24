import os
import sys

if len(sys.argv) != 2:
    print('One argument is needed, number of processors')
    exit()


id_s = [x for x in range (int(sys.argv[1]))]

for id in id_s:
    os.system(f'start cmd /k python main.py {id} {len(id_s)}')