from unittest.mock import sentinel

import pytest

from h.services.search_index.service_factory import factory


class TestFactory:
    def test_it(
        self, pyramid_request, SearchIndexService, settings, BatchIndexer, Queue
    ):
        result = factory(sentinel.context, pyramid_request)

        BatchIndexer.assert_called_once_with(
            pyramid_request.db, pyramid_request.es, pyramid_request
        )
        Queue.assert_called_once_with(
            db=pyramid_request.db,
            es=pyramid_request.es,
            batch_indexer=BatchIndexer.return_value,
            limit=10,
        )
        SearchIndexService.assert_called_once_with(
            request=pyramid_request,
            es_client=pyramid_request.es,
            session=pyramid_request.db,
            settings=settings,
            queue=Queue.return_value,
        )
        assert result == SearchIndexService.return_value

    @pytest.fixture
    def settings(self, pyramid_config):
        settings = sentinel.settings
        pyramid_config.register_service(settings, name="settings")
        return settings

    @pytest.fixture
    def pyramid_request(self, pyramid_request):
        pyramid_request.es = sentinel.es
        pyramid_request.registry.settings["h.es_sync_job_limit"] = 10
        return pyramid_request


@pytest.fixture(autouse=True)
def BatchIndexer(patch):
    return patch("h.services.search_index.service_factory.BatchIndexer")


@pytest.fixture(autouse=True)
def Queue(patch):
    return patch("h.services.search_index.service_factory.Queue")


@pytest.fixture(autouse=True)
def SearchIndexService(patch):
    return patch("h.services.search_index.service_factory.SearchIndexService")
