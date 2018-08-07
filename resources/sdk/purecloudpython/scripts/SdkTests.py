import base64, imp, os, requests, sys, unittest, uuid
from pprint import pprint

# Load SDK from local build
sys.path.append('../../../../output/purecloudpython/build/build/lib')
import PureCloudPlatformClientV2


class SdkTests(unittest.TestCase):
	lastResult = None

	userId = None
	userEmail = None;
	userName = 'Python SDK Tester'
	userDepartment = 'Ministry of Testing'
	userProfileSkill = 'Testmaster'
	busyPresenceId = '31fe3bac-dea6-44b7-bed7-47f91660a1a0'
	availablePresenceId = '6a3af858-942f-489d-9700-5f9bcdcdae9b'

	users_api = PureCloudPlatformClientV2.UsersApi()


	def setUp(self):
		# Skip if there has been a failure
		if SdkTests.lastResult != None and (len(SdkTests.lastResult.failures) > 0 or len(SdkTests.lastResult.errors) > 0):
			self.skipTest('Previous test failed')


	def run(self, result=None):
		# Store this execution's result as the last one
		SdkTests.lastResult = result

		# Run the test
		unittest.TestCase.run(self, result)



	def test_1_trace_basic_information(self):
		print 'PURECLOUD_ENVIRONMENT=%s' % (os.environ.get('PURECLOUD_ENVIRONMENT'))
		self.assertIsNotNone(os.environ.get('PURECLOUD_ENVIRONMENT'))

		print 'PURECLOUD_CLIENT_ID=%s' % (os.environ.get('PURECLOUD_CLIENT_ID'))
		self.assertIsNotNone(os.environ.get('PURECLOUD_CLIENT_ID'))

		self.assertIsNotNone(os.environ.get('PURECLOUD_CLIENT_SECRET'))

		SdkTests.userEmail = '%s@%s' % (uuid.uuid4(), os.environ.get('PURECLOUD_ENVIRONMENT'))
		print SdkTests.userEmail

		print PureCloudPlatformClientV2


	def test_2_authenticate(self):
		PureCloudPlatformClientV2.configuration.host = 'https://api.%s' % (os.environ.get('PURECLOUD_ENVIRONMENT'))

		# Base64 encode the client ID and client secret
		authorization = base64.b64encode('%s:%s' % (os.environ.get('PURECLOUD_CLIENT_ID'), os.environ.get('PURECLOUD_CLIENT_SECRET')))

		# Prepare for POST /oauth/token request
		requestHeaders = {
			'Authorization': 'Basic ' + authorization,
			'Content-Type': 'application/x-www-form-urlencoded'
		}
		requestBody = {
			'grant_type': 'client_credentials'
		}

		# Get token
		response = requests.post('https://login.%s/oauth/token' % (os.environ.get('PURECLOUD_ENVIRONMENT')), data=requestBody, headers=requestHeaders)

		# Check response
		self.assertEqual(response.status_code, 200)

		# Set token on SDK
		responseJson = response.json()
		self.assertIsNotNone(responseJson['access_token'])
		PureCloudPlatformClientV2.configuration.access_token = responseJson['access_token']


	def test_3_create_user(self):
		body = PureCloudPlatformClientV2.CreateUser()
		body.name = SdkTests.userName
		body.email = SdkTests.userEmail
		body.password = '%s!@#$1234asdfASDF' % (uuid.uuid4())

		user = SdkTests.users_api.post_users(body)

		SdkTests.userId = user.id
		self.assertEqual(user.name, SdkTests.userName)
		self.assertEqual(user.email, SdkTests.userEmail)


	def test_4_update_user(self):
		updateUser = PureCloudPlatformClientV2.UpdateUser()
		updateUser.department = SdkTests.userDepartment
		updateUser.version = 1

		user = SdkTests.users_api.patch_user(SdkTests.userId, updateUser)

		self.assertEqual(user.id, SdkTests.userId)
		self.assertEqual(user.name, SdkTests.userName)
		self.assertEqual(user.email, SdkTests.userEmail)
		self.assertEqual(user.department, SdkTests.userDepartment)


	def test_5_set_profile_skills(self):
		skills = SdkTests.users_api.put_user_profileskills(SdkTests.userId, [ SdkTests.userProfileSkill ])

		self.assertEqual(len(skills), 1)
		self.assertEqual(skills[0], SdkTests.userProfileSkill)


	def test_6_get_user(self):
		user = SdkTests.users_api.get_user(SdkTests.userId, expand = [ 'profileSkills' ])

		self.assertEqual(user.id, SdkTests.userId)
		self.assertEqual(user.name, SdkTests.userName)
		self.assertEqual(user.email, SdkTests.userEmail)
		self.assertEqual(user.department, SdkTests.userDepartment)
		self.assertEqual(user.profile_skills[0], SdkTests.userProfileSkill)


	def test_7_delete_user(self):
		SdkTests.users_api.delete_user(SdkTests.userId)



if __name__ == '__main__':
	unittest.sortTestMethodsUsing(None)
	unittest.main()