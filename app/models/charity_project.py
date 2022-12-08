from sqlalchemy import Column, String, Text

from .abstract_donation_model import AbstractDonationModel


class CharityProject(AbstractDonationModel):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
