import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import interest_sct as ci
print(ci.cd_interest(1000, 5, 2)) 
print(ci.si_interest(1000, 5, 2))
print(ci.total_amount(1000, 5, 2))