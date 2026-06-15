# Jenkinsfile Quick Reference

## Files Included

- **Jenkinsfile** - Main pipeline for Windows Jenkins agents
- **Jenkinsfile.linux** - Alternative pipeline for Linux/Unix agents
- **JENKINS_SETUP.md** - Complete setup guide

## Key Features

✅ **Automated Triggers**
- Runs on every commit (via SCM polling)
- Scheduled daily at 7:00 AM
- Manual trigger available with test suite selection

✅ **Test Suite Flexibility**
- regression (full suite)
- smoke (quick sanity checks)
- products, brands, search, auth, user (specific modules)

✅ **Reports & Artifacts**
- HTML test reports generated automatically
- Reports archived in Jenkins
- Console logs with timestamps

✅ **Build Management**
- Keeps last 10 builds
- 30-minute timeout per build
- Automatic cleanup after build

## Quick Start (3 Steps)

### 1. Add Jenkins Plugins
```
Dashboard → Manage Jenkins → Manage Plugins

Install:
- Pipeline
- Git
- HTML Publisher
- Email Extension (optional)
- Slack Notification (optional)
```

### 2. Create Pipeline Job
```
Dashboard → New Item
Name: AutomationExercise-API-Tests
Type: Pipeline
OK
```

### 3. Configure Pipeline
```
Configuration:
- Definition: Pipeline script from SCM
- SCM: Git
- Repository URL: <your-repo-url>
- Script Path: Jenkinsfile
- Branch: */main (or your default branch)

Save → Done
```

## Trigger Configuration

### Immediate Runs (Every Commit)
Modify `pollSCM()` in Jenkinsfile:
```groovy
pollSCM('H * * * *')    // Every hour (default)
pollSCM('H/15 * * * *') // Every 15 minutes
```

Or use **GitHub/GitLab Webhook** (faster):
- More responsive than polling
- No Jenkins-initiated requests
- Recommended for production

### Daily Morning Runs
Modify `cron()` in Jenkinsfile:
```groovy
cron('0 7 * * *')      // 7:00 AM daily (default)
cron('0 9 * * 1-5')    // 9:00 AM weekdays only
cron('30 6 * * *')     // 6:30 AM daily
```

## Test Execution

### Via Jenkins UI
1. Click **Build Now** to run with default (regression)
2. Or click **Build with Parameters** to select specific suite
3. Watch the console for real-time output

### Manual Build Examples
```bash
# Default regression suite
curl -X POST http://jenkins-url:8080/job/AutomationExercise-API-Tests/build \
     -u username:api-token

# Specific test suite via Jenkins CLI
java -jar jenkins-cli.jar -s http://jenkins-url:8080 \
     build AutomationExercise-API-Tests \
     -p TEST_SUITE=smoke
```

## Report Access

1. Navigate to completed build
2. Click **Test Report** link
3. View detailed test results
4. Download HTML report for archiving

## Notifications (Optional)

### Email Setup
```groovy
post {
    failure {
        emailext(
            subject: 'Tests Failed',
            body: 'Check: ${BUILD_URL}',
            to: 'team@example.com'
        )
    }
}
```

### Slack Setup
```groovy
post {
    failure {
        slackSend(color: 'danger', message: 'Tests FAILED')
    }
}
```

## Environment Variables

Available in pipeline:
- `${BUILD_NUMBER}` - Build number
- `${BUILD_URL}` - Build URL
- `${WORKSPACE}` - Build workspace
- `${BRANCH_NAME}` - Git branch (requires branch plugin)
- `${GIT_COMMIT}` - Git commit hash

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Python not found | Add Python to PATH or use absolute path in Jenkinsfile |
| Tests timeout | Increase timeout value: `timeout(time: 60, unit: 'MINUTES')` |
| Permission denied | Ensure Jenkins user has workspace permissions |
| venv errors | Delete venv folder, rebuild, or use absolute path |
| No reports | Check reports/ directory exists, verify pytest-html installed |

## Advanced Features

### Run Multiple Branches
Create separate jobs:
- `AutomationExercise-API-Tests-Main`
- `AutomationExercise-API-Tests-Develop`

Configure each with appropriate branch specifier.

### Run in Docker
Replace agent section:
```groovy
agent {
    docker {
        image 'python:3.11'
        reuseNode true
    }
}
```

### Conditional Execution
```groovy
stage('Run Tests') {
    when {
        branch 'main'  // Only run on main branch
    }
    steps { ... }
}
```

## Cron Schedule Reference

Cron format: `minute hour day month day-of-week`

```
0 7 * * *     → 7:00 AM daily
0 2 * * *     → 2:00 AM daily
30 6 * * 1-5  → 6:30 AM weekdays
0 * * * *     → Every hour
H H * * *     → Once daily at random time
H H(9-17) * * 1-5 → Random time between 9 AM-5 PM weekdays
```

## Git Integration

### GitHub Webhook Setup
```
Settings → Webhooks → Add webhook
URL: https://jenkins-url/github-webhook/
Content type: application/json
Events: Push events
```

### GitLab Webhook Setup
```
Settings → Webhooks
URL: https://jenkins-url/project/job-name
Trigger: Push events
```

## Performance Tips

1. Use `.gitignore` to exclude large files
2. Set `skipDefaultCheckout()` if not needed
3. Use matrix builds to run tests in parallel
4. Archive only essential reports
5. Regular cleanup of old builds

## Support Resources

- [Jenkins Documentation](https://jenkins.io/doc/)
- [Pipeline Syntax](https://jenkins.io/doc/book/pipeline/syntax/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Git Plugin](https://plugins.jenkins.io/git/)
