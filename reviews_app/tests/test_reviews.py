from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from profiles_app.models import Profile
from reviews_app.models import Review
from rest_framework import status
from datetime import datetime
import pytz
import time

class ReviewTestsHappy(APITestCase):

    def setUp(self):
        # print user count to verify test DB starts empty
        # print(f"Users before setup: {User.objects.count()}")
        # clear existing reviews to ensure clean state
        Review.objects.all().delete()
        # set up test client
        self.client = APIClient()
        # create reviewer (customer)
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        # get existing profile (auto-created by signal) and set type to customer
        self.reviewer_profile = Profile.objects.get(user=self.reviewer)
        self.reviewer_profile.type = 'customer'
        self.reviewer_profile.save()
        # create business user 1
        self.business_user1 = User.objects.create_user(
            username='business1',
            email='business1@example.com',
            password='testpass456'
        )
        # get existing profile (auto-created by signal) and set type to business
        self.business_user1_profile = Profile.objects.get(user=self.business_user1)
        self.business_user1_profile.type = 'business'
        self.business_user1_profile.save()
        # create business user 2
        self.business_user2 = User.objects.create_user(
            username='business2',
            email='business2@example.com',
            password='testpass789'
        )
        # get existing profile (auto-created by signal) and set type to business
        self.business_user2_profile = Profile.objects.get(user=self.business_user2)
        self.business_user2_profile.type = 'business'
        self.business_user2_profile.save()
        # authenticate as reviewer
        self.client.force_authenticate(user=self.reviewer)

    # get review tests

    def test_get_reviews_list(self):
        # create reviews for this test
        review2 = Review.objects.create(
            business_user=self.business_user2,
            reviewer=self.reviewer,
            rating=5,
            description='Top Qualität und schnelle Lieferung!'
        )
        time.sleep(1)  # Delay for timestamp
        review1 = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=4,
            description='Sehr professioneller Service.'
        )
        # test listing all reviews
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response structure (order by -updated_at)
        expected_data = [
            {
                'id': review1.id,
                'business_user': self.business_user1.id,
                'reviewer': self.reviewer.id,
                'rating': 4,
                'description': 'Sehr professioneller Service.',
                'created_at': review1.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': review1.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            },
            {
                'id': review2.id,
                'business_user': self.business_user2.id,
                'reviewer': self.reviewer.id,
                'rating': 5,
                'description': 'Top Qualität und schnelle Lieferung!',
                'created_at': review2.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': review2.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        ]
        self.assertEqual(response.data, expected_data)

    def test_get_reviews_filtered_and_ordered(self):
        # create reviews for this test
        review2 = Review.objects.create(
            business_user=self.business_user2,
            reviewer=self.reviewer,
            rating=5,
            description='Top Qualität und schnelle Lieferung!'
        )
        time.sleep(1)  # Delay for timestamp
        review1 = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=4,
            description='Sehr professioneller Service.'
        )
        # test listing reviews with filter and ordering
        url = reverse('review-list') + f'?business_user_id={self.business_user1.id}&ordering=rating'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response structure (filtered, ordered by rating)
        expected_data = [
            {
                'id': review1.id,
                'business_user': self.business_user1.id,
                'reviewer': self.reviewer.id,
                'rating': 4,
                'description': 'Sehr professioneller Service.',
                'created_at': review1.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': review1.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        ]
        self.assertEqual(response.data, expected_data)

    # create review tests

    def test_create_review_success(self):
        # test creating review as customer
        url = reverse('review-list')
        data = {
            'business_user_id': self.business_user1.id,  # changed to business_user_id per updated serializer
            'rating': 5,
            'description': 'Excellent service!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # assert response structure
        self.assertEqual(response.data['business_user'], self.business_user1.id)
        self.assertEqual(response.data['reviewer'], self.reviewer.id)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Excellent service!')

    # update review tests

    def test_update_review_success(self):
        # create review for this test
        review = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=4,
            description='Original description'
        )
        # test updating review as owner
        url = reverse('review-detail', kwargs={'pk': review.id})
        data = {'rating': 5, 'description': 'Updated description'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert response structure
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Updated description')

    # delete review tests

    def test_delete_review_success(self):
        # create review for this test
        review = Review.objects.create(
            business_user=self.business_user1,
            reviewer=self.reviewer,
            rating=4,
            description='Test review'
        )
        # test deleting review as owner
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

class ReviewTestsUnhappy(APITestCase):

    def setUp(self):
        # print user count to verify test DB starts empty
        # print(f"Users before setup: {User.objects.count()}")
        # clear existing reviews to ensure clean state
        Review.objects.all().delete()
        # set up test client
        self.client = APIClient()
        # create reviewer (customer)
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        # get existing profile (auto-created by signal) and set type to customer
        self.reviewer_profile = Profile.objects.get(user=self.reviewer)
        self.reviewer_profile.type = 'customer'
        self.reviewer_profile.save()
        # create business user
        self.business_user = User.objects.create_user(
            username='business',
            email='business@example.com',
            password='testpass456'
        )
        # get existing profile (auto-created by signal) and set type to business
        self.business_profile = Profile.objects.get(user=self.business_user)
        self.business_profile.type = 'business'
        self.business_profile.save()
        # create non-owner user
        self.non_owner = User.objects.create_user(
            username='nonowner',
            email='nonowner@example.com',
            password='testpass789'
        )
        # get existing profile (auto-created by signal) and set type to customer
        self.non_owner_profile = Profile.objects.get(user=self.non_owner)
        self.non_owner_profile.type = 'customer'
        self.non_owner_profile.save()
        # authenticate as reviewer by default
        self.client.force_authenticate(user=self.reviewer)

    # get review tests

    def test_get_reviews_unauthenticated(self):
        # test listing reviews unauthenticated
        self.client.force_authenticate(user=None)
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # create review tests

    def test_create_review_invalid_rating(self):
        # test creating with invalid rating
        url = reverse('review-list')
        data = {'business_user_id': self.business_user.id, 'rating': 0, 'description': 'Test'}  # changed to business_user_id
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Rating must be between 1 and 5.', str(response.data))

    def test_create_review_invalid_business_user(self):
        # test creating with invalid business_user_id
        url = reverse('review-list')
        data = {'business_user_id': 999, 'rating': 5, 'description': 'Test'}  # changed to business_user_id
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Business user not found or not a business profile.', str(response.data))

    def test_create_review_unauthenticated(self):
        # test creating review unauthenticated
        self.client.force_authenticate(user=None)
        url = reverse('review-list')
        data = {'business_user_id': 1, 'rating': 5, 'description': 'Test'}  # changed to business_user_id
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_non_customer(self):
        # test creating as non-customer
        Profile.objects.filter(user=self.reviewer).update(type='business')
        url = reverse('review-list')
        data = {'business_user_id': self.business_user.id, 'rating': 5, 'description': 'Test'}  # changed to business_user_id
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  

    def test_create_review_duplicate(self):
        # create existing review for this test
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        # test creating duplicate
        url = reverse('review-list')
        data = {
            'business_user_id': self.business_user.id,  # changed to business_user_id
            'rating': 5,
            'description': 'Duplicate'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You have already reviewed this business user.', str(response.data))

    # update review tests

    def test_update_review_unauthenticated(self):
        # create review for this test
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        # test updating review unauthenticated
        self.client.force_authenticate(user=None)
        url = reverse('review-detail', kwargs={'pk': review.id})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_not_owner(self):
        # create review for this test
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        # test updating as non-owner
        self.client.force_authenticate(user=self.non_owner)
        url = reverse('review-detail', kwargs={'pk': review.id})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You are not the owner of this review.', str(response.data))

    def test_update_review_invalid_rating(self):
        # create review for this test
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        # test updating with invalid rating
        url = reverse('review-detail', kwargs={'pk': review.id})
        data = {'rating': 0}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Rating must be between 1 and 5.', str(response.data))

    def test_update_review_not_found(self):
        # test updating non-existent review
        url = reverse('review-detail', kwargs={'pk': 999})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # delete reviews tests

    def test_delete_review_unauthenticated(self):
        # create review for this test
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        # test deleting review unauthenticated
        self.client.force_authenticate(user=None)
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_not_owner(self):
        # create review for this test
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer,
            rating=4,
            description='Test'
        )
        # test deleting as non-owner
        self.client.force_authenticate(user=self.non_owner)
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You are not the owner of this review.', str(response.data))

    def test_delete_review_not_found(self):
        # test deleting non-existent review
        url = reverse('review-detail', kwargs={'pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)