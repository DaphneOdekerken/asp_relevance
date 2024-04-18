ASP-based algorithms for stability and relevance in IAFs
========================================================
Author: Daphne Odekerken

This package contains algorithms for stability and relevance in Incomplete 
Argumentation Frameworks under grounded and complete semantics.
- For listing relevant updates under grounded semantics, see 
  grounded_relevance.py.
- For listing complete-credulous-IN/OUT/UNDEC updates, see 
  complete_credulous_relevance.py.
- For checking stability under grounded semantics, see grounded_stability.py.

Installation
------------
First, make sure that [Clingo](https://github.com/potassco/clingo) is 
installed on your machine.
Then run
```
git clone git@github.com:DaphneOdekerken/asp_relevance.git
pip install -r requirements.txt
```