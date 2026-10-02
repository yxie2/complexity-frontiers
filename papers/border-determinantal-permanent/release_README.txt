Smooth slices and superquadratic border determinantal complexity of the permanent
Ying Xie
Kennesaw State University
yxie2@kennesaw.edu

CONTENTS
paper/superquadratic_border_determinantal.pdf: 20-page manuscript.
paper/main.tex and four input files: complete LaTeX source.
verification/: eight exact verification suites, results, and hash manifest.
submission_metadata.json: title, author details, abstract, and suggested categories.
MANIFEST.json: SHA-256 hashes of every other release file.

BUILD THE PAPER
From paper/, run either:
    pdflatex main.tex
    pdflatex main.tex
or:
    tectonic main.tex
The supplied PDF was built with Tectonic. All references are embedded in
main.tex; no BibTeX run, images, external research notes, or custom style
files are required. The source uses standard LaTeX packages.
The supplied PDF retains only its title, author, and subject metadata.

VERIFY THE CODE
From verification/:
    python -m pip install -r requirements.txt
    python -X utf8 run_verification.py
See verification/README.txt for the checks and their scope.

ARXIV SOURCE ARCHIVE
The separately supplied superquadratic_border_determinantal_arxiv.zip
contains only the five required .tex files, with main.tex at its root.
Upload that archive as the source; consult submission_metadata.json for
the submission fields. It does not include the verification code or
the precompiled PDF. Category and license are selected in the submission
form. No external submission is performed by these files.

SCOPE
The main bound is Omega(n^2 log n) for border determinantal complexity
of the permanent over the complex numbers, with explicit bounds from
n=64 and n=512. The large-characteristic statements assume p>n.
Circuit appendices retain their budgets on non-skew products and
nonscalar divisions. The paper makes no VP-versus-VNP separation claim.
