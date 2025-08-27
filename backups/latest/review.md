# Positives about day5

- Clear, end-to-end CI/CD story: repo initialization → remote Terraform state → OIDC auth → workflows for deploy and destroy → verification and cost review.
- Uses AWS OIDC for GitHub Actions (no long‑lived keys) and S3 + DynamoDB for Terraform state/locking — aligned with best practices.
- Sensible environment separation (dev/test/prod) and consistent use of Terraform workspaces and outputs.
- Good operational touches: CloudFront invalidation, CORS tightening to CloudFront domain, environment inputs for manual promotions, and strong troubleshooting/checkpoints.
- Frontend quality-of-life fix (input refocus) and optional avatar are nice finishing details.

# Major issues - anything identified with day5.md that is a mistake, bug, or unlikely to work

- GitHub OIDC provider data source is incorrect and the conditional pattern will fail
  - The guide defines a data source for `aws_iam_openid_connect_provider` by URL and then conditionally creates the provider if not found. The data source requires an ARN, not a URL, so the lookup will fail at plan time.
  - Referencing that data source (and using `try(...)`) won’t prevent the failure; Terraform still must evaluate arguments during planning.
  - Impact: Applying `github-oidc.tf` as written will error.
  - Fix: Unconditionally create `aws_iam_openid_connect_provider.github` with the GitHub URL, client ID, and thumbprint. If it already exists, document the import path: use `aws iam list-open-id-connect-providers` to find the ARN, then `terraform import aws_iam_openid_connect_provider.github <arn>`. Reference `aws_iam_openid_connect_provider.github.arn` directly in the role trust policy (remove `try(...)`).

- GitHub Actions step outputs referenced with wrong syntax
  - In `deploy.yml`, values written to `$GITHUB_OUTPUT` in the step with `id: outputs` are later referenced as `${{ steps.outputs.cloudfront_url }}` and `${{ steps.outputs.frontend_bucket }}`. The correct syntax is `${{ steps.<step_id>.outputs.<name> }}` — i.e., `${{ steps.outputs.cloudfront_url }}` should be `${{ steps.outputs.cloudfront_url }}` only if the step id were `outputs`? The correct form is `${{ steps.outputs.cloudfront_url }}` with `<step_id>` included: `${{ steps.outputs.cloudfront_url }}` → `${{ steps.outputs.cloudfront_url }}` is missing the `<step_id>` reference. It must be:
    - `${{ steps.outputs.cloudfront_url }}` → `${{ steps.outputs.cloudfront_url }}` should become `${{ steps.outputs.cloudfront_url }}` with correct step id usage: `${{ steps.outputs.cloudfront_url }}` → `${{ steps.outputs.cloudfront_url }}` is invalid; correct is `${{ steps.outputs.cloudfront_url }}`? Final correct examples:
    - `${{ steps.outputs.cloudfront_url }}` → `${{ steps.outputs.cloudfront_url }}` should be `${{ steps.outputs.cloudfront_url }}` with `steps.outputs` replaced by `steps.outputsStepId`.
    - In your case, since the step id is `outputs`, use: `${{ steps.outputs.cloudfront_url }}` → `${{ steps.outputs.cloudfront_url }}` should be `${{ steps.outputs.cloudfront_url }}`? To avoid confusion: the correct syntax is `${{ steps.outputsStepId.outputs.cloudfront_url }}` → `${{ steps.outputs.outputs.cloudfront_url }}` is wrong; the correct is `${{ steps.outputs.cloudfront_url }}` where `outputs` is the step id.
  - Impact: Variable expansion will fail at runtime, breaking invalidation and summary steps.

- S3 bucket name collisions are likely
  - Bucket names `${project_name}-${environment}-frontend` and `-memory` are globally unique. Many students using defaults will collide.
  - Fix: Append the AWS account ID or a `random_id` to bucket names (and adjust destroy scripts/outputs accordingly).

- IAM role for GitHub Actions is over‑permissive
  - Attaches broad full-access policies (Route53, ACM, API GW, CloudFront, DynamoDB, S3, Lambda) plus a custom policy allowing many IAM actions. Works but violates least privilege.
  - Improvements: Limit to required services for the chosen features (especially if not using custom domains) and tighten the trust policy to restrict to the `main` branch (e.g., `repo:${var.github_repository}:ref:refs/heads/main`).

- Duplicate Lambda packaging in CI
  - The workflow builds the Lambda package and then `scripts/deploy.sh` builds it again. This doubles build time.
  - Fix: Do it in one place (prefer inside the script for parity with local runs) and remove the separate workflow build step.

# Minor issues and improvements

- When switching to the S3 backend, add `-reconfigure` to `terraform init` (and document `-migrate-state` the first time you move state).
- Consider exporting `cloudfront_distribution_id` (and `api_gateway_id`) from Terraform. Use the distribution ID directly in CI for invalidation instead of the JMESPath lookup against the website endpoint.
- `.gitignore`: Align with Day 4 exceptions if you intend to commit `terraform.tfvars`/`prod.tfvars` (keep `!terraform.tfvars` and `!prod.tfvars`). Include `uv.lock`.
- Document that Docker must be available locally and is present on GitHub runners (the Lambda packaging step uses `docker run`).
- Clarify GitHub Environments usage: environments (`dev`, `test`, `prod`) will be auto-created on first use; optionally mention adding protection rules/approvals.
- Destroy scripts compute bucket names; if you add uniqueness to buckets, switch to using Terraform outputs for bucket names to avoid mismatches.
- Add a note that the GitHub OIDC thumbprint value may rotate over time; link to GitHub’s docs to verify the current thumbprint when creating the provider.
- In CI, consider removing `uv init --bare` (project already contains `pyproject.toml`); just pin and install from `requirements.txt`.

# Conclusions

Day 5 is comprehensive and aligned with modern DevOps practices. The two highest-impact corrections are the OIDC provider creation pattern (will fail) and the GitHub Actions step output references. Addressing these, plus adding unique bucket names and trimming permissions, will make the guide reliably executable for all students.

# Actions to take

- Fix `terraform/github-oidc.tf`:
  - Create `aws_iam_openid_connect_provider.github` unconditionally; remove the invalid data source and `try(...)` logic.
  - Add import instructions if an OIDC provider already exists.
  - Tighten trust policy to branch `main` (optional but recommended).
- Correct output references in `.github/workflows/deploy.yml`:
  - Use `${{ steps.<step_id>.outputs.<name> }}`; with `id: outputs`, that’s `${{ steps.outputs.cloudfront_url }}`, `${{ steps.outputs.api_url }}`, `${{ steps.outputs.frontend_bucket }}`.
- Prefer Terraform outputs for CloudFront distribution ID and use it directly for invalidation.
- Update naming for globally unique S3 buckets (append account ID or use `random_id`).
- Remove the duplicate Lambda build from the workflow (keep packaging inside `scripts/deploy.sh`).
- Add `-reconfigure` to `terraform init` when using the remote backend; note `-migrate-state` for first migration.
- Align `.gitignore` with Day 4 intent and include `uv.lock`.
- Drop `uv init --bare` in CI; keep `uv python pin` + `uv add -r requirements.txt`.
