pipeline {
    agent any

    triggers {
        // Poll SCM every minute to detect changes
        pollSCM('H * * * *')
        
        // Schedule daily at 7:00 AM
        cron('0 7 * * *')
    }

    parameters {
        choice(
            name: 'TEST_SUITE',
            choices: ['regression', 'smoke', 'products', 'brands', 'search', 'auth', 'user'],
            description: 'Select which test suite to run (default: regression for auto-triggered builds)'
        )
    }

    options {
        // Keep last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Add timestamps to console output
        timestamps()
        // Timeout after 30 minutes
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        // Set Python path and virtual environment
        PYTHON_VERSION = '3.11'
        // CHANGED: Use double quotes so ${WORKSPACE} evaluates correctly
        VENV_DIR = "${WORKSPACE}/venv"
        PATH = "${VENV_DIR}/Scripts;${PATH}"
        // Email configuration from .env file or Jenkins credentials
        BUILD_RESULTS_EMAIL = credentials('BUILD_RESULTS_EMAIL')
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "========== Checking out code =========="
                    checkout scm
                }
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    echo "========== Setting up Python environment =========="
                    
                    // Create virtual environment
                    bat '''
                        python -m venv venv
                        call venv\\Scripts\\activate.bat
                    '''
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    echo "========== Installing dependencies =========="
                    
                    bat '''
                        call venv\\Scripts\\activate.bat
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "========== Running ${params.TEST_SUITE} tests =========="
                    
                    bat '''
                        call venv\\Scripts\\activate.bat
                        
                        REM Create reports directory if it doesn't exist
                        if not exist "reports" mkdir reports
                        
                        if "%TEST_SUITE%"=="smoke" (
                            pytest -m smoke -v --html=reports/report.html --self-contained-html --tb=short --capture=no
                        ) else if "%TEST_SUITE%"=="regression" (
                            pytest -v --html=reports/report.html --self-contained-html --tb=short --capture=no
                        ) else (
                            pytest -m %TEST_SUITE% -v --html=reports/report.html --self-contained-html --tb=short --capture=no
                        )
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo "========== Test Execution Complete =========="
                
                // Archive test reports
                archiveArtifacts artifacts: 'reports/report.html', 
                                 allowEmptyArchive: true,
                                 onlyIfSuccessful: false
                
                // Publish HTML test report
                publishHTML([
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'Test Report',
                    keepAll: true
                ])
                
                // Collect JUnit test results if available
                junit testResults: 'reports/*.xml', 
                      allowEmptyResults: true
            }
        }
        
        success {
            script {
                echo "========== Tests PASSED =========="
                // Add email or Slack notification for success
                mail to: "${BUILD_RESULTS_EMAIL}", subject: 'Tests Passed', body: 'All tests passed successfully'
            }
        }
        
        failure {
            script {
                echo "========== Tests FAILED =========="
                // Add email or Slack notification for failure
                mail to: "${BUILD_RESULTS_EMAIL}", subject: 'Tests Failed', body: 'Some tests failed. Check the report.'
            }
        }
        
        unstable {
            script {
                echo "========== Build UNSTABLE =========="
            }
        }
        
        cleanup {
            script {
                echo "========== Cleaning up =========="
                // Clean up virtual environment
                bat '''
                    if exist venv rmdir /s /q venv
                    if exist __pycache__ rmdir /s /q __pycache__
                '''
                cleanWs()
            }
        }
    }
}
