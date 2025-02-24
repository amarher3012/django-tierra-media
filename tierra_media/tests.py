from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tierra_media.models import Character, Location, Faction, Race


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.test_user = self.User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            is_active=True,
        )

        self.faction = Faction.objects.create(name="Mordor")
        self.location = Location.objects.create(name="Rivendel")
        self.race = Race.objects.create(name="Humano")

        self.character = Character.objects.create(
            user=self.test_user,
            name="Test Character",
            faction=self.faction,
            location=self.location,
            race=self.race,
        )

    def test_register_view(self):
        response = self.client.get(reverse("tierra_media:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signin.html")

        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        response = self.client.post(reverse("tierra_media:register"), data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(get_user_model().objects.filter(username="newuser").exists())

    def test_index_view(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("tierra_media:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tierra_media/index.html")
        self.assertIn("characters", response.context)

    def test_character_creation(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("tierra_media:character_creation"))
        self.assertEqual(response.status_code, 200)

        data = {
            "name": "New Character",
            "sex": "F",
            "faction": self.faction.id,
            "location": self.location.id,
            "race": self.race.id,
        }
        response = self.client.post(reverse("tierra_media:character_creation"), data)
        self.assertEqual(response.status_code, 302)

    def test_character_details(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("tierra_media:character_details", kwargs={"pk": self.character.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tierra_media/character_menu.html")

    def test_move_character(self):
        self.client.login(username="testuser", password="testpass123")
        new_location = Location.objects.create(name="New Location")

        response = self.client.post(
            reverse("tierra_media:move", kwargs={"pk": self.character.pk}),
            {"location": new_location.id},
        )
        self.assertEqual(response.status_code, 302)

        self.character.refresh_from_db()
        self.assertEqual(self.character.location, new_location)
