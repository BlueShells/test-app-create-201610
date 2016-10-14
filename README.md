# test-app-create-201610

TODO:

* use standardised project name
  * openshift-monitoring
* hide project visibility from admins
  * /etc/sysconfig/openshift-dedicated-role
* change deployment name for each test
  * oc new-app http://github.com --name=build-test.date.random -n openshift-monitoring
  * oc new-app image --name=deploy-test.date.random -n openshift-monitoring
* ensure cleanup in script
  * delete just the app
  * delete project if need to clean further
  * setup() should create project
