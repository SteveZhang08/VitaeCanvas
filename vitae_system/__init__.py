from . import cells
from . import env
from . import metabolism
from time import time

__version__ = "0.1.0"
__author__ = "SteveZhang08"
__all__ = ['cells', 'env', 'metabolism']
__date__ = "2025-7-16"
time_stamp = 1752676067

print('Welcome to use Vitae_System, thank you for your use.')
print(f'Developer: {__author__}')
print(f'Version: {__version__}')
print(f'Last build date: {__date__}')

current_time = int(time())
time_diff = current_time - time_stamp

# 检查过期警告
if time_diff > 31536000:
    print(f"Package build date {__date__} is older than one year! This package may be deprecated. Time difference: {int(time_diff / 86400)} days.")    
    if time_diff > 63072000:  # 2 years
        print("CRITICAL: Package is severely outdated! Using it may cause compatibility issues.")

print()