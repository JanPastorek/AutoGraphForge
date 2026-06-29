import re

def main():
    with open('itat_pipeline.tex', 'r') as f:
        content = f.read()

    # We will split the document into blocks using regex to find section/subsection markers.
    # But since we are doing manual merging, let's just find the indices of the headings.
    
    # Helper to find text
    def extract_between(start_str, end_str, include_start=True):
        start_idx = content.find(start_str)
        if start_idx == -1: raise ValueError(f"Could not find {start_str}")
        if end_str:
            end_idx = content.find(end_str, start_idx + len(start_str))
            if end_idx == -1: raise ValueError(f"Could not find {end_str}")
        else:
            end_idx = len(content)
        
        extracted = content[start_idx:end_idx]
        if not include_start:
            extracted = extracted[len(start_str):]
        return extracted

    # Extract preamble + Intro + Preliminaries
    header_to_framework = content[:content.find(r'\section{Theoretical Framework and Related Work}')]
    
    # Extract sections
    sec3_1 = extract_between(r'\subsection{Conjecturing as theory selection}', r'\subsection{Filtering and sorting heuristics}')
    sec3_2 = extract_between(r'\subsection{Filtering and sorting heuristics}', r'\subsection{Counterexamples as iterative counterexample search}')
    sec3_3 = extract_between(r'\subsection{Counterexamples as iterative counterexample search}', r'\subsection{Filtering redundant theorems via linear programming}')
    sec3_4 = extract_between(r'\subsection{Filtering redundant theorems via linear programming}', r'\section{The AutoGraphForge Pipeline}')
    
    sec4_1 = extract_between(r'\subsection{System overview}', r'\subsection{Invariants and the database}')
    sec4_2 = extract_between(r'\subsection{Invariants and the database}', r'\subsection{Conjecture generation engine}')
    
    sec4_3_intro = extract_between(r'\subsection{Conjecture generation engine}', r'\subsubsection{Architecture and linear generation}')
    sec4_3_1 = extract_between(r'\subsubsection{Architecture and linear generation}', r'\subsubsection{Product and ratio conjectures}')
    sec4_3_2 = extract_between(r'\subsubsection{Product and ratio conjectures}', r'\subsubsection{Sophie layer: sufficient conditions}')
    sec4_3_3 = extract_between(r'\subsubsection{Sophie layer: sufficient conditions}', r'\subsection{Refutation and the integrated discovery pipeline}')
    
    sec4_4_intro = extract_between(r'\subsection{Refutation and the integrated discovery pipeline}', r'\subsubsection{Adversarial verification}')
    sec4_4_1 = extract_between(r'\subsubsection{Adversarial verification}', r'\subsubsection{Counterexample-search backends}')
    sec4_4_2 = extract_between(r'\subsubsection{Counterexample-search backends}', r'\subsubsection{Dynamic database}')
    sec4_4_3 = extract_between(r'\subsubsection{Dynamic database}', r'\subsection{Formalization and proving}')
    
    sec4_5 = extract_between(r'\subsection{Formalization and proving}', r'\section{Discovery in graph theory}')
    
    rest_of_doc = content[content.find(r'\section{Discovery in graph theory}'):]

    # --- APPLY FIXES AND REDUNDANCY TRIMMING ---
    
    # Fix Intro redundancies:
    # 1. Second paragraph enumeration:
    intro_p2_old = r"Computer-assistance in this area can be roughly classified into four areas based on the research stage it assists: (i) \emph{conjecturing}, which generates new statements that are hypothesised to be true based on a finite database (of graphs); (ii) \emph{refuting}, which searches for counterexamples to conjectures; (iii) \emph{formalizing}, which translates conjectures into a formal language; and (iv) \emph{proving} stage which attempts to prove the conjectures in a formal system."
    intro_p2_new = r"Computer-assistance in this area can be roughly classified into four corresponding areas based on the research stage it assists: \emph{conjecturing} new statements based on a finite database, \emph{refuting} them by searching for counterexamples, \emph{formalizing} them into a rigorous language, and ultimately \emph{proving} them in a formal system."
    header_to_framework = header_to_framework.replace(intro_p2_old, intro_p2_new)

    # 2. Flow fix between failure modes and computational search methods:
    intro_p5_old = r"Computational methods used for searching for (counter)examples of graphs have been recently summarised"
    intro_p5_new = r"To address the first and fourth failure modes---false bounds and overfitting---a robust refutation engine is required. Computational methods used for searching for (counter)examples of graphs have been recently summarised"
    header_to_framework = header_to_framework.replace(intro_p5_old, intro_p5_new)
    
    # Fix 4.3.1 Seed sizes redundant with 5.1
    # Remove: "(to $2{,}860$ at the start of the HPC run, growing further each round)"
    # Remove: "from an earlier one-pass run"
    # Actually let's just surgically replace the text.
    sec4_3_1 = sec4_3_1.replace(
        r"Generation begins from the TxGraffiti\n\emph{expressive graphs} (a curated default dataset; $329$ graphs) and grows only by\nhard witnesses (to $2{,}860$ at the start of the HPC run, growing further each round).",
        r"Generation begins from the TxGraffiti \emph{expressive graphs} (a curated default dataset) and grows only by hard witnesses."
    )
    
    # Fix 4.4.3 Dynamic database: Make it part of 4.4.1 (Adversarial verification)
    sec4_4_3_clean = sec4_4_3.replace(r'\subsubsection{Dynamic database}', '').replace(r'\label{sec:redburton}', '').strip()
    # Also in 4.4.3 there's reference to \S\ref{sec:rolling-audit}, which is 3.3.
    # We will merge 3.3 into the start of the Refutation section.

    # Build New Section 3: The AutoGraphForge Architecture
    new_sec3 = r"\section{The AutoGraphForge Architecture}" + "\n\n"
    
    # 3.1 System Overview
    new_sec3 += sec4_1 # \subsection{System overview}
    
    # 3.2 Initial Datasets
    new_sec3 += sec4_2 # \subsection{Invariants and the database}
    
    # 3.3 Conjecture Generation as Theory Selection
    new_sec3 += r"\subsection{Conjecture generation as theory selection}" + "\n"
    new_sec3 += r"\label{sec:theory-selection}" + "\n"
    # Content of 3.1
    new_sec3 += sec3_1.replace(r'\subsection{Conjecturing as theory selection}', '').replace(r'\label{sec:theory-selection}', '').strip() + "\n\n"
    # Content of 4.3 intro & 4.3.1 & 4.3.2
    new_sec3 += sec4_3_intro.replace(r'\subsection{Conjecture generation engine}', '').replace(r'\label{sec:system}', '').strip() + "\n\n"
    new_sec3 += sec4_3_1 + sec4_3_2
    
    # 3.4 Novelty Filtering and Dominance Heuristics
    new_sec3 += r"\subsection{Novelty filtering and dominance heuristics}" + "\n"
    new_sec3 += r"\label{sec:heuristics_related}" + "\n"
    new_sec3 += sec3_2.replace(r'\subsection{Filtering and sorting heuristics}', '').replace(r'\label{sec:heuristics_related}', '').strip() + "\n\n"
    new_sec3 += sec3_4.replace(r'\subsection{Filtering redundant theorems via linear programming}', '').replace(r'\label{sec:novelty}', '').strip() + "\n\n"
    # Also add 4.3.3 (Sophie layer) here since it uses the heuristics heavily
    new_sec3 += sec4_3_3
    
    # 3.5 Iterative Refutation and Adversarial Search
    new_sec3 += r"\subsection{Iterative refutation and adversarial search}" + "\n"
    new_sec3 += r"\label{sec:refute}" + "\n"
    # Merge 3.3 theory
    new_sec3 += sec3_3.replace(r'\subsection{Counterexamples as iterative counterexample search}', '').replace(r'\label{sec:rolling-audit}', '').strip() + "\n\n"
    # Add 4.4 intro
    new_sec3 += sec4_4_intro.replace(r'\subsection{Refutation and the integrated discovery pipeline}', '').replace(r'\label{sec:refute}', '').strip() + "\n\n"
    # Add 4.4.1 (Adversarial Verification)
    sec4_4_1_mod = sec4_4_1 + "\n\n" + r"\paragraph{Dynamic database.}" + " " + sec4_4_3_clean + "\n\n"
    new_sec3 += sec4_4_1_mod
    # Add 4.4.2 (Backends)
    new_sec3 += sec4_4_2
    
    # 3.6 Formalization and Neural Proving
    new_sec3 += sec4_5 # \subsection{Formalization and proving}

    # Final assembly
    final_content = header_to_framework + new_sec3 + rest_of_doc

    # Write out
    with open('itat_pipeline_reorganized.tex', 'w') as f:
        f.write(final_content)
        
    print("Successfully reorganized document into itat_pipeline_reorganized.tex")

if __name__ == '__main__':
    main()
