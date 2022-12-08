from sqlalchemy import Column, ForeignKey, Integer, Text

from .abstract_donation_model import AbstractDonationModel


class Donation(AbstractDonationModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
