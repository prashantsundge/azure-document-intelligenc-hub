
```md
# Contributing

Thank you for contributing to Azure Document Intelligence Hub.

## Before opening a pull request

1. Use only synthetic or openly licensed documents.
2. Never commit `.env`, API keys, connection strings, or personal data.
3. Run backend checks:

   ```powershell
   cd backend
   ruff check app tests
   pytest
   ```

4. Run frontend checks:

   ```powershell
   cd frontend
   npm run build
   ```

5. Update documentation when architecture, deployment, or user behavior changes.

## Pull request expectations

- Keep changes focused.
- Explain the business or learning objective.
- Include test evidence.
- Mention Azure cost or security impact.
- Do not merge if GitHub Actions fails.
```

`.github/CODEOWNERS`

```text
# Replace this placeholder with your GitHub username or team.
* @prashantsundge
```

`.github/pull_request_template.md`

```md
## Summary

Describe the change.

## Azure AI / engineering area

- [ ] Document Intelligence
- [ ] Azure AI Language
- [ ] Azure AI Search or RAG
- [ ] Azure OpenAI
- [ ] Content Safety
- [ ] Storage, security, monitoring, Docker, or CI/CD
- [ ] Documentation only

## Validation

- [ ] `ruff check app tests`
- [ ] `pytest`
- [ ] Frontend build
- [ ] Docker build or Compose smoke test
- [ ] Manual Azure verification, if applicable

## Security and cost impact

- [ ] No secrets or personal/company data were added.
- [ ] Azure resource or cost impact was reviewed.
- [ ] Documentation was updated where needed.
```

`.github/ISSUE_TEMPLATE/bug_report.md`

```md
---
name: Bug report
about: Report incorrect behavior
title: "[Bug] "
labels: bug
---

## What happened?

## Expected behavior

## Steps to reproduce

1.
2.
3.

## Environment

- Local Docker / Azure deployment:
- Browser or API client:
- Relevant endpoint:

## Logs or screenshots

Remove secrets, keys, and personal data before posting.
```

`.github/ISSUE_TEMPLATE/feature_request.md`

```md
---
name: Feature request
about: Propose an improvement
title: "[Feature] "
labels: enhancement
---

## Problem

What learning or user problem does this solve?

## Proposed solution

## Azure AI services involved

## Security, privacy, and cost impact

## Acceptance criteria
```

After creating these, reply `done`.