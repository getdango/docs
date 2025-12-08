# Deployment Guide

This document explains how to deploy the Dango documentation to Cloudflare Pages.

## Cloudflare Pages Setup

### Initial Setup

1. **Connect Repository**:
   - Go to [Cloudflare Pages Dashboard](https://dash.cloudflare.com/pages)
   - Click "Create a project"
   - Select "Connect to Git"
   - Choose the `getdango/docs` repository
   - Authorize Cloudflare Pages

2. **Configure Build Settings**:
   ```
   Production branch: main
   Build command: pip install -r requirements.txt && mkdocs build
   Build output directory: site
   Root directory: (leave empty)
   ```

3. **Environment Variables**:
   ```
   PYTHON_VERSION=3.11
   ```

4. **Custom Domain**:
   - Go to project settings → Custom domains
   - Add custom domain: `docs.getdango.dev`
   - Follow DNS configuration instructions

### Build Configuration

The build process:

1. Cloudflare Pages checks out the `main` branch
2. Installs Python 3.11
3. Runs `pip install -r requirements.txt` to install MkDocs and plugins
4. Runs `mkdocs build` to generate static site
5. Deploys contents of `site/` directory to CDN

### Deployment Workflow

**Automatic Deployments:**

- **Production**: Every push to `main` branch triggers a production deployment
- **Preview**: Every pull request triggers a preview deployment

**Manual Deployments:**

You can also trigger deployments manually from the Cloudflare Pages dashboard.

---

## Branch Protection

The `main` branch is protected:

- ✅ Pull requests required
- ✅ Status checks must pass (configure after first deployment)
- ❌ Force pushes blocked
- ❌ Deletions blocked

---

## Adding Status Checks

After the first successful Cloudflare Pages deployment:

1. Go to GitHub repository settings
2. Navigate to **Branches** → **main** → **Edit**
3. Enable **Require status checks to pass before merging**
4. Select: `cloudflare-pages/build`
5. Save changes

This ensures all PRs pass the build check before merging.

---

## Monitoring Deployments

### Cloudflare Pages Dashboard

View deployment status, logs, and analytics:
- [Cloudflare Pages Dashboard](https://dash.cloudflare.com/pages)

### Deployment Logs

Each deployment shows:
- Build logs (pip install, mkdocs build output)
- Build time and status
- Preview URL for testing

### Preview Deployments

Every PR gets a unique preview URL:
```
https://<commit-hash>.docs.pages.dev
```

Use this to review changes before merging to production.

---

## Rollback Procedure

If a deployment causes issues:

1. Go to Cloudflare Pages dashboard
2. Select the project
3. Click "Deployments"
4. Find the last working deployment
5. Click "⋯" → "Rollback to this deployment"

---

## Local Testing

Always test locally before pushing:

```bash
# Activate virtual environment
source venv/bin/activate

# Build site
mkdocs build

# Serve locally
mkdocs serve

# Open http://localhost:8000 in browser
```

---

## Troubleshooting

### Build Fails on Cloudflare Pages

**Check build logs:**

1. Go to Cloudflare Pages dashboard
2. Click on the failed deployment
3. View build logs
4. Common issues:
   - Missing dependencies in `requirements.txt`
   - Python version mismatch
   - MkDocs configuration errors
   - Missing files referenced in `mkdocs.yml`

**Test locally first:**

```bash
# Clean build
rm -rf site/
mkdocs build
```

### Preview URL Not Working

- Check that the PR has completed building
- Preview URLs are available in PR comments (added by Cloudflare bot)
- DNS propagation can take a few minutes

### Custom Domain Issues

1. Verify DNS records in your domain registrar
2. Check Cloudflare DNS settings
3. SSL certificate generation can take up to 24 hours

---

## Performance

Cloudflare Pages provides:

- **Global CDN**: Content served from 200+ edge locations
- **Automatic SSL**: HTTPS enabled by default
- **Instant rollback**: One-click rollback to previous versions
- **Unlimited bandwidth**: No bandwidth limits

Expected performance:
- **Build time**: 1-2 minutes
- **Page load**: < 1 second globally
- **Deployment time**: < 30 seconds after build

---

## Cost

Cloudflare Pages is free for:
- Unlimited requests
- Unlimited bandwidth
- 500 builds per month
- 20,000 files per site

This is more than sufficient for documentation sites.

---

## Support

- **Cloudflare Pages Docs**: [developers.cloudflare.com/pages](https://developers.cloudflare.com/pages/)
- **MkDocs Material Docs**: [squidfunk.github.io/mkdocs-material](https://squidfunk.github.io/mkdocs-material/)
- **Repository Issues**: [github.com/getdango/docs/issues](https://github.com/getdango/docs/issues)
