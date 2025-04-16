"""Tests of authentication."""
import django.test
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from polls.models import Question, Choice

class UserAuthTest(django.test.TestCase):

    def setUp(self):
        # Initialize test user
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()

        # Create a sample question and choices
        self.question = Question.objects.create(question_text="First Poll Question")
        for n in range(1, 4):
            Choice.objects.create(choice_text=f"Choice {n}", question=self.question)

    def test_successful_login(self):
        """BC_AUTH_001: Verify that a user can successfully log in with valid credentials."""
        login_url = reverse("login")
        response = self.client.post(login_url, {
            "username": self.username,
            "password": self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_login_with_incorrect_username(self):
        """BC_AUTH_002: Verify that a user cannot log in with an incorrect username."""
        login_url = reverse("login")
        response = self.client.post(login_url, {
            "username": "wronguser",
            "password": self.password
        })
        self.assertEqual(response.status_code, 200)  # Should not redirect
        self.assertContains(response, "Please enter a correct username and password", status_code=200)

    def test_login_with_incorrect_password(self):
        """BC_AUTH_003: Verify that a user cannot log in with an incorrect password."""
        login_url = reverse("login")
        response = self.client.post(login_url, {
            "username": self.username,
            "password": "WrongPassword123"
        })
        self.assertEqual(response.status_code, 200)  # Should not redirect
        self.assertContains(response, "Please enter a correct username and password", status_code=200)

    def test_successful_logout(self):
        """BC_AUTH_004: Verify that a logged-in user can successfully log out."""
        logout_url = reverse("logout")
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Extra test: Authentication is required to submit a vote."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        choice = self.question.choice_set.first()
        response = self.client.post(vote_url, {"choice": str(choice.id)})
        login_redirect = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_redirect)
