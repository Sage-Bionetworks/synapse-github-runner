# synapse-github-runner
CDK-based deployment of an EC2 server to run Synapse builds and administrative jobs.  Runner can see `/synapse/admin-pat` in Secrets Manager.

To run using the CLI:

```
cdk deploy --all --context env=dev \
--context github_runner_token=AAMNJ...IGNBOK \
--context github_repo_url=...

```

where `github_runner_token` is the token to attach a runner to a repo', obtained by visiting the repo' and selecting
Settings > Actions > Runners > New Self-Hosted Runner, then scroll down to "Configure" and copy the token; and

where `github_repo_url` is the URL to the repo' which will use the runner, e.g. `https://github.com/Sage-Bionetworks/synapse-dev-ops`
