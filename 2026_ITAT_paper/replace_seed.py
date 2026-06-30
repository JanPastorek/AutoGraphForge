import re

file_path = "itat_pipeline.tex"
with open(file_path, "r") as f:
    content = f.read()

replacements = [
    (r'a small seed', r'a small core database'),
    (r'small evolving seed', r'small evolving core database'),
    (r'the seed\'s', r'the core database\'s'),
    (r'counterexample-hardened seed', r'counterexample-hardened core database'),
    (r'small initial seed', r'small initial core database'),
    (r'structured seed family', r'structured base family'),
    (r'structured seed library', r'structured base library'),
    (r'each seed is driven', r'each base graph is driven'),
    (r'common seed of', r'common core database of'),
    (r'The \\emph\{seed\} is', r'The \\emph{core database} is'),
    (r'into the seed in each', r'into the core database in each'),
    (r'final seed size', r'final core database size'),
    (r'28\\%\} seed expansion', r'28\\%\} core database expansion'),
    (r'the seed and hence', r'the core database and hence')
]

for old, new in replacements:
    content = re.sub(old, new, content)

with open(file_path, "w") as f:
    f.write(content)

print("Done replacing 'seed' with 'core database'.")
