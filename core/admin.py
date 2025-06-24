from django.contrib import admin
from django.contrib import admin
from .models import (
    Property, Amenity, PropertyAmenity, Facility, PropertyFacility,
    HouseRule, PropertyHouseRule, Booking, Review, Conversation,
    ConversationParticipant, Message, Photo, Availability
)

admin.site.register(Property)
admin.site.register(Amenity)
admin.site.register(PropertyAmenity)
admin.site.register(Facility)
admin.site.register(PropertyFacility)
admin.site.register(HouseRule)
admin.site.register(PropertyHouseRule)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Conversation)
admin.site.register(ConversationParticipant)
admin.site.register(Message)
admin.site.register(Photo)
admin.site.register(Availability)
