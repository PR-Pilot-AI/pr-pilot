# Frequently Asked Questions

## When PR Pilot commits to the repo, does it execute commit hooks?

**No**, PR Pilot runs all commits with the `--no-verify` flag, which bypasses all commit hooks.

## Does OpenAI use my data to train their models?
**No**, as described in the [OpenAI API Terms of Service](https://help.openai.com/en/articles/5722486-how-your-data-is-used-to-improve-model-performance#h_6dea59578a), OpenAI does not use your data to train their models.