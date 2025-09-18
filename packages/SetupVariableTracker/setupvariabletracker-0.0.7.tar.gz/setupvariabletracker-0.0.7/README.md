# SetupVariableTracker
Very simple library to track and log the declaration of new (setup) variables.

## Usage example

``` python
from SetupVariableTracker import SetupVariableTracker
vtrack = SetupVariableTracker(locals())

# Define parameters for this script
setup_variable_1 = "Hello"
setup_variable_2 = "World!"
foo = 1
bar = None

# Create a summary of all newly defined variables
summary_content = vtrack.save(locals(), sort=True)
print(summary_content)
```


This will print an overview of the declared variables (`setup_variable_1`, `setup_variable_2`, `foo`, and `bar`) as well
as save them in a timestamped `.log` file.

I know there are more elegant ways to achieve this, but I found this an elegant way to add this functionality to legacy
code with very little effort. Hope it'll be useful to others.

## Installation
`pip install SetupVariableTracker`
