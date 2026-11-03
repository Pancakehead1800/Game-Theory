
# Payoff Matrix Analyzer

### Introduction

Anyone who's taken basic microeconomics has seen a basic 2x2x2 payoff matrix when analyzing oligopolies. They really are quite easy to deal with: look at the matrix, recall what the things mean, and in your head you can understand what the players will do. Your teacher/professor probably also showed you the **Prisoner's Dilemma**. It's such an interesting game to me; hopefully you also recognize the importance behind it. I'll try to do a project based on the **Repeated Prisoner's Dilemma** where I replicate that 1980s experiment regarding different strategies, but that's for later.

Anyways, for this project, I imagined taking a much larger payoff matrix of the size $m \times n \times 2$ (for whoever actually has a matrix that size) and actually watching how the players will move around the matrix (i.e. how they will change their strategies as the game plays out). Of course, I'm not a frontend guy and never will be, but with ChatGPT-6 Astra comes an opportunity to build whatever I want and have AI make a neat way to visualize it. Thus, I built the **Payoff Matrix Analyzer**.

To use this, simply enter in the payoff matrix you want to consider. Maybe even try out some of the default matrices (though I haven't added that many...). Press `simulate` to watch what happens. Make sure the rules selected for each player are the rules you want. In basic microeconomics classes, you won't even have to worry about having multiple strategies give the same maximum value, so most of the rules here would perform the same. You can also (hopefully--if I will add it in the future), add a fixed cost for switching strategies. 

Other than that, this project is pretty simple. If I add more than just the simulator function later, I'll try to update this README.


### Notes

1. All the frontend was completed by `ChatGPT-6 Astra`
2. All the backend was completed by me, though sometimes asking AI for help on the high-level software engineering parts (classes, conventions, etc.)
3. The project has one dependency: `numpy`. I really didn't need to use `numpy` for the project, but what if the user wants to analyze a $100,000 \times 100,000 \times 2$ matrix?


### Files

1. The `api.py` file is the actual API. Run `python3 run api.py` or `uv run api.py` or `python run api.py` or whatever your setup uses to run it.
2. The `payoff_matrix.py` file is the backend file that has the analysis functions in it.
3. The `payoff_matrix_2x2.py` file is the first version I had and (somewhat obviously) only analyzed $2 \times 2 \times 2$ matrices.
4. The `decision_rules.py` file defines the strategies available.
5. The `text.json` and `text.py` files provide a large, 20-25 something big matrix to test the backend on.
6. The `frontend/` folder is full of frontend nonsense that AI made. Don't ask me anything about it.
