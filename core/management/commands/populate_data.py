from django.core.management.base import BaseCommand
from core.models import Amenity, Facility, HouseRule

class Command(BaseCommand):
    help = 'Populates initial data for Amenities, Facilities, and House Rules.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Populating initial data...'))

        amenities = [
            {'name': 'Wifi', 'icon': 'wifi'},
            {'name': 'Kitchen', 'icon': 'kitchen'},
            {'name': 'Air conditioning', 'icon': 'ac'},
            {'name': 'Heating', 'icon': 'heating'},
            {'name': 'Washer', 'icon': 'washer'},
            {'name': 'Dryer', 'icon': 'dryer'},
            {'name': 'TV', 'icon': 'tv'},
            {'name': 'Hair dryer', 'icon': 'hair_dryer'},
            {'name': 'Iron', 'icon': 'iron'},
            {'name': 'Pool', 'icon': 'pool'},
            {'name': 'Hot tub', 'icon': 'hot_tub'},
            {'name': 'Free parking on premises', 'icon': 'parking'},
            {'name': 'EV charger', 'icon': 'ev_charger'},
            {'name': 'Crib', 'icon': 'crib'},
            {'name': 'BBQ grill', 'icon': 'bbq'},
            {'name': 'Outdoor dining area', 'icon': 'outdoor_dining'},
            {'name': 'Fire pit', 'icon': 'fire_pit'},
            {'name': 'Exercise equipment', 'icon': 'exercise'},
            {'name': 'Breakfast', 'icon': 'breakfast'},
            {'name': 'Indoor fireplace', 'icon': 'fireplace'},
        ]

        for data in amenities:
            amenity, created = Amenity.objects.get_or_create(name=data['name'], defaults={'icon': data['icon']})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Amenity: {amenity.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Amenity already exists: {amenity.name}'))

        facilities = [
            {'name': 'Gym', 'icon': 'gym'},
            {'name': 'Free parking', 'icon': 'parking'},
            {'name': 'Paid parking on premises', 'icon': 'paid_parking'},
            {'name': 'Paid parking off premises', 'icon': 'paid_parking_off'},
            {'name': 'Hot tub', 'icon': 'hot_tub'},
            {'name': 'Pool', 'icon': 'pool'},
            {'name': 'Sauna', 'icon': 'sauna'},
            {'name': 'Steam room', 'icon': 'steam_room'},
            {'name': 'Outdoor shower', 'icon': 'outdoor_shower'},
            {'name': 'Patio or balcony', 'icon': 'patio'},
            {'name': 'Backyard', 'icon': 'backyard'},
            {'name': 'Beach access', 'icon': 'beach_access'},
            {'name': 'Ski-in/Ski-out', 'icon': 'ski_in_out'},
            {'name': 'Lake access', 'icon': 'lake_access'},
            {'name': 'Waterfront', 'icon': 'waterfront'},
            {'name': 'Ski resort', 'icon': 'ski_resort'},
            {'name': 'Golf course', 'icon': 'golf_course'},
            {'name': 'Tennis court', 'icon': 'tennis_court'},
            {'name': 'Basketball court', 'icon': 'basketball_court'},
            {'name': 'Volleyball court', 'icon': 'volleyball_court'},
        ]

        for data in facilities:
            facility, created = Facility.objects.get_or_create(name=data['name'], defaults={'icon': data['icon']})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Facility: {facility.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Facility already exists: {facility.name}'))

        house_rules = [
            {'name': 'No smoking', 'description': 'Smoking is not allowed inside the property.'},
            {'name': 'No pets', 'description': 'Pets are not allowed.'},
            {'name': 'No parties or events', 'description': 'Parties or events are strictly prohibited.'},
            {'name': 'Check-in time is 3 PM - 10 PM', 'description': 'Guests must check in between 3 PM and 10 PM.'},
            {'name': 'Check-out time is 11 AM', 'description': 'Guests must check out by 11 AM.'},
            {'name': 'Quiet hours 10 PM - 8 AM', 'description': 'Please observe quiet hours between 10 PM and 8 AM.'},
            {'name': 'No unregistered guests', 'description': 'Only registered guests are allowed on the property.'},
            {'name': 'Please take off your shoes', 'description': 'Kindly remove your shoes before entering the house.'},
            {'name': 'Dispose of trash properly', 'description': 'Please use the designated bins for trash and recycling.'},
            {'name': 'Conserve energy', 'description': 'Turn off lights and AC when leaving the property.'},
        ]

        for data in house_rules:
            rule, created = HouseRule.objects.get_or_create(name=data['name'], defaults={'description': data['description']})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created House Rule: {rule.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'House Rule already exists: {rule.name}'))

        self.stdout.write(self.style.SUCCESS('Data population complete.'))
