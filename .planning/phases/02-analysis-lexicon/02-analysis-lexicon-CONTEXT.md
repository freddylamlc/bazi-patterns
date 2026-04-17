# Analysis Lexicon Expansion Context

## Phase Goal
Systematically integrate "Shi Shen (Ten Gods) combination predictions" and "60 Jiazi (Yi Zhu) features" from literature into the project.

## Core Tasks
1. **Ten Gods Event Predictions**: 
   - Update `bazi/analysis/duanyu_db.py` with specific combination predictions extracted from Chapter 09 (e.g., "Mixed Guan/Sha without Shi/Shang", "Strong Yin with Weak Cai", etc.).
2. **60 Jiazi Feature Refinement**:
   - Update `bazi/analysis/yizhu.py` with specific imagery and descriptions for each of the 60 Jiazi pairs from Chapter 11.
3. **Great Luck and Flowing Year Interaction**:
   - Introduce "Sui Yun triggered" prediction recognition in `bazi/analysis/integrated.py` or related modules.

## Decisions
- D-01: Focus on text-based prediction database expansion first.
- D-02: Use structured mapping for predictions to allow programmatic lookup in the integrated analysis phase.
- D-03: Ensure 60 Jiazi descriptions maintain traditional Chinese terminology.

## Deferred Ideas
- Dynamic generation of new predictions via LLM (to be considered in a later phase).
- Visual mapping of imagery (deferred to UI phase).
