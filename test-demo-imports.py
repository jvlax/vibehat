# Test file for demonstrating publishing of non-test packages
# These imports don't exist and aren't in our test manifest

import super_awesome_helper  # Should be publishable 
from magical_utils import process_data  # Should be publishable
import demo_package_for_testing  # Should be publishable

print("This is just a demo file for testing dependency scanning and publishing") 