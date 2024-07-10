<h1 align="center"><img src="https://github.com/mechanikate/WikiDiff/blob/main/README-assets/img/wikidiff-logo.png?raw=true" height="100" /></h1>

WikiDiff checks controversial-ness and differences between revisions of Wikipedia articles with a simple(ish) web interface.
## Installation
```bash
pip install flask requests # requirements
git clone https://github.com/mechanikate/WikiDiff.git # download repo
cd WikiDiff
python main.py
```
## Usage
Paste Wikipedia URL into the URL box, then click "Calculate heatmap".

"Minimum prevalence" sets the minimum number of revisions needed for the text to appear on the textarea.

"Number of revisions to compare?" gets the number of revisions starting before right now to compare to each other.
> [!WARNING]  
> The text display is NOT in order of appearance,  but rather alphabetical order, due to technical restrictions.