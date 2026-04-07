import strawberry
from typing import List, Optional
from chalicelib.schema import SolarSite, EnergyReading, CreateSiteInput, AddReadingInput
from chalicelib import models


@strawberry.type
class Query:
    @strawberry.field
    def sites(self) -> List[SolarSite]:
        items = models.get_all_sites()
        return [
            SolarSite(
                site_id=item['site_id'],
                name=item['name'],
                location=item['location'],
                capacity=float(item['capacity']),
                created_at=item['created_at']
            )
            for item in items
        ]

    @strawberry.field
    def site(self, site_id: str) -> Optional[SolarSite]:
        item = models.get_site(site_id)
        if not item:
            return None
        return SolarSite(
            site_id=item['site_id'],
            name=item['name'],
            location=item['location'],
            capacity=float(item['capacity']),
            created_at=item['created_at']
        )

    @strawberry.field
    def readings(self, site_id: str, limit: int = 10) -> List[EnergyReading]:
        items = models.get_readings(site_id, limit)
        return [
            EnergyReading(
                site_id=item['site_id'],
                timestamp=item['timestamp'],
                output_kw=float(item['output_kw'])
            )
            for item in items
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_site(self, input: CreateSiteInput) -> SolarSite:
        item = models.create_site(
            name=input.name,
            location=input.location,
            capacity=input.capacity
        )
        return SolarSite(
            site_id=item['site_id'],
            name=item['name'],
            location=item['location'],
            capacity=float(item['capacity']),
            created_at=item['created_at']
        )

    @strawberry.mutation
    def add_reading(self, input: AddReadingInput) -> EnergyReading:
        item = models.add_reading(
            site_id=input.site_id,
            output_kw=input.output_kw
        )
        return EnergyReading(
            site_id=item['site_id'],
            timestamp=item['timestamp'],
            output_kw=float(item['output_kw'])
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)