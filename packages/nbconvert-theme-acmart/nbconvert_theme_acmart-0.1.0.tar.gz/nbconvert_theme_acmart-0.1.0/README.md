# nbconvert-theme-acmart
This is a theme for the jupyter nbconvert extension. With minimal modification to the original latex template, the extension adds templates to convert Juoyter Notebook to ACM Journal themed LaTeX or PDF.

## Installation
```bash
pip install nbconvert-theme-acmart
```

## Dependency

- Make sure you have installed LaTeX compiler properly and with `acmart` package installed.


## Usage
After installing the package you can select theme by passing the template parameter to the jupyter nbconvert command.
```bash
jupyter nbconvert --to pdf --template sigconf notebook.ipynb
```
