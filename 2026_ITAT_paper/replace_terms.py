import re

file_path = "itat_pipeline.tex"
with open(file_path, "r") as f:
    content = f.read()

replacements = [
    (r'on-demand structure-targeted pools', 'on-demand structure-targeted datasets'),
    (r'parametric/atlas tier', 'parametric/atlas dataset'),
    (r'random-models tier', 'random-models dataset'),
    (r'static hold-out', 'static validation set'),
    (r'adversarial pool', 'adversarial dataset'),
    (r'tiered exact pools', 'stratified exact datasets'),
    (r'two further tiers', 'two further datasets'),
    (r'pool of boolean predicates', 'set of boolean predicates'),
    (r'a tier lacking', 'a dataset lacking'),
    (r'fixed pool', 'fixed dataset'),
    (r'parallel pool', 'parallel process pool'), # keep this as pool or worker group
    (r'family pool', 'family dataset'),
    (r'random models tier', 'random models dataset'),
    (r'House of Graphs tier', 'House of Graphs dataset'),
    (r'parametrised pools', 'parametrised datasets'),
    (r'pool-dominated', 'dataset-dominated'),
    (r'pool figure', 'dataset figure'),
    (r'census tier', 'census dataset'),
    (r'refutation pool', 'refutation dataset'),
    (r'this tier', 'this collection')
]

for old, new in replacements:
    content = re.sub(old, new, content)

with open(file_path, "w") as f:
    f.write(content)

print("Done")
