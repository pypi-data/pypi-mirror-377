import time

def start_c():
    return time.time()

def end_c(start):
    print('\n----------------------------------------------------\n',
          "Process execution time - ", round(time.time() - start, 5))