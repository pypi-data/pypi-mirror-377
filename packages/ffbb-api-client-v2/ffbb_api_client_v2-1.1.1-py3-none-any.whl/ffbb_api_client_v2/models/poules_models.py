from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .rankings_models import TeamRanking


# Query Parameters Model
@dataclass
class PoulesQuery:
    deep_rencontres__limit: str | None = "1000"  # Original: deep[rencontres][_limit]
    fields_: list[str] | None = field(default=None)  # Original: fields[]


# Response Model
@dataclass
class GetPouleResponse:
    id: str

    @dataclass
    class RencontresitemModel:
        id: str
        numero: str
        numeroJournee: str
        idPoule: str
        competitionId: str
        resultatEquipe1: str
        resultatEquipe2: str
        joue: int
        nomEquipe1: str
        nomEquipe2: str
        date_rencontre: datetime

    rencontres: list[RencontresitemModel]
    classements: list[TeamRanking] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GetPouleResponse | None:
        """Convert dictionary to PoulesModel instance."""
        if not data:
            return None

        # Handle case where data is not a dictionary
        if not isinstance(data, dict):
            return None

        # Handle API error responses
        if "errors" in data:
            return None

        # Basic implementation - can be expanded later
        rencontres = []
        for rencontre_data in data.get("rencontres", []):
            if rencontre_data:
                rencontre = cls.RencontresitemModel(
                    id=str(rencontre_data.get("id", "")),
                    numero=str(rencontre_data.get("numero", "")),
                    numeroJournee=str(rencontre_data.get("numeroJournee", "")),
                    idPoule=str(rencontre_data.get("idPoule", "")),
                    competitionId=str(rencontre_data.get("competitionId", "")),
                    resultatEquipe1=str(rencontre_data.get("resultatEquipe1", "")),
                    resultatEquipe2=str(rencontre_data.get("resultatEquipe2", "")),
                    joue=int(rencontre_data.get("joue", 0)),
                    nomEquipe1=str(rencontre_data.get("nomEquipe1", "")),
                    nomEquipe2=str(rencontre_data.get("nomEquipe2", "")),
                    date_rencontre=datetime.fromisoformat(
                        rencontre_data.get("date_rencontre", "1970-01-01")
                    ),
                )
                rencontres.append(rencontre)

        # Process classements
        classements = []
        for classement_data in data.get("classements", []):
            if classement_data:
                classement = TeamRanking.from_dict(classement_data)
                if classement:
                    classements.append(classement)

        return cls(
            id=str(data.get("id", "")),
            rencontres=rencontres,
            classements=classements if classements else None,
        )
