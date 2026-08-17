LATEX = pdflatex
BIB   = bibtex
NAME  = ai4math_abstract

all: $(NAME).pdf

$(NAME).pdf: $(NAME).tex refs.bib
	$(LATEX) -interaction=nonstopmode $(NAME).tex
	$(BIB) $(NAME)
	$(LATEX) -interaction=nonstopmode $(NAME).tex
	$(LATEX) -interaction=nonstopmode $(NAME).tex

clean:
	rm -f $(NAME).aux $(NAME).log $(NAME).bbl $(NAME).blg $(NAME).out
