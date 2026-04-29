from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from src.api.dependencies import get_create_document_handler, get_search_documents_handler
from src.api.dtos.requests import CreateDocumentRequest
from src.api.dtos.responses import (
    DocumentCreateSuccessResponse,
    DocumentResponse,
    DocumentSearchSuccessResponse,
)
from src.api.mappers.document_mapper import (
    to_document_response_from_domain,
    to_document_response_from_read_model,
)
from src.application.use_cases.create_document.command import CreateDocumentCommand
from src.application.use_cases.create_document.handler import CreateDocumentHandler
from src.application.use_cases.search_documents.handler import SearchDocumentsHandler
from src.application.use_cases.search_documents.query import SearchDocumentsQuery
from src.shared.request_context import request_id_ctx

router = APIRouter()


@router.post(
    "",
    response_model=DocumentCreateSuccessResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    request: CreateDocumentRequest,
    handler: CreateDocumentHandler = Depends(get_create_document_handler),
) -> DocumentCreateSuccessResponse:
    command = CreateDocumentCommand(
        titulo=request.titulo,
        autor=request.autor,
        conteudo=request.conteudo,
        data=request.data,
        latitude=request.latitude,
        longitude=request.longitude,
    )
    created = handler.execute(command)
    return DocumentCreateSuccessResponse(
        success=True,
        message="Documento criado com sucesso.",
        data=to_document_response_from_domain(created),
        trace_id=request_id_ctx.get(),
    )


@router.get(
    "",
    response_model=DocumentSearchSuccessResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def search_documents(
    palavra_chave: Annotated[str | None, Query(alias="palavraChave", min_length=1)] = None,
    busca: Annotated[str | None, Query(min_length=1)] = None,
    latitude: Annotated[float | None, Query(ge=-90.0, le=90.0)] = None,
    longitude: Annotated[float | None, Query(ge=-180.0, le=180.0)] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    handler: SearchDocumentsHandler = Depends(get_search_documents_handler),
) -> DocumentSearchSuccessResponse:
    query = SearchDocumentsQuery(
        palavra_chave=palavra_chave,
        busca=busca,
        latitude=latitude,
        longitude=longitude,
        limit=limit,
    )
    documents = handler.execute(query)
    return DocumentSearchSuccessResponse(
        success=True,
        message="Busca realizada com sucesso.",
        data=[to_document_response_from_read_model(item) for item in documents],
        trace_id=request_id_ctx.get(),
    )
