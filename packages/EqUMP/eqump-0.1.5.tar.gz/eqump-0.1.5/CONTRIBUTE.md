# CONTRIBUTE
## Welcome
Thank you for your interest in contribution to EqUMP!
Before getting started, please review the guidelines below.

## Finding or Proposing an Issue
When you plan to contribute, it’s important to coordinate with the team:
1. Check the [issue tracker](https://github.com/huni1023/EqUMP/issues) to see if your idea or bug has already been reported.
2. If it exists:
    - Add a comment to provide details or indicate that you are working on it.
3. If it does not exist:
    - Open a new issue. We provide multiple issue templates--please fill them out carefully.

## Submitting a PR
Once you feature or fix is implemted and passes tests, open a Pull Request against the `dev` branch of [EqUMP](https://github.com/huni1023/EqUMP)
### Quick Start
```bash
git clone https://github.com/huni1023/EqUMP.git
cd EqUMP
uv sync
git checkout dev
git checkout -b {nema_of_your_branch}

#
# develop your code
# run all tests locally
#

git add .
git commit -m "{write commit message}"
git push --set-upstream origina {name of your branch}
```
Then:
- Open a PR on github (`dev` ← `{{ your branch }}`
    - check [branch naming convention](CONTRIBUTE.md#Branch-Naming-Convention)
- Assign a reviewer from the team
- Complete the provided PR template thoroughly
- After review, your PR may be merged

### Notes for Regular Contributors
- Always bracn from `dev` (not `main`).
- The `main` branch is linkied to TestPyPI; please avoid direct commits there.
- Example workflow for new work:
```bash
git checkout dev
git pull
git checkout -b {new_branch}
# write your code
# git add /commit / push combo + PR
```

## Branch Naming Convention
When creating a new branch, please use one of the following prefixes to indicate the purpose of your work:
- `feat/` – for new features or enhancements
    - Example: feat/mmle-em-estimation
- `bug/` – for bug fixes
    - Example: bug/fix-tcc-scaling-error
- `test/` – for testing, experiments, or CI-related work
    - Example: test/bootstrap-vs-delta
- general rules
    - Use lowercase with hypens to separate words
    - Keep names concise but descriptive
    - Avoid generic names like `update`, `temp`, or `work`
