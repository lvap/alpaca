# ALPACA
Content-focused webpage credibility evaluation

## Installation

> \>pip install -r requirements.txt

Then in a Python shell:

> \>\>\>import language_tool_python  
> \>\>\>language_tool_python.LanguageTool('en-US')  
> \>\>\>import nltk  
> \>\>\>nltk.download('punkt')

If you want to run the code on branch 
[signal-implementation-analysis](https://github.com/lvap/alpaca/tree/signal-implementation-analysis), 
you will need fastText:

> \>pip install fasttext==0.9.2

which might require you to to install Microsoft Visual C++ via the 
[Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

## Usage

Run main.py in a terminal to start the program, then enter any http(s) webpage URL to evaluate its credibility.
Returned credibility score is between 0 -> low credibility and 1 -> high credibility.

Logging, and export of credibility signal statistics to a .csv file can be configured in main.py. 
To evaluate all URLs in a list, use evaluate_datasets() in the same file.

## System analysis

The performance analysis data and results for the system and the signal sub-scores are in the 
[analysis folder](https://github.com/lvap/alpaca/tree/main/analysis).

The code for and analysis of signal measurements and different signal implementations are on the branch 
[signal-implementation-analysis](https://github.com/lvap/alpaca/tree/signal-implementation-analysis).

