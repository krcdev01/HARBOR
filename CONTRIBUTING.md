# Contributing to HARBOR

Contributions are submitted through pull requests for review by the project
maintainer.

## Contribution Process

1. Fork the HARBOR repository on GitHub.

2. Clone your fork.

   ```bash
   git clone git@github.com:YOUR-USERNAME/HARBOR.git
   cd HARBOR
   ```

3. Create a branch for the change.

   ```bash
   git switch -c descriptive-branch-name
   ```

4. Make the change in your branch.

   Keep the implementation focused on one issue or related set of changes.
   Update the applicable architecture, deployment, and operations documentation
   when behavior, paths, configuration, or operating procedures change.

5. Validate the change.

   Run the checks appropriate to the files changed. For Compose changes,
   validate the affected environment configuration. For Polly changes, run its
   unit tests. Include relevant staging results in the pull request when the
   change affects deployment or runtime behavior.

6. Review the changes for credentials and private system information.

   Do not commit deployed `.env` files, passwords, API keys, Cloudflare tokens,
   VPN credentials, hardware identifiers, or other private deployment values.
   Templates must contain placeholders and safe defaults.

7. Commit the change.

   ```bash
   git status
   git diff
   git add --patch
   git diff --cached
   git commit -m "Describe the change"
   ```

8. Push the branch to your fork.

   ```bash
   git push -u origin descriptive-branch-name
   ```

9. Open a pull request against the HARBOR repository's `main` branch.

   The pull request should explain:

   - what changed;
   - why the change is needed;
   - how it was validated; and
   - any deployment or compatibility considerations.

## Review

The project maintainer will review the pull request and decide whether to merge
it, request changes, or close it. A submitted pull request is a proposal and is
not accepted until it has been reviewed and merged.
