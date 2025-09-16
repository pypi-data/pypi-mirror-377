import sys

from .clients.api_ffbb_app_client import ApiFFBBAppClient  # noqa
from .clients.ffbb_api_client_v2 import FFBBAPIClientV2  # noqa
from .clients.meilisearch_client import MeilisearchClient  # noqa
from .clients.meilisearch_ffbb_client import MeilisearchFFBBClient  # noqa
from .helpers.meilisearch_client_extension import MeilisearchClientExtension  # noqa
from .helpers.multi_search_query_helper import generate_queries  # noqa
from .models.multi_search_query import MultiSearchQuery  # noqa
from .models.multi_search_result_competitions import (  # noqa
    CompetitionsFacetDistribution,
    CompetitionsFacetStats,
    CompetitionsHit,
    CompetitionsMultiSearchResult,
)
from .models.multi_search_result_organismes import (  # noqa
    OrganismesFacetDistribution,
    OrganismesFacetStats,
    OrganismesHit,
    OrganismesMultiSearchResult,
)
from .models.multi_search_result_pratiques import (  # noqa
    PratiquesFacetDistribution,
    PratiquesFacetStats,
    PratiquesHit,
    PratiquesMultiSearchResult,
)
from .models.multi_search_result_rencontres import (  # noqa
    RencontresFacetDistribution,
    RencontresFacetStats,
    RencontresHit,
    RencontresMultiSearchResult,
)
from .models.multi_search_result_salles import (  # noqa
    SallesFacetDistribution,
    SallesFacetStats,
    SallesHit,
    SallesMultiSearchResult,
)
from .models.multi_search_result_terrains import (  # noqa
    TerrainsFacetDistribution,
    TerrainsFacetStats,
    TerrainsHit,
    TerrainsMultiSearchResult,
)
from .models.multi_search_result_tournois import (  # noqa
    TournoisFacetDistribution,
    TournoisFacetStats,
    TournoisHit,
    TournoisMultiSearchResult,
)

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.9`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
