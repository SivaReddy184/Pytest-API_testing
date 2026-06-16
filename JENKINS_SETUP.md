# Jenkins Pipeline Setup Guide

This guide explains how to integrate this API test framework with Jenkins.

## Prerequisites

1. **Jenkins Installation**: Jenkins 2.387+ or later
2. **Required Plugins**:
   - Pipeline (groovy)
   - Git plugin
   - HTML Publisher Plugin
   - Email Extension Plugin (for notifications)
   - Slack Notification Plugin (optional, for Slack alerts)

3. **Agent Requirements**:
   - Python 3.8+ installed on Jenkins agent
   - Git installed on Jenkins agent
   - Windows environment (or modify Jenkinsfile for Linux)

## Step 1: Install Jenkins Plugins

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Search for and install these plugins:
   - `Pipeline`
   - `Git`
   - `HTML Publisher`
   - `Email Extension`
   - `Slack Notification` (optional)
   - `Log Parser` (optional, for better log analysis)

3. Click **Install without restart** or **Restart Jenkins**

## Step 2: Create a New Pipeline Job

1. Click **New Item** on the Jenkins dashboard
2. Enter job name (e.g., `AutomationExercise-API-Tests`)
3. Select **Pipeline**
4. Click **OK**

## Step 3: Configure Pipeline Job

### General Section
- Enable **Discard old builds**
  - Days to keep builds: `30`
  - Max # of builds to keep: `10`

### Pipeline Section
- **Definition**: Select `Pipeline script from SCM`
- **SCM**: Choose `Git`
- **Repository URL**: Enter your Git repository URL
  ```
  https://github.com/your-username/automationexercise_api_framework.git
  ```
- **Credentials**: Add credentials if repository is private
- **Branch Specifier**: `*/main` (or your default branch)
- **Script Path**: `Jenkinsfile`

## Step 4: Configure Build Triggers

The Jenkinsfile includes two triggers:

### 1. **Poll SCM** (Triggered on commit)
- Checks every hour for changes
- Modify the schedule in the Jenkinsfile:
  ```groovy
  pollSCM('H * * * *')  // Current: every hour
  pollSCM('H/15 * * * *')  // Every 15 minutes
  pollSCM('H H * * *')  // Once per day at random time
  ```

### 2. **Cron Schedule** (Daily at 7 AM)
- Runs every morning at 7:00 AM
- Modify in the Jenkinsfile:
  ```groovy
  cron('0 7 * * *')  // 7:00 AM every day
  cron('0 9 * * 1-5')  // 9:00 AM, Monday-Friday
  ```

**Cron Syntax**: `(minute hour day month day-of-week)`
- `0 7 * * *` = 7:00 AM daily
- `0 2 * * *` = 2:00 AM daily
- `30 6 * * *` = 6:30 AM daily

## Step 5: Enable GitHub/GitLab Webhook (Optional, Better than Polling)

### For GitHub:
1. Go to GitHub repository → **Settings** → **Webhooks**
2. Click **Add webhook**
3. Payload URL: `https://your-jenkins-url/github-webhook/`
4. Content type: `application/json`
5. Events: Select `Push events`
6. Click **Add webhook**

### For GitLab:
1. Go to GitLab project → **Settings** → **Webhooks**
2. URL: `https://your-jenkins-url/project/your-jenkins-job-name`
3. Trigger: Select `Push events`
4. Click **Add webhook**

## Step 6: Configure Notifications

### Email Notifications:
1. In the Jenkinsfile, uncomment the email lines:
   ```groovy
   mail to: 'your-email@example.com', 
        subject: 'Tests Passed', 
        body: 'All tests passed successfully'
   ```

2. Configure SMTP in Jenkins:
   - Go to **Manage Jenkins** → **Configure System**
   - Find **Email Notification**
   - Configure SMTP settings

### Slack Notifications:
1. Install `Slack Notification` plugin
2. Configure in the Jenkinsfile:
   ```groovy
   post {
       success {
           slackSend(color: 'good', message: 'Tests PASSED')
       }
       failure {
           slackSend(color: 'danger', message: 'Tests FAILED')
       }
   }
   ```

## Step 7: Jenkins File Parameters

The pipeline supports a parameter for selecting which test suite to run:

```groovy
parameters {
    choice(
        name: 'TEST_SUITE',
        choices: ['regression', 'smoke', 'products', 'brands', 'search', 'auth', 'user'],
        description: 'Select which test suite to run'
    )
}
```

You can manually trigger the job and select a test suite.

### ⚠️ Important: Parameters in Auto-Triggered Builds

**When Jenkins automatically triggers a build** (via webhook, pollSCM, or cron schedule), it uses the **first parameter value in the choices list** as the default:

```groovy
choices: ['regression', 'smoke', 'products', 'brands', 'search', 'auth', 'user']
                    ↑
        This is used for auto-triggered builds
```

#### Scenario Breakdown:

| Trigger Type | TEST_SUITE Value | Notes |
|---|---|---|
| **Manual Build** | User selects | User clicks "Build Now" and chooses from dropdown |
| **Webhook/Poll** | `regression` | Auto-triggered builds use the 1st choice (default) |
| **Cron Schedule** | `regression` | Auto-triggered builds use the 1st choice (default) |

#### Example Workflow:
```
1. Developer pushes to main (triggers webhook)
   ↓
   Jenkins starts build with TEST_SUITE='regression'
   
2. Manual trigger via "Build Now"
   ↓
   User selects TEST_SUITE='smoke' from dropdown
   ↓
   Jenkins starts build with selected value
```

### Customizing Auto-Triggered Behavior

If you want auto-triggered builds to run a different suite, **reorder the choices list**:

**Current order** (regression runs on auto-trigger):
```groovy
choices: ['regression', 'smoke', 'products', 'brands', 'search', 'auth', 'user']
```

**To run 'smoke' on auto-trigger** (faster feedback):
```groovy
choices: ['smoke', 'regression', 'products', 'brands', 'search', 'auth', 'user']
```

**To run 'products' tests on auto-trigger**:
```groovy
choices: ['products', 'regression', 'smoke', 'brands', 'search', 'auth', 'user']
```

### Alternative: Environment-Based Trigger Detection

You can detect and handle auto-triggered vs manual builds differently:

```groovy
environment {
    // Default to regression for auto-triggered, allow override for manual
    DEFAULT_SUITE = 'regression'
    TEST_SUITE = "${params.TEST_SUITE ?: env.DEFAULT_SUITE}"
}

stage('Run Tests') {
    steps {
        script {
            echo "Running: ${env.TEST_SUITE} suite"
            // Use env.TEST_SUITE in your pytest commands
        }
    }
}
```

## Step 8: Manual Build Trigger

You can also trigger the job:
- **Via Jenkins UI**: Click **Build Now**
- **Via CLI**: 
  ```bash
  curl -X POST http://jenkins-url:8080/job/AutomationExercise-API-Tests/build \
       -u username:token
  ```
- **Via Git Hook**: Add a post-push hook in your Git repository

## Step 9: View Test Reports

1. After the build completes, go to the build page
2. Click **Test Report** to view the HTML report
3. Reports are archived and accessible from build history

## Monitoring & Troubleshooting

### View Build Console
- Click on any build number
- Click **Console Output**
- Check for errors

### Common Issues:

**Issue**: Python not found
- **Solution**: Ensure Python is in PATH on Jenkins agent, or update the Jenkinsfile with absolute Python path

**Issue**: Dependencies not installing
- **Solution**: Check internet connectivity on Jenkins agent, or use a requirements mirror

**Issue**: Virtual environment errors
- **Solution**: Delete `venv` folder and rebuild, or change `VENV_DIR` path

**Issue**: Permission denied on venv scripts
- **Solution**: Ensure Jenkins agent has write permissions in workspace

## Advanced Configuration

### Run in Docker (Recommended)
Replace the agent section:
```groovy
agent {
    docker {
        image 'python:3.11'
        args '-v /var/run/docker.sock:/var/run/docker.sock'
    }
}
```

### Run in Parallel on Multiple Agents
```groovy
agent {
    label 'python && windows'
}
```

### Archive Test Artifacts
The Jenkinsfile already archives:
- HTML test reports
- JUnit XML results (if generated)

## Best Practices

1. ✅ Use a branch protection rule on `main` to require pipeline success
2. ✅ Set up email/Slack notifications for failures
3. ✅ Archive reports for compliance/audit purposes
4. ✅ Use a separate pipeline job for each branch (main, develop, etc.)
5. ✅ Pin Jenkins plugin versions for consistency
6. ✅ Regularly review and clean old builds
7. ✅ **For parameterized jobs**: Keep the fastest/most critical test suite first in the choices list for auto-triggered builds
8. ✅ **Document parameter defaults**: Add comments in the Jenkinsfile explaining which test suite runs by default
9. ✅ **Monitor auto-triggered builds**: Check build console to verify correct test suite is running

### Parameter Best Practice Example:
```groovy
// ✅ GOOD: Put fastest/most important test first
choices: ['smoke', 'regression', 'products', 'brands']
         // Auto-triggered builds will run 'smoke' (fast feedback)

// ❌ AVOID: Slow tests as default for auto-triggered builds  
choices: ['regression', 'smoke', 'products', 'brands']
         // This is fine, but runs full regression on every commit (slower)
```

## Troubleshooting Parameters

### Issue: Auto-triggered build runs wrong test suite
**Cause**: The choices list isn't ordered correctly
**Solution**: Reorder the choices in parameters section (first value is default)

### Issue: Manual build keeps using the first choice
**Cause**: This is expected Jenkins behavior - verify in "Build Now" dropdown
**Solution**: This is normal; Jenkins shows all choices for manual builds

### Issue: Need different suites for different triggers
**Solution**: Use environment detection or create multiple jobs:
```groovy
environment {
    TRIGGER_CAUSE = "${BUILD_CAUSE}"
    // BUILD_CAUSE can be: MANUAL, SCM_TRIGGER, TIMER, etc.
}
```

### How to Check Which Test Suite Ran
1. Open the completed build
2. Click **Console Output**
3. Look for the line:
   ```
   ========== Running [SUITE_NAME] tests ==========
   ```

## Support

For issues or questions:
- Check Jenkins logs: **Manage Jenkins** → **System Log**
- Review the build console output
- Verify Python and Git versions on the Jenkins agent
- Check firewall rules for GitHub/GitLab webhook connectivity
