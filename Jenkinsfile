pipeline {
    agent any

    stages {
        stage('Virtual Env Test') {
            steps {
                echo 'Running Virtual install tests...'                
            }
        }
        stage('Virtual Env Test Cleanup') {
            steps {
                echo 'Cleaning up Virtual install tests...'                
            }
        }
        stage('Physical Install Test') {
            steps {
                echo 'Running Physical install tests...'
                cp /var/lib/jenkins/workspace/snaps-config/lab3/lab3-SoS.yaml /var/lib/jenkins/workspace/snaps-config/jenkins-ci/lab3-SoS.yaml
                python /var/lib/jenkins/workspace/snaps-orchestration/openstack-launch.py -t /var/lib/jenkins/workspace/snaps-openstack/ci/snaps/snaps_os_tmplt.yaml -e /var/lib/jenkins/workspace/snaps-config/jenkins-ci/lab3-SoS.yaml -v build_id=$BUILD_ID -d
            }
        }
        stage('Cleaning up Physical Install Test') {
            steps {
                echo 'Cleaning up Physical install tests...'
                python /var/lib/jenkins/workspace/snaps-orchestration/openstack-launch.py -t /var/lib/jenkins/workspace/snaps-openstack/ci/snaps/snaps_os_tmplt.yaml -e /var/lib/jenkins/workspace/snaps-config/jenkins-ci/lab3-SoS.yaml -v build_id=$BUILD_ID -i -c
            }
        }
        stage('Baremetal install Test') {
            steps {
                echo 'Running Baremetal install tests...'
            }
        }
        stage('Baremetal install Test') {
            steps {
                echo 'Running Baremetal install tests...'
            }
        }
    }
}
