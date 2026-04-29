from prometheus_client import Histogram

DOCUMENT_SEARCH_DURATION = Histogram(
    "document_search_duration_seconds",
    "Tempo de execucao do caso de uso de busca de documentos.",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)